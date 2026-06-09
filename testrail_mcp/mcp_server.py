"""MCP server implementation for TestRail."""
from typing import Dict, List, Any, Optional, Union
from fastmcp import FastMCP

from testrail_mcp.testrail_client import TestRailClient
from testrail_mcp.config import TESTRAIL_URL, TESTRAIL_USERNAME, TESTRAIL_API_KEY


class TestRailMCPServer(FastMCP):
    """MCP server for TestRail integration using FastMCP."""
    
    def __init__(self):
        """Initialize the TestRail MCP server."""
        super().__init__(name="TestRail MCP Server", version="0.1.3")
        self.client = TestRailClient(TESTRAIL_URL, TESTRAIL_USERNAME, TESTRAIL_API_KEY)
        self._register_tools()
        self._register_resources()
    
    def _register_tools(self):
        """Register all TestRail tools with the MCP server."""
        # Project tools
        @self.tool("get_project", description="Get a project by ID")
        def get_project(project_id: int) -> Dict:
            """Get a project by ID."""
            return self.client.get_project(project_id)
        
        @self.tool("get_projects", description="Get projects")
        def get_projects(
            is_completed: Optional[bool] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
        ) -> Dict[str, Any]:
            """Get all projects."""
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'is_completed', is_completed)
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            return self.client.get_projects(filters or None)
        
        @self.tool("add_project", description="Add a new project")
        def add_project(
            name: str,
            announcement: Optional[str] = None,
            show_announcement: Optional[bool] = None,
            suite_mode: Optional[int] = None
        ) -> Dict:
            """
            Add a new project.
            
            Args:
                name: The name of the project
                announcement: The announcement of the project (optional)
                show_announcement: Whether to show the announcement (optional)
                suite_mode: The suite mode: 1 for single suite mode, 2 for single suite + baselines, 3 for multiple suites (optional)
            """
            data = {'name': name}
            if announcement is not None:
                data['announcement'] = announcement
            if show_announcement is not None:
                data['show_announcement'] = show_announcement
            if suite_mode is not None:
                data['suite_mode'] = suite_mode
            return self.client.add_project(data)
        
        @self.tool("update_project", description="Update an existing project")
        def update_project(
            project_id: int,
            name: Optional[str] = None,
            announcement: Optional[str] = None,
            show_announcement: Optional[bool] = None,
            is_completed: Optional[bool] = None
        ) -> Dict:
            """
            Update an existing project.
            
            Args:
                project_id: The ID of the project
                name: The name of the project (optional)
                announcement: The announcement of the project (optional)
                show_announcement: Whether to show the announcement (optional)
                is_completed: Whether the project is completed (optional)
            """
            data = {}
            if name is not None:
                data['name'] = name
            if announcement is not None:
                data['announcement'] = announcement
            if show_announcement is not None:
                data['show_announcement'] = show_announcement
            if is_completed is not None:
                data['is_completed'] = is_completed
            return self.client.update_project(project_id, data)
        
        @self.tool("delete_project", description="Delete a project")
        def delete_project(project_id: int) -> Dict:
            """
            Delete a project.
            
            Args:
                project_id: The ID of the project
            """
            return self.client.delete_project(project_id)

        # Milestone tools
        @self.tool("get_milestone", description="Get a milestone by ID")
        def get_milestone(milestone_id: int) -> Dict:
            """Get a milestone by ID."""
            return self.client.get_milestone(milestone_id)

        @self.tool("get_milestones", description="Get milestones for a project")
        def get_milestones(
            project_id: int,
            is_completed: Optional[bool] = None,
            is_started: Optional[bool] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
        ) -> Dict[str, Any]:
            """Get milestones for a project."""
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'is_completed', is_completed)
            _set_if_present(filters, 'is_started', is_started)
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            return self.client.get_milestones(project_id, filters or None)

        @self.tool("add_milestone", description="Add a new milestone")
        def add_milestone(
            project_id: int,
            name: str,
            description: Optional[str] = None,
            due_on: Optional[int] = None,
            parent_id: Optional[int] = None,
            refs: Optional[str] = None,
            start_on: Optional[int] = None,
        ) -> Dict:
            """Add a new milestone."""
            data = {'name': name}
            _set_if_present(data, 'description', description)
            _set_if_present(data, 'due_on', due_on)
            _set_if_present(data, 'parent_id', parent_id)
            _set_if_present(data, 'refs', refs)
            _set_if_present(data, 'start_on', start_on)
            return self.client.add_milestone(project_id, data)

        @self.tool("update_milestone", description="Update an existing milestone")
        def update_milestone(
            milestone_id: int,
            name: Optional[str] = None,
            description: Optional[str] = None,
            due_on: Optional[int] = None,
            parent_id: Optional[int] = None,
            refs: Optional[str] = None,
            start_on: Optional[int] = None,
            is_completed: Optional[bool] = None,
            is_started: Optional[bool] = None,
        ) -> Dict:
            """Update an existing milestone."""
            data: Dict[str, Any] = {}
            _set_if_present(data, 'name', name)
            _set_if_present(data, 'description', description)
            _set_if_present(data, 'due_on', due_on)
            _set_if_present(data, 'parent_id', parent_id)
            _set_if_present(data, 'refs', refs)
            _set_if_present(data, 'start_on', start_on)
            _set_if_present(data, 'is_completed', is_completed)
            _set_if_present(data, 'is_started', is_started)
            return self.client.update_milestone(milestone_id, data)

        @self.tool("delete_milestone", description="Delete a milestone")
        def delete_milestone(milestone_id: int) -> Dict:
            """Delete a milestone."""
            return self.client.delete_milestone(milestone_id)
        
        def _set_if_present(data: Dict[str, Any], key: str, value: Any) -> None:
            """Store optional fields without sending nulls to TestRail."""
            if value is not None:
                data[key] = value

        def _merge_payload(base: Optional[Dict[str, Any]] = None, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            """Merge explicit MCP arguments with an optional raw payload override."""
            payload = dict(base or {})
            payload.update(extra or {})
            return payload

        # Plan tools
        @self.tool("get_plan", description="Get a test plan by ID")
        def get_plan(plan_id: int) -> Dict:
            """
            Get a test plan by ID.

            Args:
                plan_id: The ID of the test plan
            """
            return self.client.get_plan(plan_id)

        @self.tool("get_plans", description="Get all test plans for a project")
        def get_plans(
            project_id: int,
            created_after: Optional[int] = None,
            created_before: Optional[int] = None,
            created_by: Optional[List[int]] = None,
            is_completed: Optional[bool] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            milestone_id: Optional[List[int]] = None,
            refs: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Get all test plans for a project.

            Args:
                project_id: The ID of the project
                created_after: Only return plans created after this UNIX timestamp
                created_before: Only return plans created before this UNIX timestamp
                created_by: Filter by one or more creator user IDs
                is_completed: Filter active (`False`) vs completed (`True`) plans
                limit: Maximum number of plans to return
                offset: Number of plans to skip for pagination
                milestone_id: Filter by one or more milestone IDs
                refs: Filter by an external reference ID
            """
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'created_after', created_after)
            _set_if_present(filters, 'created_before', created_before)
            _set_if_present(filters, 'created_by', created_by)
            _set_if_present(filters, 'is_completed', is_completed)
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            _set_if_present(filters, 'milestone_id', milestone_id)
            _set_if_present(filters, 'refs', refs)
            return self.client.get_plans(project_id, filters or None)

        @self.tool("add_plan", description="Add a new test plan")
        def add_plan(
            project_id: int,
            name: str,
            description: Optional[str] = None,
            milestone_id: Optional[int] = None,
            start_on: Optional[int] = None,
            due_on: Optional[int] = None,
            entries: Optional[List[Dict[str, Any]]] = None,
            refs: Optional[str] = None,
            dynamic_filters: Optional[Dict[str, Any]] = None,
        ) -> Dict:
            """
            Add a new test plan.

            Args:
                project_id: The ID of the project
                name: The name of the test plan
                description: The description of the test plan
                milestone_id: The milestone to link to the test plan
                start_on: The start date as a UNIX timestamp
                due_on: The due date as a UNIX timestamp
                entries: Optional list of plan entry payloads
            """
            data = {'name': name}
            _set_if_present(data, 'description', description)
            _set_if_present(data, 'milestone_id', milestone_id)
            _set_if_present(data, 'start_on', start_on)
            _set_if_present(data, 'due_on', due_on)
            _set_if_present(data, 'entries', entries)
            _set_if_present(data, 'refs', refs)
            _set_if_present(data, 'dynamic_filters', dynamic_filters)
            return self.client.add_plan(project_id, data)

        @self.tool("add_plan_entry", description="Add one or more test runs to a test plan")
        def add_plan_entry(
            plan_id: int,
            suite_id: Optional[int] = None,
            name: Optional[str] = None,
            description: Optional[str] = None,
            assignedto_id: Optional[int] = None,
            start_on: Optional[int] = None,
            due_on: Optional[int] = None,
            include_all: Optional[bool] = None,
            case_ids: Optional[List[int]] = None,
            config_ids: Optional[List[int]] = None,
            refs: Optional[str] = None,
            runs: Optional[List[Dict[str, Any]]] = None,
        ) -> Dict:
            """
            Add one or more test runs to a plan.

            Args:
                plan_id: The ID of the test plan
                suite_id: The test suite ID for the plan entry
                name: The display name for the generated run group
                description: The description of the plan entry
                assignedto_id: Default assignee for generated runs
                start_on: The start date as a UNIX timestamp
                due_on: The due date as a UNIX timestamp
                include_all: Whether to include all cases by default
                case_ids: Custom case selection when `include_all` is `False`
                config_ids: Configuration IDs used by the plan entry
                refs: External reference IDs
                runs: Optional list of per-run overrides for configuration-based entries
            """
            data: Dict[str, Any] = {}
            _set_if_present(data, 'suite_id', suite_id)
            _set_if_present(data, 'name', name)
            _set_if_present(data, 'description', description)
            _set_if_present(data, 'assignedto_id', assignedto_id)
            _set_if_present(data, 'start_on', start_on)
            _set_if_present(data, 'due_on', due_on)
            _set_if_present(data, 'include_all', include_all)
            _set_if_present(data, 'case_ids', case_ids)
            _set_if_present(data, 'config_ids', config_ids)
            _set_if_present(data, 'refs', refs)
            _set_if_present(data, 'runs', runs)
            return self.client.add_plan_entry(plan_id, data)

        @self.tool("add_run_to_plan_entry", description="Add a run to an existing plan entry")
        def add_run_to_plan_entry(
            plan_id: int,
            entry_id: str,
            config_ids: List[int],
            description: Optional[str] = None,
            assignedto_id: Optional[int] = None,
            start_on: Optional[int] = None,
            due_on: Optional[int] = None,
            include_all: Optional[bool] = None,
            case_ids: Optional[List[int]] = None,
            refs: Optional[str] = None,
        ) -> Dict:
            """
            Add a run to a configuration-based plan entry.

            Args:
                plan_id: The ID of the test plan
                entry_id: The ID of the test plan entry
                config_ids: Configuration IDs used by the new run
                description: The description of the run
                assignedto_id: The user ID to assign the run to
                start_on: The start date as a UNIX timestamp
                due_on: The due date as a UNIX timestamp
                include_all: Whether to include all cases in the run
                case_ids: Custom case selection when `include_all` is `False`
                refs: External reference IDs
            """
            data: Dict[str, Any] = {'config_ids': config_ids}
            _set_if_present(data, 'description', description)
            _set_if_present(data, 'assignedto_id', assignedto_id)
            _set_if_present(data, 'start_on', start_on)
            _set_if_present(data, 'due_on', due_on)
            _set_if_present(data, 'include_all', include_all)
            _set_if_present(data, 'case_ids', case_ids)
            _set_if_present(data, 'refs', refs)
            return self.client.add_run_to_plan_entry(plan_id, entry_id, data)

        @self.tool("update_plan", description="Update an existing test plan")
        def update_plan(
            plan_id: int,
            name: Optional[str] = None,
            description: Optional[str] = None,
            milestone_id: Optional[int] = None,
            start_on: Optional[int] = None,
            due_on: Optional[int] = None,
            refs: Optional[str] = None,
            dynamic_filters: Optional[Dict[str, Any]] = None,
        ) -> Dict:
            """
            Update an existing test plan.

            Args:
                plan_id: The ID of the test plan
                name: The name of the test plan
                description: The description of the test plan
                milestone_id: The milestone to link to the test plan
                start_on: The start date as a UNIX timestamp
                due_on: The due date as a UNIX timestamp
            """
            data: Dict[str, Any] = {}
            _set_if_present(data, 'name', name)
            _set_if_present(data, 'description', description)
            _set_if_present(data, 'milestone_id', milestone_id)
            _set_if_present(data, 'start_on', start_on)
            _set_if_present(data, 'due_on', due_on)
            _set_if_present(data, 'refs', refs)
            _set_if_present(data, 'dynamic_filters', dynamic_filters)
            return self.client.update_plan(plan_id, data)

        @self.tool("update_plan_entry", description="Update an existing test plan entry")
        def update_plan_entry(
            plan_id: int,
            entry_id: str,
            name: Optional[str] = None,
            description: Optional[str] = None,
            assignedto_id: Optional[int] = None,
            start_on: Optional[int] = None,
            due_on: Optional[int] = None,
            include_all: Optional[bool] = None,
            case_ids: Optional[List[int]] = None,
            refs: Optional[str] = None,
        ) -> Dict:
            """
            Update an existing plan entry.

            Args:
                plan_id: The ID of the test plan
                entry_id: The ID of the test plan entry
                name: The name of the entry
                description: The description of the entry
                assignedto_id: The user ID to assign the entry to
                start_on: The start date as a UNIX timestamp
                due_on: The due date as a UNIX timestamp
                include_all: Whether the entry includes all cases
                case_ids: Custom case selection when `include_all` is `False`
                refs: External reference IDs
            """
            data: Dict[str, Any] = {}
            _set_if_present(data, 'name', name)
            _set_if_present(data, 'description', description)
            _set_if_present(data, 'assignedto_id', assignedto_id)
            _set_if_present(data, 'start_on', start_on)
            _set_if_present(data, 'due_on', due_on)
            _set_if_present(data, 'include_all', include_all)
            _set_if_present(data, 'case_ids', case_ids)
            _set_if_present(data, 'refs', refs)
            return self.client.update_plan_entry(plan_id, entry_id, data)

        @self.tool("update_run_in_plan_entry", description="Update a run inside a test plan entry")
        def update_run_in_plan_entry(
            run_id: int,
            description: Optional[str] = None,
            assignedto_id: Optional[int] = None,
            start_on: Optional[int] = None,
            due_on: Optional[int] = None,
            include_all: Optional[bool] = None,
            case_ids: Optional[List[int]] = None,
            refs: Optional[str] = None,
        ) -> Dict:
            """
            Update a run inside a configuration-based plan entry.

            Args:
                run_id: The ID of the test run
                description: The description of the run
                assignedto_id: The user ID to assign the run to
                start_on: The start date as a UNIX timestamp
                due_on: The due date as a UNIX timestamp
                include_all: Whether the run includes all cases
                case_ids: Custom case selection when `include_all` is `False`
                refs: External reference IDs
            """
            data: Dict[str, Any] = {}
            _set_if_present(data, 'description', description)
            _set_if_present(data, 'assignedto_id', assignedto_id)
            _set_if_present(data, 'start_on', start_on)
            _set_if_present(data, 'due_on', due_on)
            _set_if_present(data, 'include_all', include_all)
            _set_if_present(data, 'case_ids', case_ids)
            _set_if_present(data, 'refs', refs)
            return self.client.update_run_in_plan_entry(run_id, data)

        @self.tool("close_plan", description="Close an existing test plan")
        def close_plan(plan_id: int) -> Dict:
            """
            Close an existing test plan.

            Args:
                plan_id: The ID of the test plan
            """
            return self.client.close_plan(plan_id)

        @self.tool("delete_plan", description="Delete a test plan")
        def delete_plan(plan_id: int) -> Dict:
            """
            Delete an existing test plan.

            Args:
                plan_id: The ID of the test plan
            """
            return self.client.delete_plan(plan_id)

        @self.tool("delete_plan_entry", description="Delete a test plan entry")
        def delete_plan_entry(plan_id: int, entry_id: str) -> Dict:
            """
            Delete an existing test plan entry.

            Args:
                plan_id: The ID of the test plan
                entry_id: The ID of the test plan entry
            """
            return self.client.delete_plan_entry(plan_id, entry_id)

        @self.tool("delete_run_from_plan_entry", description="Delete a run from a test plan entry")
        def delete_run_from_plan_entry(run_id: int) -> Dict:
            """
            Delete a run from an existing plan entry.

            Args:
                run_id: The ID of the test run
            """
            return self.client.delete_run_from_plan_entry(run_id)
        
        # Case tools
        @self.tool("get_case", description="Get a test case by ID")
        def get_case(case_id: int) -> Dict:
            """
            Get a test case by ID.
            
            Args:
                case_id: The ID of the test case
            """
            return self.client.get_case(case_id)
        
        @self.tool("get_cases", description="Get test cases for a project or suite")
        def get_cases(
            project_id: int,
            suite_id: Optional[int] = None,
            created_after: Optional[int] = None,
            created_before: Optional[int] = None,
            created_by: Optional[List[int]] = None,
            filter: Optional[str] = None,
            limit: Optional[int] = None,
            milestone_id: Optional[List[int]] = None,
            offset: Optional[int] = None,
            priority_id: Optional[List[int]] = None,
            refs: Optional[str] = None,
            section_id: Optional[int] = None,
            template_id: Optional[List[int]] = None,
            type_id: Optional[List[int]] = None,
            updated_after: Optional[int] = None,
            updated_before: Optional[int] = None,
            updated_by: Optional[List[int]] = None,
            label_id: Optional[List[int]] = None,
        ) -> Dict[str, Any]:
            """
            Get test cases for a project or suite.
            
            Args:
                project_id: The ID of the project
                suite_id: The ID of the test suite (optional)
            """
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'suite_id', suite_id)
            _set_if_present(filters, 'created_after', created_after)
            _set_if_present(filters, 'created_before', created_before)
            _set_if_present(filters, 'created_by', created_by)
            _set_if_present(filters, 'filter', filter)
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'milestone_id', milestone_id)
            _set_if_present(filters, 'offset', offset)
            _set_if_present(filters, 'priority_id', priority_id)
            _set_if_present(filters, 'refs', refs)
            _set_if_present(filters, 'section_id', section_id)
            _set_if_present(filters, 'template_id', template_id)
            _set_if_present(filters, 'type_id', type_id)
            _set_if_present(filters, 'updated_after', updated_after)
            _set_if_present(filters, 'updated_before', updated_before)
            _set_if_present(filters, 'updated_by', updated_by)
            _set_if_present(filters, 'label_id', label_id)
            return self.client.get_cases(project_id, filters or None)

        @self.tool("get_history_for_case", description="Get edit history for a test case")
        def get_history_for_case(case_id: int, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict[str, Any]:
            """
            Get edit history for a test case.

            Args:
                case_id: The ID of the test case
                limit: Maximum number of history items to return
                offset: Number of history items to skip
            """
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            return self.client.get_history_for_case(case_id, filters or None)
        
        @self.tool("add_case", description="Add a new test case")
        def add_case(
            section_id: int,
            title: str,
            template_id: Optional[int] = None,
            type_id: Optional[int] = None,
            priority_id: Optional[int] = None,
            estimate: Optional[str] = None,
            milestone_id: Optional[int] = None,
            refs: Optional[str] = None,
            labels: Optional[List[Union[int, str]]] = None,
            custom_steps: Optional[str] = None,
            custom_expected: Optional[str] = None,
            custom_steps_separated: Optional[List[Dict[str, str]]] = None,
            steps_separated: Optional[List[Dict[str, str]]] = None
        ) -> Dict:
            """
            Add a new test case.
            
            Args:
                section_id: The ID of the section
                title: The title of the test case
                type_id: The ID of the case type (optional)
                priority_id: The ID of the priority (optional)
                estimate: The estimate, e.g. '30s' or '1m 45s' (optional)
                milestone_id: The ID of the milestone (optional)
                refs: A comma-separated list of references (optional)
                custom_steps: Steps as string
                custom_expected: case expected result
                custom_steps_separated: A list of test steps (optional), each with fields:
                    - content: The text contents of the "Step" field
                    - expected: The text contents of the "Expected Result" field
                    - additional_info: The text contents of the "Additional Info" field
                    - refs: Reference information for the "References" field
                steps_separated: A list of test steps (optional), each with fields:
                    - content: The text contents of the "Step" field
                    - expected: The text contents of the "Expected Result" field
                    - additional_info: The text contents of the "Additional Info" field
                    - refs: Reference information for the "References" field
            """
            data = {'title': title}
            if template_id is not None:
                data['template_id'] = template_id
            if type_id is not None:
                data['type_id'] = type_id
            if priority_id is not None:
                data['priority_id'] = priority_id
            if estimate is not None:
                data['estimate'] = estimate
            if milestone_id is not None:
                data['milestone_id'] = milestone_id
            if refs is not None:
                data['refs'] = refs
            if labels is not None:
                data['labels'] = labels
            if custom_steps_separated is not None:
                data['custom_steps_separated'] = custom_steps_separated
            if steps_separated is not None:
                data['steps_separated'] = steps_separated
            if custom_steps is not None:
                data['custom_steps'] = custom_steps
            if custom_expected is not None:
                data['custom_expected'] = custom_expected
            return self.client.add_case(section_id, data)
        
        @self.tool("update_case", description="Update an existing test case")
        def update_case(
            case_id: int,
            title: Optional[str] = None,
            section_id: Optional[int] = None,
            type_id: Optional[int] = None,
            priority_id: Optional[int] = None,
            estimate: Optional[str] = None,
            milestone_id: Optional[int] = None,
            refs: Optional[str] = None,
            template_id: Optional[int] = None,
            labels: Optional[List[Union[int, str]]] = None,
            custom_steps: Optional[str] = None,
            custom_expected: Optional[str] = None,
            custom_steps_separated: Optional[List[Dict[str, str]]] = None,
            steps_separated: Optional[List[Dict[str, str]]] = None
        ) -> Dict:
            """
            Update an existing test case.
            
            Args:
                case_id: The ID of the test case
                title: The title of the test case (optional)
                type_id: The ID of the case type (optional)
                priority_id: The ID of the priority (optional)
                estimate: The estimate, e.g. '30s' or '1m 45s' (optional)
                milestone_id: The ID of the milestone (optional)
                refs: A comma-separated list of references (optional)
                custom_expected: case expected result
                custom_steps_separated: A list of test steps (optional), each with fields:
                    - content: The text contents of the "Step" field
                    - expected: The text contents of the "Expected Result" field
                    - additional_info: The text contents of the "Additional Info" field
                    - refs: Reference information for the "References" field
                steps_separated: A list of test steps (optional), each with fields:
                    - content: The text contents of the "Step" field
                    - expected: The text contents of the "Expected Result" field
                    - additional_info: The text contents of the "Additional Info" field
                    - refs: Reference information for the "References" field
            """
            data = {}
            if title is not None:
                data['title'] = title
            if section_id is not None:
                data['section_id'] = section_id
            if type_id is not None:
                data['type_id'] = type_id
            if priority_id is not None:
                data['priority_id'] = priority_id
            if estimate is not None:
                data['estimate'] = estimate
            if milestone_id is not None:
                data['milestone_id'] = milestone_id
            if refs is not None:
                data['refs'] = refs
            if template_id is not None:
                data['template_id'] = template_id
            if labels is not None:
                data['labels'] = labels
            if custom_steps_separated is not None:
                data['custom_steps_separated'] = custom_steps_separated
            if steps_separated is not None:
                data['steps_separated'] = steps_separated
            if custom_steps is not None:
                data['custom_steps'] = custom_steps
            if custom_expected is not None:
                data['custom_expected'] = custom_expected
            return self.client.update_case(case_id, data)
        
        @self.tool("delete_case", description="Delete a test case")
        def delete_case(case_id: int) -> Dict:
            """
            Delete a test case.
            
            Args:
                case_id: The ID of the test case
            """
            return self.client.delete_case(case_id)

        @self.tool("update_cases", description="Bulk update multiple test cases with the same values")
        def update_cases(
            suite_id: int,
            case_ids: List[int],
            section_id: Optional[int] = None,
            title: Optional[str] = None,
            template_id: Optional[int] = None,
            type_id: Optional[int] = None,
            priority_id: Optional[int] = None,
            estimate: Optional[str] = None,
            milestone_id: Optional[int] = None,
            refs: Optional[str] = None,
            labels: Optional[List[Union[int, str]]] = None,
            data: Optional[Dict[str, Any]] = None
        ) -> Dict:
            """
            Bulk update multiple test cases with the same values.

            Args:
                suite_id: The suite ID for the cases
                case_ids: The test case IDs to update
            """
            payload: Dict[str, Any] = {'case_ids': case_ids}
            _set_if_present(payload, 'section_id', section_id)
            _set_if_present(payload, 'title', title)
            _set_if_present(payload, 'template_id', template_id)
            _set_if_present(payload, 'type_id', type_id)
            _set_if_present(payload, 'priority_id', priority_id)
            _set_if_present(payload, 'estimate', estimate)
            _set_if_present(payload, 'milestone_id', milestone_id)
            _set_if_present(payload, 'refs', refs)
            _set_if_present(payload, 'labels', labels)
            return self.client.update_cases(suite_id, _merge_payload(payload, data))

        @self.tool("copy_cases_to_section", description="Copy cases to another section")
        def copy_cases_to_section(section_id: int, case_ids: Optional[List[int]] = None) -> Dict:
            """
            Copy cases to another section.

            Args:
                section_id: Destination section ID
                case_ids: Optional list of case IDs to copy
            """
            payload: Dict[str, Any] = {}
            _set_if_present(payload, 'case_ids', case_ids)
            return self.client.copy_cases_to_section(section_id, payload)

        @self.tool("move_cases_to_section", description="Move cases to another section")
        def move_cases_to_section(section_id: int, suite_id: int, case_ids: List[int]) -> Dict:
            """
            Move cases to another section.

            Args:
                section_id: Destination section ID
                suite_id: Destination suite ID
                case_ids: Case IDs to move
            """
            return self.client.move_cases_to_section(section_id, {'suite_id': suite_id, 'case_ids': case_ids})

        # Suite tools
        @self.tool("get_suite", description="Get a suite by ID")
        def get_suite(suite_id: int) -> Dict:
            """Get a suite by ID."""
            return self.client.get_suite(suite_id)

        @self.tool("get_suites", description="Get suites for a project")
        def get_suites(
            project_id: int,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
        ) -> Dict[str, Any]:
            """Get suites for a project."""
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            return self.client.get_suites(project_id, filters or None)

        @self.tool("add_suite", description="Add a new suite")
        def add_suite(project_id: int, name: str, description: Optional[str] = None) -> Dict:
            """Add a new suite."""
            data = {'name': name}
            _set_if_present(data, 'description', description)
            return self.client.add_suite(project_id, data)

        @self.tool("update_suite", description="Update an existing suite")
        def update_suite(suite_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Dict:
            """Update an existing suite."""
            data: Dict[str, Any] = {}
            _set_if_present(data, 'name', name)
            _set_if_present(data, 'description', description)
            return self.client.update_suite(suite_id, data)

        @self.tool("delete_suite", description="Delete a suite")
        def delete_suite(suite_id: int, soft: Optional[bool] = None) -> Dict:
            """Delete a suite."""
            return self.client.delete_suite(suite_id, soft)

        # Section tools
        @self.tool("get_section", description="Retrieves details of a specific section by ID")
        def get_section(section_id: int) -> Dict:
            """
            Get a section by ID.
            
            Args:
                section_id: The ID of the section
            """
            return self.client.get_section(section_id)

        @self.tool("get_sections", description="Retrieves all sections for a specified project and or suite")
        def get_sections(
            project_id : int,
            suite_id: Optional[int] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
        ) -> Dict[str, Any]:
            """
            Retrieves all sections for a specified project and suite
            
            Args:
                project_id: The ID of the project
                suite_id: The ID of the test suite (Optional)

            """
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            return self.client.get_sections(project_id, suite_id, filters or None)

        @self.tool("add_section", description="Creates a new section in a TestRail project")
        def add_section(
            project_id : int,
            name: str,
            description: str,
            suite_id: Optional[int] = None,
            parent_id: Optional[int] = None) -> Dict:
            """
            Retrieves all sections for a specified project and suite
            
            Args:
                project_id: The ID of the project
                name: Name of the section
                description: Description of the section
                suite_id: The ID of the test suite (Optional)
                parent_id: The ID of the parent

            """
            data = {}
            data["name"] = name
            data["description"] = description
            if suite_id is not None:
                data["suite_id"] = suite_id
            if parent_id is not None:
                data["parent_id"] = parent_id

            return self.client.add_section(project_id,data)

        @self.tool("update_section", description="Updates an existing section")
        def update_section(
            section_id : int,
            name: Optional[str] = None,
            description: Optional[str] = None) -> Dict:
            """
            Updates an existing section
            
            Args:
                section_id: The ID of the section
                name: Name of the section
                description: Description of the section
            """
            data = {}
            if name is not None:
                data["name"] = name
            if description is not None:
                data["description"] = description

            return self.client.update_section(section_id, data)

        @self.tool("delete_section", description="Deletes a section")
        def delete_section(
            section_id : int,
            soft: bool) -> Dict:
            """
            Deletes an existing section
            
            Args:
                section_id: The ID of the section
                soft: Omitting the soft parameter, or submitting soft=0 will delete the section and its test cases If soft=1, this will return data on the number of affected tests, cases, etc.
            """

            return self.client.delete_section(section_id, soft)

        @self.tool("move_section", description="Moves a section to a new position in the test hierarchy")
        def move_section(
            section_id : int,
            parent_id : Optional[int],
            after_id : Optional[int]) -> Dict:
            """
            Moves a section to a new position in the test hierarchy
            
            Args:
                section_id: The ID of the section
                parent_id: ID of the new parent
                after_id: ID of the section to be moved after
            """
            data = {}
            if parent_id is not None:
                data["parent_id"] = parent_id
            if after_id is not None:
                data["after_id"] = after_id

            return self.client.move_section(section_id, data)

        # Run tools
        @self.tool("get_run", description="Get a test run by ID")
        def get_run(run_id: int) -> Dict:
            """
            Get a test run by ID.
            
            Args:
                run_id: The ID of the test run
            """
            return self.client.get_run(run_id)
        
        @self.tool("get_runs", description="Get all test runs for a project")
        def get_runs(
            project_id: int,
            created_after: Optional[int] = None,
            created_before: Optional[int] = None,
            created_by: Optional[List[int]] = None,
            include_plan_runs: Optional[bool] = None,
            is_completed: Optional[bool] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            milestone_id: Optional[List[int]] = None,
            refs: Optional[str] = None,
            suite_id: Optional[int] = None,
        ) -> Dict[str, Any]:
            """
            Get test runs for a project.
            
            Args:
                project_id: The ID of the project
            """
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'created_after', created_after)
            _set_if_present(filters, 'created_before', created_before)
            _set_if_present(filters, 'created_by', created_by)
            _set_if_present(filters, 'include_plan_runs', include_plan_runs)
            _set_if_present(filters, 'is_completed', is_completed)
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            _set_if_present(filters, 'milestone_id', milestone_id)
            _set_if_present(filters, 'refs', refs)
            _set_if_present(filters, 'suite_id', suite_id)
            return self.client.get_runs(project_id, filters or None)
        
        @self.tool("add_run", description="Add a new test run")
        def add_run(
            project_id: int,
            suite_id: int,
            name: str,
            description: Optional[str] = None,
            milestone_id: Optional[int] = None,
            assignedto_id: Optional[int] = None,
            refs: Optional[str] = None,
            start_on: Optional[int] = None,
            due_on: Optional[int] = None,
            include_all: Optional[bool] = None,
            case_ids: Optional[List[int]] = None,
            dynamic_filters: Optional[Dict[str, Any]] = None,
        ) -> Dict:
            """
            Add a new test run.
            
            Args:
                project_id: The ID of the project
                suite_id: The ID of the test suite
                name: The name of the test run
                description: The description of the test run (optional)
                milestone_id: The ID of the milestone (optional)
                assignedto_id: The ID of the user the test run should be assigned to (optional)
                include_all: True for including all test cases of the test suite and false for a custom case selection (default: true) (optional)
                case_ids: An array of case IDs for the custom case selection (optional)
            """
            data = {
                'suite_id': suite_id,
                'name': name
            }
            if description is not None:
                data['description'] = description
            if milestone_id is not None:
                data['milestone_id'] = milestone_id
            if assignedto_id is not None:
                data['assignedto_id'] = assignedto_id
            if refs is not None:
                data['refs'] = refs
            if start_on is not None:
                data['start_on'] = start_on
            if due_on is not None:
                data['due_on'] = due_on
            if include_all is not None:
                data['include_all'] = include_all
            if case_ids is not None:
                data['case_ids'] = case_ids
            if dynamic_filters is not None:
                data['dynamic_filters'] = dynamic_filters
            return self.client.add_run(project_id, data)
        
        @self.tool("update_run", description="Update an existing test run")
        def update_run(
            run_id: int,
            name: Optional[str] = None,
            description: Optional[str] = None,
            milestone_id: Optional[int] = None,
            assignedto_id: Optional[int] = None,
            refs: Optional[str] = None,
            start_on: Optional[int] = None,
            due_on: Optional[int] = None,
            include_all: Optional[bool] = None,
            case_ids: Optional[List[int]] = None,
            dynamic_filters: Optional[Dict[str, Any]] = None,
        ) -> Dict:
            """
            Update an existing test run.
            
            Args:
                run_id: The ID of the test run
                name: The name of the test run (optional)
                description: The description of the test run (optional)
                milestone_id: The ID of the milestone (optional)
                assignedto_id: The ID of the user the test run should be assigned to (optional)
                include_all: True for including all test cases of the test suite and false for a custom case selection (default: true) (optional)
                case_ids: An array of case IDs for the custom case selection (optional)
            """
            data = {}
            if name is not None:
                data['name'] = name
            if description is not None:
                data['description'] = description
            if milestone_id is not None:
                data['milestone_id'] = milestone_id
            if assignedto_id is not None:
                data['assignedto_id'] = assignedto_id
            if refs is not None:
                data['refs'] = refs
            if start_on is not None:
                data['start_on'] = start_on
            if due_on is not None:
                data['due_on'] = due_on
            if include_all is not None:
                data['include_all'] = include_all
            if case_ids is not None:
                data['case_ids'] = case_ids
            if dynamic_filters is not None:
                data['dynamic_filters'] = dynamic_filters
            return self.client.update_run(run_id, data)
        
        @self.tool("close_run", description="Close an existing test run")
        def close_run(run_id: int) -> Dict:
            """
            Close an existing test run.
            
            Args:
                run_id: The ID of the test run
            """
            return self.client.close_run(run_id)
        
        @self.tool("delete_run", description="Delete a test run")
        def delete_run(run_id: int, soft: Optional[bool] = None) -> Dict:
            """
            Delete a test run.
            
            Args:
                run_id: The ID of the test run
            """
            return self.client.delete_run(run_id, soft)
        
        # Results tools
        @self.tool("get_results", description="Get all test results for a test")
        def get_results(
            test_id: int,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            status_id: Optional[List[int]] = None,
            defects_filter: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Get all test results for a test.
            
            Args:
                test_id: The ID of the test
            """
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            _set_if_present(filters, 'status_id', status_id)
            _set_if_present(filters, 'defects_filter', defects_filter)
            return self.client.get_results(test_id, filters or None)

        @self.tool("get_results_for_case", description="Get all test results for a run and case combination")
        def get_results_for_case(
            run_id: int,
            case_id: int,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            status_id: Optional[List[int]] = None,
            defects_filter: Optional[str] = None
        ) -> Dict[str, Any]:
            """Get all test results for a run and case combination."""
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            _set_if_present(filters, 'status_id', status_id)
            _set_if_present(filters, 'defects_filter', defects_filter)
            return self.client.get_results_for_case(run_id, case_id, filters or None)

        @self.tool("get_results_for_run", description="Get all test results for a run")
        def get_results_for_run(
            run_id: int,
            created_after: Optional[int] = None,
            created_before: Optional[int] = None,
            created_by: Optional[List[int]] = None,
            defects_filter: Optional[str] = None,
            status_id: Optional[List[int]] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None
        ) -> Dict[str, Any]:
            """Get all test results for a run."""
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'created_after', created_after)
            _set_if_present(filters, 'created_before', created_before)
            _set_if_present(filters, 'created_by', created_by)
            _set_if_present(filters, 'defects_filter', defects_filter)
            _set_if_present(filters, 'status_id', status_id)
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            return self.client.get_results_for_run(run_id, filters or None)
        
        @self.tool("add_result", description="Add a new test result")
        def add_result(
            test_id: int,
            status_id: int,
            comment: Optional[str] = None,
            version: Optional[str] = None,
            elapsed: Optional[str] = None,
            defects: Optional[str] = None,
            assignedto_id: Optional[int] = None,
            data: Optional[Dict[str, Any]] = None
        ) -> Dict:
            """
            Add a new test result.
            
            Args:
                test_id: The ID of the test
                status_id: The ID of the test status
                comment: The comment / description for the test result (optional)
                version: The version or build you tested against (optional)
                elapsed: The time it took to execute the test, e.g. '30s' or '1m 45s' (optional)
                defects: A comma-separated list of defects to link to the test result (optional)
                assignedto_id: The ID of a user the test should be assigned to (optional)
            """
            payload = {'status_id': status_id}
            if comment is not None:
                payload['comment'] = comment
            if version is not None:
                payload['version'] = version
            if elapsed is not None:
                payload['elapsed'] = elapsed
            if defects is not None:
                payload['defects'] = defects
            if assignedto_id is not None:
                payload['assignedto_id'] = assignedto_id
            return self.client.add_result(test_id, _merge_payload(payload, data))

        @self.tool("add_result_for_case", description="Add a new test result for a run and case combination")
        def add_result_for_case(
            run_id: int,
            case_id: int,
            status_id: int,
            comment: Optional[str] = None,
            version: Optional[str] = None,
            elapsed: Optional[str] = None,
            defects: Optional[str] = None,
            assignedto_id: Optional[int] = None,
            data: Optional[Dict[str, Any]] = None
        ) -> Dict:
            """Add a new test result for a run and case combination."""
            payload = {'status_id': status_id}
            _set_if_present(payload, 'comment', comment)
            _set_if_present(payload, 'version', version)
            _set_if_present(payload, 'elapsed', elapsed)
            _set_if_present(payload, 'defects', defects)
            _set_if_present(payload, 'assignedto_id', assignedto_id)
            return self.client.add_result_for_case(run_id, case_id, _merge_payload(payload, data))

        @self.tool("add_results", description="Add multiple test results to a run")
        def add_results(run_id: int, results: List[Dict[str, Any]]) -> Dict[str, Any]:
            """Add multiple test results to a run."""
            return self.client.add_results(run_id, {'results': results})

        @self.tool("add_results_for_cases", description="Add multiple test results to a run by case ID")
        def add_results_for_cases(run_id: int, results: List[Dict[str, Any]]) -> Dict[str, Any]:
            """Add multiple test results to a run using case IDs."""
            return self.client.add_results_for_cases(run_id, {'results': results})

        # Test tools
        @self.tool("get_test", description="Get a test by ID")
        def get_test(test_id: int, with_data: Optional[str] = None) -> Dict:
            """Get a test by ID."""
            return self.client.get_test(test_id, with_data)

        @self.tool("get_tests", description="Get all tests for a run")
        def get_tests(
            run_id: int,
            status_id: Optional[List[int]] = None,
            label_id: Optional[List[int]] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None
        ) -> Dict[str, Any]:
            """Get all tests for a run."""
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'status_id', status_id)
            _set_if_present(filters, 'label_id', label_id)
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            return self.client.get_tests(run_id, filters or None)

        @self.tool("update_test", description="Update labels for an existing test")
        def update_test(test_id: int, labels: List[Union[int, str]]) -> Dict:
            """Update labels for an existing test."""
            return self.client.update_test(test_id, {'labels': labels})

        @self.tool("update_tests", description="Bulk update labels for multiple tests")
        def update_tests(test_ids: List[int], labels: List[Union[int, str]]) -> Dict:
            """Bulk update labels for multiple tests."""
            return self.client.update_tests({'test_ids': test_ids, 'labels': labels})

        # Metadata lookup tools
        @self.tool("get_templates", description="Get templates for a project")
        def get_templates(project_id: int) -> List[Dict]:
            """Get templates for a project."""
            return self.client.get_templates(project_id)

        @self.tool("get_case_fields", description="Get custom case fields")
        def get_case_fields() -> List[Dict]:
            """Get custom case fields."""
            return self.client.get_case_fields()

        @self.tool("get_result_fields", description="Get custom result fields")
        def get_result_fields() -> List[Dict]:
            """Get custom result fields."""
            return self.client.get_result_fields()

        @self.tool("get_case_types", description="Get case types")
        def get_case_types() -> List[Dict]:
            """Get case types."""
            return self.client.get_case_types()

        @self.tool("get_priorities", description="Get priorities")
        def get_priorities() -> List[Dict]:
            """Get priorities."""
            return self.client.get_priorities()

        @self.tool("get_statuses", description="Get test statuses")
        def get_statuses() -> List[Dict]:
            """Get test statuses."""
            return self.client.get_statuses()

        @self.tool("get_case_statuses", description="Get case statuses")
        def get_case_statuses() -> List[Dict]:
            """Get case statuses."""
            return self.client.get_case_statuses()

        @self.tool("get_dynamic_filter_fields", description="Get dynamic filter fields for a project")
        def get_dynamic_filter_fields(project_id: int) -> List[Dict]:
            """Get dynamic filter fields for a project."""
            return self.client.get_dynamic_filter_fields(project_id)

        # Label tools
        @self.tool("get_label", description="Get a label by ID")
        def get_label(label_id: int) -> Dict:
            """Get a label by ID."""
            return self.client.get_label(label_id)

        @self.tool("get_labels", description="Get labels for a project")
        def get_labels(project_id: int, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict[str, Any]:
            """Get labels for a project."""
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            return self.client.get_labels(project_id, filters or None)

        @self.tool("update_label", description="Update an existing label")
        def update_label(label_id: int, project_id: int, title: str) -> Dict:
            """Update an existing label."""
            return self.client.update_label(label_id, {'project_id': project_id, 'title': title})

        # User tools
        @self.tool("get_user", description="Get a user by ID")
        def get_user(user_id: int) -> Dict:
            """Get a user by ID."""
            return self.client.get_user(user_id)

        @self.tool("get_current_user", description="Get the current API user")
        def get_current_user(user_id: int) -> Dict:
            """Get the current API user details."""
            return self.client.get_current_user(user_id)

        @self.tool("get_user_by_email", description="Get a user by email")
        def get_user_by_email(email: str) -> Dict:
            """Get a user by email."""
            return self.client.get_user_by_email(email)

        @self.tool("get_users", description="Get users, optionally scoped to a project")
        def get_users(project_id: Optional[int] = None) -> List[Dict]:
            """Get users, optionally scoped to a project."""
            return self.client.get_users(project_id)

        @self.tool("add_user", description="Add a new user")
        def add_user(
            name: str,
            email: str,
            role_id: Optional[int] = None,
            is_active: Optional[bool] = None,
            is_admin: Optional[bool] = None,
            email_notifications: Optional[bool] = None,
            group_ids: Optional[List[int]] = None,
            assigned_projects: Optional[List[int]] = None,
            mfa_required: Optional[bool] = None,
            sso_enabled: Optional[bool] = None
        ) -> Dict:
            """Add a new user."""
            payload = {'name': name, 'email': email}
            _set_if_present(payload, 'role_id', role_id)
            _set_if_present(payload, 'is_active', is_active)
            _set_if_present(payload, 'is_admin', is_admin)
            _set_if_present(payload, 'email_notifications', email_notifications)
            _set_if_present(payload, 'group_ids', group_ids)
            _set_if_present(payload, 'assigned_projects', assigned_projects)
            _set_if_present(payload, 'mfa_required', mfa_required)
            _set_if_present(payload, 'sso_enabled', sso_enabled)
            return self.client.add_user(payload)

        @self.tool("update_user", description="Update an existing user")
        def update_user(
            user_id: int,
            name: Optional[str] = None,
            email: Optional[str] = None,
            role_id: Optional[int] = None,
            is_active: Optional[bool] = None,
            is_admin: Optional[bool] = None,
            email_notifications: Optional[bool] = None,
            group_ids: Optional[List[int]] = None,
            assigned_projects: Optional[List[int]] = None,
            mfa_required: Optional[bool] = None,
            sso_enabled: Optional[bool] = None
        ) -> Dict:
            """Update an existing user."""
            payload: Dict[str, Any] = {}
            _set_if_present(payload, 'name', name)
            _set_if_present(payload, 'email', email)
            _set_if_present(payload, 'role_id', role_id)
            _set_if_present(payload, 'is_active', is_active)
            _set_if_present(payload, 'is_admin', is_admin)
            _set_if_present(payload, 'email_notifications', email_notifications)
            _set_if_present(payload, 'group_ids', group_ids)
            _set_if_present(payload, 'assigned_projects', assigned_projects)
            _set_if_present(payload, 'mfa_required', mfa_required)
            _set_if_present(payload, 'sso_enabled', sso_enabled)
            return self.client.update_user(user_id, payload)

        # Configuration tools
        @self.tool("get_configs", description="Get configurations for a project")
        def get_configs(project_id: int) -> List[Dict]:
            """Get configurations for a project."""
            return self.client.get_configs(project_id)

        @self.tool("add_config_group", description="Add a configuration group")
        def add_config_group(project_id: int, name: str) -> Dict:
            """Add a configuration group."""
            return self.client.add_config_group(project_id, {'name': name})

        @self.tool("add_config", description="Add a configuration")
        def add_config(config_group_id: int, name: str) -> Dict:
            """Add a configuration."""
            return self.client.add_config(config_group_id, {'name': name})

        @self.tool("update_config_group", description="Update a configuration group")
        def update_config_group(config_group_id: int, name: str) -> Dict:
            """Update a configuration group."""
            return self.client.update_config_group(config_group_id, {'name': name})

        @self.tool("update_config", description="Update a configuration")
        def update_config(config_id: int, name: str) -> Dict:
            """Update a configuration."""
            return self.client.update_config(config_id, {'name': name})

        @self.tool("delete_config_group", description="Delete a configuration group")
        def delete_config_group(config_group_id: int) -> Dict:
            """Delete a configuration group."""
            return self.client.delete_config_group(config_group_id)

        @self.tool("delete_config", description="Delete a configuration")
        def delete_config(config_id: int) -> Dict:
            """Delete a configuration."""
            return self.client.delete_config(config_id)

        # Shared steps tools
        @self.tool("get_shared_step", description="Get a shared step by ID")
        def get_shared_step(shared_step_id: int) -> Dict:
            """Get a shared step by ID."""
            return self.client.get_shared_step(shared_step_id)

        @self.tool("get_shared_step_history", description="Get history for a shared step")
        def get_shared_step_history(shared_step_id: int) -> Dict[str, Any]:
            """Get history for a shared step."""
            return self.client.get_shared_step_history(shared_step_id)

        @self.tool("get_shared_steps", description="Get shared steps for a project")
        def get_shared_steps(
            project_id: int,
            created_after: Optional[int] = None,
            created_before: Optional[int] = None,
            created_by: Optional[List[int]] = None,
            updated_after: Optional[int] = None,
            updated_before: Optional[int] = None,
            refs: Optional[str] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None
        ) -> Dict[str, Any]:
            """Get shared steps for a project."""
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'created_after', created_after)
            _set_if_present(filters, 'created_before', created_before)
            _set_if_present(filters, 'created_by', created_by)
            _set_if_present(filters, 'updated_after', updated_after)
            _set_if_present(filters, 'updated_before', updated_before)
            _set_if_present(filters, 'refs', refs)
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            return self.client.get_shared_steps(project_id, filters or None)

        @self.tool("add_shared_step", description="Add a new shared step set")
        def add_shared_step(project_id: int, title: str, custom_steps_separated: Optional[List[Dict[str, Any]]] = None, refs: Optional[str] = None) -> Dict:
            """Add a shared step set."""
            payload: Dict[str, Any] = {'title': title}
            _set_if_present(payload, 'custom_steps_separated', custom_steps_separated)
            _set_if_present(payload, 'refs', refs)
            return self.client.add_shared_step(project_id, payload)

        @self.tool("update_shared_step", description="Update an existing shared step set")
        def update_shared_step(
            shared_step_id: int,
            title: Optional[str] = None,
            custom_steps_separated: Optional[List[Dict[str, Any]]] = None,
            refs: Optional[str] = None
        ) -> Dict:
            """Update an existing shared step set."""
            payload: Dict[str, Any] = {}
            _set_if_present(payload, 'title', title)
            _set_if_present(payload, 'custom_steps_separated', custom_steps_separated)
            _set_if_present(payload, 'refs', refs)
            return self.client.update_shared_step(shared_step_id, payload)

        @self.tool("delete_shared_step", description="Delete a shared step set")
        def delete_shared_step(shared_step_id: int, keep_in_cases: Optional[bool] = None) -> Dict:
            """Delete a shared step set."""
            payload: Dict[str, Any] = {}
            _set_if_present(payload, 'keep_in_cases', keep_in_cases)
            return self.client.delete_shared_step(shared_step_id, payload or None)

        # Attachment tools
        @self.tool("add_attachment_to_case", description="Add an attachment to a case")
        def add_attachment_to_case(case_id: int, file_path: str) -> Dict[str, Any]:
            """Add an attachment to a case."""
            return self.client.add_attachment_to_case(case_id, file_path)

        @self.tool("add_attachment_to_plan", description="Add an attachment to a plan")
        def add_attachment_to_plan(plan_id: int, file_path: str) -> Dict[str, Any]:
            """Add an attachment to a plan."""
            return self.client.add_attachment_to_plan(plan_id, file_path)

        @self.tool("add_attachment_to_plan_entry", description="Add an attachment to a plan entry")
        def add_attachment_to_plan_entry(plan_id: int, entry_id: str, file_path: str) -> Dict[str, Any]:
            """Add an attachment to a plan entry."""
            return self.client.add_attachment_to_plan_entry(plan_id, entry_id, file_path)

        @self.tool("add_attachment_to_result", description="Add an attachment to a result")
        def add_attachment_to_result(result_id: int, file_path: str) -> Dict[str, Any]:
            """Add an attachment to a result."""
            return self.client.add_attachment_to_result(result_id, file_path)

        @self.tool("add_attachment_to_run", description="Add an attachment to a run")
        def add_attachment_to_run(run_id: int, file_path: str) -> Dict[str, Any]:
            """Add an attachment to a run."""
            return self.client.add_attachment_to_run(run_id, file_path)

        @self.tool("get_attachments_for_case", description="Get attachments for a case")
        def get_attachments_for_case(case_id: int, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict[str, Any]:
            """Get attachments for a case."""
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            return self.client.get_attachments_for_case(case_id, filters or None)

        @self.tool("get_attachments_for_plan", description="Get attachments for a plan")
        def get_attachments_for_plan(plan_id: int, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict[str, Any]:
            """Get attachments for a plan."""
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            return self.client.get_attachments_for_plan(plan_id, filters or None)

        @self.tool("get_attachments_for_plan_entry", description="Get attachments for a plan entry")
        def get_attachments_for_plan_entry(plan_id: int, entry_id: str) -> List[Dict]:
            """Get attachments for a plan entry."""
            return self.client.get_attachments_for_plan_entry(plan_id, entry_id)

        @self.tool("get_attachments_for_run", description="Get attachments for a run")
        def get_attachments_for_run(run_id: int, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict]:
            """Get attachments for a run."""
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            return self.client.get_attachments_for_run(run_id, filters or None)

        @self.tool("get_attachments_for_test", description="Get attachments for a test")
        def get_attachments_for_test(test_id: int) -> List[Dict]:
            """Get attachments for a test."""
            return self.client.get_attachments_for_test(test_id)

        @self.tool("get_attachment", description="Get an attachment body encoded as base64")
        def get_attachment(attachment_id: Union[int, str]) -> Dict[str, Any]:
            """Get an attachment body encoded as base64 for MCP transport."""
            return self.client.get_attachment(attachment_id)

        @self.tool("delete_attachment", description="Delete an attachment")
        def delete_attachment(attachment_id: Union[int, str]) -> Dict:
            """Delete an attachment."""
            return self.client.delete_attachment(attachment_id)

        # Report tools
        @self.tool("get_reports", description="Get API-accessible reports for a project")
        def get_reports(project_id: int) -> List[Dict]:
            """Get API-accessible reports for a project."""
            return self.client.get_reports(project_id)

        @self.tool("run_report", description="Run a single-project report")
        def run_report(report_template_id: int) -> Dict:
            """Run a single-project report."""
            return self.client.run_report(report_template_id)

        @self.tool("get_cross_project_reports", description="Get API-accessible cross-project reports")
        def get_cross_project_reports() -> List[Dict]:
            """Get API-accessible cross-project reports."""
            return self.client.get_cross_project_reports()

        @self.tool("run_cross_project_report", description="Run a cross-project report")
        def run_cross_project_report(report_template_id: int) -> Dict:
            """Run a cross-project report."""
            return self.client.run_cross_project_report(report_template_id)
        
        # Dataset tools
        @self.tool("get_dataset", description="Get a dataset by ID")
        def get_dataset(dataset_id: int) -> Dict:
            """
            Get a dataset by ID.
            
            Args:
                dataset_id: The ID of the dataset
            """
            return self.client.get_dataset(dataset_id)
        
        @self.tool("get_datasets", description="Get all datasets for a project")
        def get_datasets(
            project_id: int,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
        ) -> Dict[str, Any]:
            """
            Get all datasets for a project.
            
            Args:
                project_id: The ID of the project
            """
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            return self.client.get_datasets(project_id, filters or None)
        
        @self.tool("add_dataset", description="Add a new dataset")
        def add_dataset(
            project_id: int,
            name: str,
            description: Optional[str] = None
        ) -> Dict:
            """
            Add a new dataset.
            
            Args:
                project_id: The ID of the project
                name: The name of the dataset
                description: The description of the dataset (optional)
            """
            data = {
                'name': name
            }
            if description is not None:
                data['description'] = description
            return self.client.add_dataset(project_id, data)
        
        @self.tool("update_dataset", description="Update an existing dataset")
        def update_dataset(
            dataset_id: int,
            name: Optional[str] = None,
            description: Optional[str] = None
        ) -> Dict:
            """
            Update an existing dataset.
            
            Args:
                dataset_id: The ID of the dataset
                name: The name of the dataset (optional)
                description: The description of the dataset (optional)
            """
            data = {}
            if name is not None:
                data['name'] = name
            if description is not None:
                data['description'] = description
            return self.client.update_dataset(dataset_id, data)
        
        @self.tool("delete_dataset", description="Delete a dataset")
        def delete_dataset(dataset_id: int) -> Dict:
            """
            Delete a dataset.
            
            Args:
                dataset_id: The ID of the dataset
            """
            return self.client.delete_dataset(dataset_id)

        # Variable tools
        @self.tool("get_variables", description="Get variables for a project")
        def get_variables(
            project_id: int,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
        ) -> Dict[str, Any]:
            """Get variables for a project."""
            filters: Dict[str, Any] = {}
            _set_if_present(filters, 'limit', limit)
            _set_if_present(filters, 'offset', offset)
            return self.client.get_variables(project_id, filters or None)

        @self.tool("add_variable", description="Add a new variable")
        def add_variable(project_id: int, name: str) -> Dict:
            """Add a new variable."""
            return self.client.add_variable(project_id, {'name': name})

        @self.tool("update_variable", description="Update an existing variable")
        def update_variable(variable_id: int, name: str) -> Dict:
            """Update an existing variable."""
            return self.client.update_variable(variable_id, {'name': name})

        @self.tool("delete_variable", description="Delete a variable")
        def delete_variable(variable_id: int) -> Dict:
            """Delete a variable."""
            return self.client.delete_variable(variable_id)
    
    def _register_resources(self):
        """Register all TestRail resources with the MCP server."""
        @self.resource("testrail://project/{project_id}")
        def get_project_resource(project_id: int) -> Dict:
            """
            Get a project by ID.
            
            Args:
                project_id: The ID of the project
            """
            return self.client.get_project(project_id)
        
        @self.resource("testrail://case/{case_id}")
        def get_case_resource(case_id: int) -> Dict:
            """
            Get a test case by ID.
            
            Args:
                case_id: The ID of the test case
            """
            return self.client.get_case(case_id)
        
        @self.resource("testrail://run/{run_id}")
        def get_run_resource(run_id: int) -> Dict:
            """
            Get a test run by ID.
            
            Args:
                run_id: The ID of the test run
            """
            return self.client.get_run(run_id)
        
        @self.resource("testrail://results/{test_id}")
        def get_results_resource(test_id: int) -> List[Dict]:
            """
            Get all test results for a test.
            
            Args:
                test_id: The ID of the test
            """
            return self.client.get_results(test_id)
        
        @self.resource("testrail://dataset/{dataset_id}")
        def get_dataset_resource(dataset_id: int) -> Dict:
            """
            Get a dataset by ID.
            
            Args:
                dataset_id: The ID of the dataset
            """
            return self.client.get_dataset(dataset_id)
