import unittest
from unittest.mock import patch, Mock
from pydantic import HttpUrl
from src.langgraphapi.models import CustomAPIInterface, APIField
from src.langgraphapi.wrapper import APICallerTool, APICallerInput

class TestAPICallerTool(unittest.TestCase):

    def setUp(self):
        self.api_interface = CustomAPIInterface(
            method="GET",
            url=HttpUrl("https://api.example.com/data"),
            headers={
                "Authorization": APIField(description="Auth token"),
                "Content-Type": APIField(value="application/json", description="Content type")
            },
            body={
                "username": APIField(description="User's username"),
                "password": APIField(description="User's password")
            },
            query={
                "limit": APIField(description="Number of items to return"),
                "offset": APIField(description="Starting index")
            }
        )
        self.api_caller_tool = APICallerTool(api_interface=self.api_interface)

    def test_initialization(self):
        self.assertEqual(self.api_caller_tool.name, "api_caller")
        self.assertIsInstance(self.api_caller_tool.args_schema, type(APICallerInput))

    def test_get_api_details(self):
        result = self.api_caller_tool.get_api_details()
        self.assertEqual(result, self.api_interface)
        self.assertTrue(self.api_caller_tool.state.api_details_retrieved)

    @patch('requests.request')
    def test_fill_and_request(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.headers = {'content-type': 'application/json'}
        mock_request.return_value = mock_response

        result = self.api_caller_tool.fill_and_request(
            headers={"Authorization": "Bearer token123"},
            body={"username": "testuser", "password": "testpass"},
            query={"limit": "10", "offset": "0"}
        )

        self.assertEqual(result, {"status_code": 200, "response": {"data": "test"}})
        self.assertEqual(self.api_interface.headers["Authorization"].value, "Bearer token123")
        self.assertEqual(self.api_interface.body["username"].value, "testuser")
        self.assertEqual(self.api_interface.query["limit"].value, "10")

    def test_run_get_api_details(self):
        result = self.api_caller_tool._run("get_api_details")
        self.assertEqual(result, self.api_interface)

    @patch('requests.request')
    def test_run_fill_and_request(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.headers = {'content-type': 'application/json'}
        mock_request.return_value = mock_response

        result = self.api_caller_tool._run(
            "fill_and_request",
            headers={"Authorization": "Bearer token123"},
            body={"username": "testuser", "password": "testpass"},
            query={"limit": "10", "offset": "0"}
        )

        self.assertEqual(result, {"status_code": 200, "response": {"data": "test"}})

    def test_run_invalid_action(self):
        result = self.api_caller_tool._run("invalid_action")
        self.assertEqual(result, {"error": "Invalid action. Use 'get_api_details' or 'fill_and_request'."})

    @patch('requests.request')
    async def test_arun(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.headers = {'content-type': 'application/json'}
        mock_request.return_value = mock_response

        result = await self.api_caller_tool._arun(
            "fill_and_request",
            headers={"Authorization": "Bearer token123"},
            body={"username": "testuser", "password": "testpass"},
            query={"limit": "10", "offset": "0"}
        )

        self.assertEqual(result, {"status_code": 200, "response": {"data": "test"}})

if __name__ == '__main__':
    unittest.main()
