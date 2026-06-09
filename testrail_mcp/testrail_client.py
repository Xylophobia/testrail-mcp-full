"""TestRail API client module."""
import base64
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import requests

class TestRailClient:
    """TestRail API client for interacting with TestRail."""

    def __init__(self, base_url: str, username: str, api_key: str):
        """
        Initialize the TestRail API client.
        
        Args:
            base_url: The URL of your TestRail instance (e.g., [https://example.testrail.io/)](https://example.testrail.io/))
            username: Your TestRail username/email
            api_key: Your TestRail API key
        """
        self.username = username
        self.api_key = api_key
        
        # Ensure the base URL ends with a slash
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url + 'index.php?/api/v2/'
        
        # Set up the session with authentication
        self.session = requests.Session()
        auth = str(
            base64.b64encode(
                bytes(f'{username}:{api_key}', 'utf-8')
            ),
            'ascii'
        ).strip()
        self.session.headers.update({
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/json',
        })

    def _append_query_params(self, uri: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Append query parameters to an API URI."""
        if not params:
            return uri

        normalized_params: Dict[str, Union[str, int]] = {}
        for key, value in params.items():
            if value is None:
                continue
            if isinstance(value, bool):
                normalized_params[key] = int(value)
            elif isinstance(value, list):
                normalized_params[key] = ','.join(str(item) for item in value)
            else:
                normalized_params[key] = value

        if not normalized_params:
            return uri

        return f"{uri}&{urlencode(normalized_params)}"

    def _send_request(
        self,
        method: str,
        uri: str,
        data: Optional[Union[Dict, List]] = None,
        files: Optional[Dict[str, Any]] = None,
        expect_json: bool = True,
    ) -> Any:
        """
        Send a request to the TestRail API.

        Args:
            method: HTTP method (GET, POST, etc.)
            uri: API endpoint URI
            data: Request data for POST/PUT requests
            files: Multipart files payload for upload endpoints
            expect_json: Whether to decode the response as JSON

        Returns:
            Response data from TestRail

        Raises:
            Exception: If the request fails
        """
        url = self.base_url + uri
        method = method.upper()

        if method == 'GET':
            response = self.session.get(url)
        elif method == 'POST':
            if files:
                headers = dict(self.session.headers)
                headers.pop('Content-Type', None)
                response = self.session.post(url, data=data, files=files, headers=headers)
            else:
                response = self.session.post(url, data=json.dumps(data) if data is not None else None)
        elif method == 'PUT':
            response = self.session.put(url, data=json.dumps(data) if data is not None else None)
        elif method == 'DELETE':
            response = self.session.delete(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if response.status_code >= 300:
            try:
                error = response.json()
            except Exception:
                error = response.text
            raise Exception(f"TestRail API returned HTTP {response.status_code}: {error}")

        if not expect_json:
            return response

        return response.json() if response.content else {}

    def _upload_attachment(self, uri: str, file_path: str) -> Dict[str, Any]:
        """Upload an attachment using multipart/form-data."""
        path = Path(file_path)
        with path.open('rb') as handle:
            files = {'attachment': (path.name, handle)}
            return self._send_request('POST', uri, files=files)

    # Cases API
    def get_case(self, case_id: int) -> Dict:
        """Get a test case by ID."""
        return self._send_request('GET', f'get_case/{case_id}')
    
    def get_cases(self, project_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get test cases for a project or suite."""
        uri = self._append_query_params(f'get_cases/{project_id}', filters)
        return self._send_request('GET', uri)

    def get_history_for_case(self, case_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get edit history for a case."""
        uri = self._append_query_params(f'get_history_for_case/{case_id}', filters)
        return self._send_request('GET', uri)
    
    def add_case(self, section_id: int, data: Dict) -> Dict:
        """Add a new test case."""
        return self._send_request('POST', f'add_case/{section_id}', data)
    
    def update_case(self, case_id: int, data: Dict) -> Dict:
        """Update an existing test case."""
        return self._send_request('POST', f'update_case/{case_id}', data)

    def update_cases(self, suite_id: int, data: Dict) -> Dict:
        """Bulk update multiple test cases."""
        return self._send_request('POST', f'update_cases/{suite_id}', data)
    
    def delete_case(self, case_id: int) -> Dict:
        """Delete a test case."""
        return self._send_request('POST', f'delete_case/{case_id}')

    def copy_cases_to_section(self, section_id: int, data: Dict) -> Dict:
        """Copy cases to another section."""
        return self._send_request('POST', f'copy_cases_to_section/{section_id}', data)

    def move_cases_to_section(self, section_id: int, data: Dict) -> Dict:
        """Move cases to another section."""
        return self._send_request('POST', f'move_cases_to_section/{section_id}', data)
    
    # Projects API
    def get_project(self, project_id: int) -> Dict:
        """Get a project by ID."""
        return self._send_request('GET', f'get_project/{project_id}')
    
    def get_projects(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get projects."""
        uri = self._append_query_params('get_projects', filters)
        return self._send_request('GET', uri)
    
    def add_project(self, data: Dict) -> Dict:
        """Add a new project."""
        return self._send_request('POST', 'add_project', data)
    
    def update_project(self, project_id: int, data: Dict) -> Dict:
        """Update an existing project."""
        return self._send_request('POST', f'update_project/{project_id}', data)
    
    def delete_project(self, project_id: int) -> Dict:
        """Delete a project."""
        return self._send_request('POST', f'delete_project/{project_id}')

    # Milestones API
    def get_milestone(self, milestone_id: int) -> Dict:
        """Get a milestone by ID."""
        return self._send_request('GET', f'get_milestone/{milestone_id}')

    def get_milestones(self, project_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get milestones for a project."""
        uri = self._append_query_params(f'get_milestones/{project_id}', filters)
        return self._send_request('GET', uri)

    def add_milestone(self, project_id: int, data: Dict) -> Dict:
        """Add a milestone."""
        return self._send_request('POST', f'add_milestone/{project_id}', data)

    def update_milestone(self, milestone_id: int, data: Dict) -> Dict:
        """Update a milestone."""
        return self._send_request('POST', f'update_milestone/{milestone_id}', data)

    def delete_milestone(self, milestone_id: int) -> Dict:
        """Delete a milestone."""
        return self._send_request('POST', f'delete_milestone/{milestone_id}')

    # Suites API
    def get_suite(self, suite_id: int) -> Dict:
        """Get a suite by ID."""
        return self._send_request('GET', f'get_suite/{suite_id}')

    def get_suites(self, project_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get suites for a project."""
        uri = self._append_query_params(f'get_suites/{project_id}', filters)
        return self._send_request('GET', uri)

    def add_suite(self, project_id: int, data: Dict) -> Dict:
        """Add a suite."""
        return self._send_request('POST', f'add_suite/{project_id}', data)

    def update_suite(self, suite_id: int, data: Dict) -> Dict:
        """Update a suite."""
        return self._send_request('POST', f'update_suite/{suite_id}', data)

    def delete_suite(self, suite_id: int, soft: Optional[bool] = None) -> Dict:
        """Delete a suite."""
        uri = self._append_query_params(f'delete_suite/{suite_id}', {'soft': soft})
        return self._send_request('POST', uri)
    
    # Plans API
    def get_plan(self, plan_id: int) -> Dict:
        """Get a test plan by ID."""
        return self._send_request('GET', f'get_plan/{plan_id}')

    def get_plans(self, project_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get all test plans for a project."""
        uri = self._append_query_params(f'get_plans/{project_id}', filters)
        return self._send_request('GET', uri)

    def add_plan(self, project_id: int, data: Dict) -> Dict:
        """Add a new test plan."""
        return self._send_request('POST', f'add_plan/{project_id}', data)

    def add_plan_entry(self, plan_id: int, data: Dict) -> Dict:
        """Add one or more test runs to an existing test plan."""
        return self._send_request('POST', f'add_plan_entry/{plan_id}', data)

    def add_run_to_plan_entry(self, plan_id: int, entry_id: str, data: Dict) -> Dict:
        """Add a run to an existing test plan entry."""
        return self._send_request('POST', f'add_run_to_plan_entry/{plan_id}/{entry_id}', data)

    def update_plan(self, plan_id: int, data: Dict) -> Dict:
        """Update an existing test plan."""
        return self._send_request('POST', f'update_plan/{plan_id}', data)

    def update_plan_entry(self, plan_id: int, entry_id: str, data: Dict) -> Dict:
        """Update an existing test plan entry."""
        return self._send_request('POST', f'update_plan_entry/{plan_id}/{entry_id}', data)

    def update_run_in_plan_entry(self, run_id: int, data: Dict) -> Dict:
        """Update a run within a test plan entry."""
        return self._send_request('POST', f'update_run_in_plan_entry/{run_id}', data)

    def close_plan(self, plan_id: int) -> Dict:
        """Close an existing test plan."""
        return self._send_request('POST', f'close_plan/{plan_id}')

    def delete_plan(self, plan_id: int) -> Dict:
        """Delete an existing test plan."""
        return self._send_request('POST', f'delete_plan/{plan_id}')

    def delete_plan_entry(self, plan_id: int, entry_id: str) -> Dict:
        """Delete a test plan entry."""
        return self._send_request('POST', f'delete_plan_entry/{plan_id}/{entry_id}')

    def delete_run_from_plan_entry(self, run_id: int) -> Dict:
        """Delete a run from a test plan entry."""
        return self._send_request('POST', f'delete_run_from_plan_entry/{run_id}')

    # Runs API
    def get_run(self, run_id: int) -> Dict:
        """Get a test run by ID."""
        return self._send_request('GET', f'get_run/{run_id}')
    
    def get_runs(self, project_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get test runs for a project."""
        uri = self._append_query_params(f'get_runs/{project_id}', filters)
        return self._send_request('GET', uri)
    
    def add_run(self, project_id: int, data: Dict) -> Dict:
        """Add a new test run."""
        return self._send_request('POST', f'add_run/{project_id}', data)
    
    def update_run(self, run_id: int, data: Dict) -> Dict:
        """Update an existing test run."""
        return self._send_request('POST', f'update_run/{run_id}', data)
    
    def close_run(self, run_id: int) -> Dict:
        """Close a test run."""
        return self._send_request('POST', f'close_run/{run_id}')
    
    def delete_run(self, run_id: int, soft: Optional[bool] = None) -> Dict:
        """Delete a test run."""
        uri = self._append_query_params(f'delete_run/{run_id}', {'soft': soft})
        return self._send_request('POST', uri)
    
    # Results API
    def get_results(self, test_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get all results for a test."""
        uri = self._append_query_params(f'get_results/{test_id}', filters)
        return self._send_request('GET', uri)

    def get_results_for_case(self, run_id: int, case_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get all results for a test run and case combination."""
        uri = self._append_query_params(f'get_results_for_case/{run_id}/{case_id}', filters)
        return self._send_request('GET', uri)

    def get_results_for_run(self, run_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get all results for a run."""
        uri = self._append_query_params(f'get_results_for_run/{run_id}', filters)
        return self._send_request('GET', uri)
    
    def add_result(self, test_id: int, data: Dict) -> Dict:
        """Add a new result for a test."""
        return self._send_request('POST', f'add_result/{test_id}', data)

    def add_result_for_case(self, run_id: int, case_id: int, data: Dict) -> Dict:
        """Add a new result for a run and case combination."""
        return self._send_request('POST', f'add_result_for_case/{run_id}/{case_id}', data)
    
    def add_results(self, run_id: int, data: Dict) -> Dict[str, Any]:
        """Add multiple results for a run."""
        return self._send_request('POST', f'add_results/{run_id}', data)
    
    def add_results_for_cases(self, run_id: int, data: Dict) -> Dict[str, Any]:
        """Add results for specific cases in a run."""
        return self._send_request('POST', f'add_results_for_cases/{run_id}', data)

    # Tests API
    def get_test(self, test_id: int, with_data: Optional[str] = None) -> Dict:
        """Get a test by ID."""
        uri = self._append_query_params(f'get_test/{test_id}', {'with_data': with_data})
        return self._send_request('GET', uri)

    def get_tests(self, run_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get all tests for a run."""
        uri = self._append_query_params(f'get_tests/{run_id}', filters)
        return self._send_request('GET', uri)

    def update_test(self, test_id: int, data: Dict) -> Dict:
        """Update an existing test."""
        return self._send_request('POST', f'update_test/{test_id}', data)

    def update_tests(self, data: Dict) -> Dict:
        """Bulk update multiple tests."""
        return self._send_request('POST', 'update_tests', data)
    
    # Datasets API
    def get_datasets(self, project_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get datasets for a project."""
        uri = self._append_query_params(f'get_datasets/{project_id}', filters)
        return self._send_request('GET', uri)
    
    def get_dataset(self, dataset_id: int) -> Dict:
        """Get a dataset by ID."""
        return self._send_request('GET', f'get_dataset/{dataset_id}')
    
    def add_dataset(self, project_id: int, data: Dict) -> Dict:
        """Add a new dataset."""
        return self._send_request('POST', f'add_dataset/{project_id}', data)
    
    def update_dataset(self, dataset_id: int, data: Dict) -> Dict:
        """Update an existing dataset."""
        return self._send_request('POST', f'update_dataset/{dataset_id}', data)
    
    def delete_dataset(self, dataset_id: int) -> Dict:
        """Delete a dataset."""
        return self._send_request('POST', f'delete_dataset/{dataset_id}')

    # Variables API
    def get_variables(self, project_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get variables for a project."""
        uri = self._append_query_params(f'get_variables/{project_id}', filters)
        return self._send_request('GET', uri)

    def add_variable(self, project_id: int, data: Dict) -> Dict:
        """Add a variable."""
        return self._send_request('POST', f'add_variable/{project_id}', data)

    def update_variable(self, variable_id: int, data: Dict) -> Dict:
        """Update a variable."""
        return self._send_request('POST', f'update_variable/{variable_id}', data)

    def delete_variable(self, variable_id: int) -> Dict:
        """Delete a variable."""
        return self._send_request('POST', f'delete_variable/{variable_id}')

    # Sections API
    def get_section(self, section_id:int) -> Dict:
        """Get a specific section"""
        return self._send_request('GET', f'get_section/{section_id}')

    def get_sections(
        self,
        project_id: int,
        suite_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get sections for a project and optional suite."""
        query_params = dict(filters or {})
        if suite_id is not None:
            query_params['suite_id'] = suite_id
        uri = self._append_query_params(f'get_sections/{project_id}', query_params)
        return self._send_request('GET', uri)

    def add_section(self, project_id:int, data:Dict) -> Dict:
        """Add a new section"""
        return self._send_request('POST', f'add_section/{project_id}', data)

    def update_section(self, section_id:int, data:Dict) -> Dict:
        """Update an existing section"""
        return self._send_request('POST', f'update_section/{section_id}', data)

    def delete_section(self, section_id: int, soft: Optional[bool] = None) -> Dict:
        """Delete an existing section"""
        uri = self._append_query_params(f'delete_section/{section_id}', {'soft': soft})
        return self._send_request('POST', uri)

    def move_section(self, section_id:int, data: Dict) -> Dict:
        """Move a section to a different parent or position"""
        return self._send_request('POST', f'move_section/{section_id}', data)

    # Metadata / lookup APIs
    def get_templates(self, project_id: int) -> List[Dict]:
        """Get templates for a project."""
        return self._send_request('GET', f'get_templates/{project_id}')

    def get_case_fields(self) -> List[Dict]:
        """Get custom case fields."""
        return self._send_request('GET', 'get_case_fields')

    def get_result_fields(self) -> List[Dict]:
        """Get custom result fields."""
        return self._send_request('GET', 'get_result_fields')

    def get_case_types(self) -> List[Dict]:
        """Get case types."""
        return self._send_request('GET', 'get_case_types')

    def get_priorities(self) -> List[Dict]:
        """Get priorities."""
        return self._send_request('GET', 'get_priorities')

    def get_statuses(self) -> List[Dict]:
        """Get test statuses."""
        return self._send_request('GET', 'get_statuses')

    def get_case_statuses(self) -> List[Dict]:
        """Get case statuses."""
        return self._send_request('GET', 'get_case_statuses')

    def get_dynamic_filter_fields(self, project_id: int) -> List[Dict]:
        """Get dynamic filter fields for a project."""
        return self._send_request('GET', f'get_dynamic_filter_fields/{project_id}')

    # Labels API
    def get_label(self, label_id: int) -> Dict:
        """Get a label by ID."""
        return self._send_request('GET', f'get_label/{label_id}')

    def get_labels(self, project_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get labels for a project."""
        uri = self._append_query_params(f'get_labels/{project_id}', filters)
        return self._send_request('GET', uri)

    def update_label(self, label_id: int, data: Dict) -> Dict:
        """Update a label."""
        return self._send_request('POST', f'update_label/{label_id}', data)

    # Users API
    def get_user(self, user_id: int) -> Dict:
        """Get a user by ID."""
        return self._send_request('GET', f'get_user/{user_id}')

    def get_current_user(self, user_id: int) -> Dict:
        """Get the current API user details."""
        return self._send_request('GET', f'get_current_user/{user_id}')

    def get_user_by_email(self, email: str) -> Dict:
        """Get a user by email."""
        return self._send_request('GET', self._append_query_params('get_user_by_email', {'email': email}))

    def get_users(self, project_id: Optional[int] = None) -> List[Dict]:
        """Get users, optionally scoped to a project."""
        uri = 'get_users' if project_id is None else f'get_users/{project_id}'
        return self._send_request('GET', uri)

    def add_user(self, data: Dict) -> Dict:
        """Add a user."""
        return self._send_request('POST', 'add_user', data)

    def update_user(self, user_id: int, data: Dict) -> Dict:
        """Update a user."""
        return self._send_request('POST', f'update_user/{user_id}', data)

    # Configurations API
    def get_configs(self, project_id: int) -> List[Dict]:
        """Get configurations for a project."""
        return self._send_request('GET', f'get_configs/{project_id}')

    def add_config_group(self, project_id: int, data: Dict) -> Dict:
        """Add a configuration group."""
        return self._send_request('POST', f'add_config_group/{project_id}', data)

    def add_config(self, config_group_id: int, data: Dict) -> Dict:
        """Add a configuration."""
        return self._send_request('POST', f'add_config/{config_group_id}', data)

    def update_config_group(self, config_group_id: int, data: Dict) -> Dict:
        """Update a configuration group."""
        return self._send_request('POST', f'update_config_group/{config_group_id}', data)

    def update_config(self, config_id: int, data: Dict) -> Dict:
        """Update a configuration."""
        return self._send_request('POST', f'update_config/{config_id}', data)

    def delete_config_group(self, config_group_id: int) -> Dict:
        """Delete a configuration group."""
        return self._send_request('POST', f'delete_config_group/{config_group_id}')

    def delete_config(self, config_id: int) -> Dict:
        """Delete a configuration."""
        return self._send_request('POST', f'delete_config/{config_id}')

    # Shared steps API
    def get_shared_step(self, shared_step_id: int) -> Dict:
        """Get a shared step by ID."""
        return self._send_request('GET', f'get_shared_step/{shared_step_id}')

    def get_shared_step_history(self, shared_step_id: int) -> Dict[str, Any]:
        """Get shared step history."""
        return self._send_request('GET', f'get_shared_step_history/{shared_step_id}')

    def get_shared_steps(self, project_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get shared steps for a project."""
        uri = self._append_query_params(f'get_shared_steps/{project_id}', filters)
        return self._send_request('GET', uri)

    def add_shared_step(self, project_id: int, data: Dict) -> Dict:
        """Add a shared step."""
        return self._send_request('POST', f'add_shared_step/{project_id}', data)

    def update_shared_step(self, shared_step_id: int, data: Dict) -> Dict:
        """Update a shared step."""
        return self._send_request('POST', f'update_shared_step/{shared_step_id}', data)

    def delete_shared_step(self, shared_step_id: int, data: Optional[Dict] = None) -> Dict:
        """Delete a shared step."""
        return self._send_request('POST', f'delete_shared_step/{shared_step_id}', data)

    # Attachments API
    def add_attachment_to_case(self, case_id: int, file_path: str) -> Dict[str, Any]:
        """Add an attachment to a case."""
        return self._upload_attachment(f'add_attachment_to_case/{case_id}', file_path)

    def add_attachment_to_plan(self, plan_id: int, file_path: str) -> Dict[str, Any]:
        """Add an attachment to a plan."""
        return self._upload_attachment(f'add_attachment_to_plan/{plan_id}', file_path)

    def add_attachment_to_plan_entry(self, plan_id: int, entry_id: str, file_path: str) -> Dict[str, Any]:
        """Add an attachment to a plan entry."""
        return self._upload_attachment(f'add_attachment_to_plan_entry/{plan_id}/{entry_id}', file_path)

    def add_attachment_to_result(self, result_id: int, file_path: str) -> Dict[str, Any]:
        """Add an attachment to a result."""
        return self._upload_attachment(f'add_attachment_to_result/{result_id}', file_path)

    def add_attachment_to_run(self, run_id: int, file_path: str) -> Dict[str, Any]:
        """Add an attachment to a run."""
        return self._upload_attachment(f'add_attachment_to_run/{run_id}', file_path)

    def get_attachments_for_case(self, case_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get attachments for a case."""
        uri = self._append_query_params(f'get_attachments_for_case/{case_id}', filters)
        return self._send_request('GET', uri)

    def get_attachments_for_plan(self, plan_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get attachments for a plan."""
        uri = self._append_query_params(f'get_attachments_for_plan/{plan_id}', filters)
        return self._send_request('GET', uri)

    def get_attachments_for_plan_entry(self, plan_id: int, entry_id: str) -> List[Dict]:
        """Get attachments for a plan entry."""
        return self._send_request('GET', f'get_attachments_for_plan_entry/{plan_id}/{entry_id}')

    def get_attachments_for_run(self, run_id: int, filters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Get attachments for a run."""
        uri = self._append_query_params(f'get_attachments_for_run/{run_id}', filters)
        return self._send_request('GET', uri)

    def get_attachments_for_test(self, test_id: int) -> List[Dict]:
        """Get attachments for a test."""
        return self._send_request('GET', f'get_attachments_for_test/{test_id}')

    def get_attachment(self, attachment_id: Union[int, str]) -> Dict[str, Any]:
        """Retrieve an attachment body and encode it for MCP transport."""
        response = self._send_request('GET', f'get_attachment/{attachment_id}', expect_json=False)
        return {
            'attachment_id': attachment_id,
            'content_type': response.headers.get('Content-Type'),
            'content_disposition': response.headers.get('Content-Disposition'),
            'size': len(response.content),
            'content_base64': base64.b64encode(response.content).decode('ascii'),
        }

    def delete_attachment(self, attachment_id: Union[int, str]) -> Dict:
        """Delete an attachment."""
        return self._send_request('POST', f'delete_attachment/{attachment_id}')

    # Reports API
    def get_reports(self, project_id: int) -> List[Dict]:
        """Get API-accessible reports for a project."""
        return self._send_request('GET', f'get_reports/{project_id}')

    def run_report(self, report_template_id: int) -> Dict:
        """Run a single-project report."""
        return self._send_request('GET', f'run_report/{report_template_id}')

    def get_cross_project_reports(self) -> List[Dict]:
        """Get API-accessible cross-project reports."""
        return self._send_request('GET', 'get_cross_project_reports')

    def run_cross_project_report(self, report_template_id: int) -> Dict:
        """Run a cross-project report."""
        return self._send_request('GET', f'run_cross_project_report/{report_template_id}')
