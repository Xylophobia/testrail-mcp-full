import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock

if 'requests' not in sys.modules:
    class _DummySession:
        def __init__(self):
            self.headers = {}

    sys.modules['requests'] = types.SimpleNamespace(Session=_DummySession)

from testrail_mcp.testrail_client import TestRailClient


def make_json_response(payload):
    response = MagicMock()
    response.status_code = 200
    response.content = b'{}'
    response.json.return_value = payload
    return response


def make_binary_response(payload: bytes, headers=None):
    response = MagicMock()
    response.status_code = 200
    response.content = payload
    response.headers = headers or {}
    return response


class TestRailClientQueryTests(unittest.TestCase):
    def setUp(self):
        self.client = TestRailClient('https://example.testrail.io', 'user', 'key')
        self.client.session = MagicMock()
        self.client.session.headers = {
            'Authorization': 'Basic test',
            'Content-Type': 'application/json',
        }

    def test_get_sections_sends_suite_and_pagination_filters(self):
        self.client.session.get.return_value = make_json_response({'sections': []})

        self.client.get_sections(12, suite_id=7, filters={'limit': 50, 'offset': 100})

        self.client.session.get.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/get_sections/12&limit=50&offset=100&suite_id=7'
        )

    def test_get_projects_sends_current_filters(self):
        self.client.session.get.return_value = make_json_response({'projects': []})

        self.client.get_projects({'is_completed': False, 'limit': 10, 'offset': 20})

        self.client.session.get.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/get_projects&is_completed=0&limit=10&offset=20'
        )

    def test_get_cases_sends_current_filters(self):
        self.client.session.get.return_value = make_json_response({'cases': []})

        self.client.get_cases(
            34,
            {
                'suite_id': 2,
                'created_by': [1, 5],
                'priority_id': [3, 4],
                'updated_after': 1710000000,
                'label_id': [9],
            },
        )

        self.client.session.get.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/get_cases/34&suite_id=2&created_by=1%2C5&priority_id=3%2C4&updated_after=1710000000&label_id=9'
        )

    def test_get_runs_sends_current_filters(self):
        self.client.session.get.return_value = make_json_response({'runs': []})

        self.client.get_runs(
            9,
            {
                'created_before': 1710000100,
                'include_plan_runs': True,
                'is_completed': False,
                'milestone_id': [11, 12],
                'suite_id': 4,
            },
        )

        self.client.session.get.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/get_runs/9&created_before=1710000100&include_plan_runs=1&is_completed=0&milestone_id=11%2C12&suite_id=4'
        )

    def test_get_datasets_sends_pagination_filters(self):
        self.client.session.get.return_value = make_json_response({'datasets': []})

        self.client.get_datasets(3, {'limit': 25, 'offset': 75})

        self.client.session.get.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/get_datasets/3&limit=25&offset=75'
        )

    def test_get_milestones_sends_filters(self):
        self.client.session.get.return_value = make_json_response({'milestones': []})

        self.client.get_milestones(5, {'is_completed': False, 'is_started': True, 'limit': 10, 'offset': 20})

        self.client.session.get.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/get_milestones/5&is_completed=0&is_started=1&limit=10&offset=20'
        )

    def test_get_suites_sends_pagination_filters(self):
        self.client.session.get.return_value = make_json_response({'suites': []})

        self.client.get_suites(8, {'limit': 15, 'offset': 30})

        self.client.session.get.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/get_suites/8&limit=15&offset=30'
        )

    def test_delete_run_supports_soft_mode(self):
        self.client.session.post.return_value = make_json_response({'ok': True})

        self.client.delete_run(42, soft=True)

        self.client.session.post.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/delete_run/42&soft=1',
            data=None,
        )

    def test_delete_suite_supports_soft_mode(self):
        self.client.session.post.return_value = make_json_response({'ok': True})

        self.client.delete_suite(17, soft=True)

        self.client.session.post.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/delete_suite/17&soft=1',
            data=None,
        )

    def test_delete_section_supports_soft_mode(self):
        self.client.session.post.return_value = make_json_response({'ok': True})

        self.client.delete_section(11, soft=True)

        self.client.session.post.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/delete_section/11&soft=1',
            data=None,
        )

    def test_get_current_user_with_user_id_uses_parameterized_endpoint(self):
        self.client.session.get.return_value = make_json_response({'id': 1})

        self.client.get_current_user(21)

        self.client.session.get.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/get_current_user/21'
        )

    def test_get_test_supports_with_data_filter(self):
        self.client.session.get.return_value = make_json_response({'id': 100})

        self.client.get_test(100, with_data='steps')

        self.client.session.get.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/get_test/100&with_data=steps'
        )

    def test_get_tests_supports_status_and_label_filters(self):
        self.client.session.get.return_value = make_json_response({'tests': []})

        self.client.get_tests(77, {'status_id': [4, 5], 'label_id': [2], 'limit': 30, 'offset': 10})

        self.client.session.get.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/get_tests/77&status_id=4%2C5&label_id=2&limit=30&offset=10'
        )

    def test_get_user_by_email_uses_query_parameter(self):
        self.client.session.get.return_value = make_json_response({'id': 2})

        self.client.get_user_by_email('john.doe@example.com')

        self.client.session.get.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/get_user_by_email&email=john.doe%40example.com'
        )

    def test_add_plan_entry_posts_to_plan_entry_endpoint(self):
        self.client.session.post.return_value = make_json_response({'id': 'entry-1'})

        self.client.add_plan_entry(5, {'suite_id': 3})

        self.client.session.post.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/add_plan_entry/5',
            data='{"suite_id": 3}',
        )

    def test_add_run_to_plan_entry_posts_to_nested_endpoint(self):
        self.client.session.post.return_value = make_json_response({'id': 42})

        self.client.add_run_to_plan_entry(5, 'entry-7', {'config_ids': [9]})

        self.client.session.post.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/add_run_to_plan_entry/5/entry-7',
            data='{"config_ids": [9]}',
        )

    def test_add_attachment_to_case_uses_multipart_upload(self):
        self.client.session.post.return_value = make_json_response({'attachment_id': 443})

        with tempfile.NamedTemporaryFile(suffix='.txt') as temp:
            temp.write(b'hello')
            temp.flush()
            self.client.add_attachment_to_case(99, temp.name)

        self.client.session.post.assert_called_once()
        args, kwargs = self.client.session.post.call_args
        self.assertEqual(
            args[0],
            'https://example.testrail.io/index.php?/api/v2/add_attachment_to_case/99',
        )
        self.assertIn('files', kwargs)
        self.assertIn('headers', kwargs)
        self.assertNotIn('Content-Type', kwargs['headers'])

    def test_get_attachment_returns_base64_encoded_body(self):
        self.client.session.get.return_value = make_binary_response(
            b'abc123',
            {
                'Content-Type': 'application/octet-stream',
                'Content-Disposition': 'attachment; filename="file.bin"',
            },
        )

        attachment = self.client.get_attachment('2ec27be4-812f-4806-9a5d-d39130d1691a')

        self.client.session.get.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/get_attachment/2ec27be4-812f-4806-9a5d-d39130d1691a'
        )
        self.assertEqual(attachment['content_base64'], 'YWJjMTIz')
        self.assertEqual(attachment['size'], 6)
        self.assertEqual(attachment['content_type'], 'application/octet-stream')

    def test_get_reports_calls_project_endpoint(self):
        self.client.session.get.return_value = make_json_response([])

        self.client.get_reports(8)

        self.client.session.get.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/get_reports/8'
        )

    def test_run_cross_project_report_calls_correct_endpoint(self):
        self.client.session.get.return_value = make_json_response({'ok': True})

        self.client.run_cross_project_report(12)

        self.client.session.get.assert_called_once_with(
            'https://example.testrail.io/index.php?/api/v2/run_cross_project_report/12'
        )


if __name__ == '__main__':
    unittest.main()
