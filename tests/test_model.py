import unittest
from pydantic import ValidationError
from src.langgraphapi.models import HeaderModel, BodyModel, QueryModel, CustomAPIInterface

class TestModels(unittest.TestCase):
    def test_header_model(self):
        valid_header = {"Content-Type": "application/json"}
        header = HeaderModel(**valid_header)
        self.assertEqual(header.dict(), valid_header)

        with self.assertRaises(ValidationError):
            HeaderModel(**{"Content-Type": 123})  # Invalid type

    def test_body_model(self):
        valid_body = {
            "department": "sales",
            "account_owner": "John Doe",
            "manager": "Jane Smith",
            "topic": "Account update request",
            "account_info": "Customer ID: 12345, Last contact: 2023-12-01"
        }
        body = BodyModel(**valid_body)
        self.assertEqual(body.dict(), valid_body)

        with self.assertRaises(ValidationError):
            BodyModel(**{"department": 123})  # Invalid type

    def test_query_model(self):
        valid_query = {"param1": "value1", "param2": "value2"}
        query = QueryModel(**valid_query)
        self.assertEqual(query.dict(), valid_query)

        with self.assertRaises(ValidationError):
            QueryModel(**{"param1": 123})  # Invalid type

    def test_custom_api_interface(self):
        valid_data = {
            "request_type": "POST",
            "uri": "http://example.com/api",
            "headers": {"Content-Type": "application/json"},
            "body": {
                "department": "sales",
                "account_owner": "John Doe",
                "manager": "Jane Smith",
                "topic": "Account update request",
                "account_info": "Customer ID: 12345, Last contact: 2023-12-01"
            },
            "query": {"param1": "value1"}
        }
        api_interface = CustomAPIInterface(**valid_data)
        self.assertEqual(api_interface.dict(), valid_data)

        with self.assertRaises(ValidationError):
            CustomAPIInterface(**{**valid_data, "request_type": "INVALID"})

if __name__ == '__main__':
    unittest.main()
