import unittest
from pydantic import BaseModel, ValidationError
from typing import Optional
from src.langgraphapi.models import APIField, CustomAPIInterface

class TestAPIField(unittest.TestCase):
    def test_both_value_and_description(self):
        field = APIField(value="Bearer token", description="Auth token")
        self.assertEqual(field.value, "Bearer token")
        self.assertEqual(field.description, "Auth token")

    def test_only_value(self):
        field = APIField(value="Bearer token")
        self.assertEqual(field.value, "Bearer token")
        self.assertIsNone(field.description)

    def test_only_description(self):
        field = APIField(description="Auth token")
        self.assertIsNone(field.value)
        self.assertEqual(field.description, "Auth token")

    def test_neither_value_nor_description(self):
        with self.assertRaises(ValidationError) as context:
            APIField()
        self.assertIn("At least one of 'value' or 'description' must be provided", str(context.exception))

if __name__ == '__main__':
    unittest.main()
