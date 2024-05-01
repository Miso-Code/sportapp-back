import unittest
from unittest.mock import MagicMock
from fastapi import Request
from fastapi.exceptions import HTTPException

from app.middleware.api_key_middleware import api_key_middleware


class TestAPIKeyMiddleware(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_request = MagicMock(spec=Request)

    async def mock_api_key_header(self, request: Request):
        return request.headers.get("X-API-Key")

    async def test_valid_api_key(self):
        self.mock_request.headers = {"X-API-Key": "secret"}
        response = await api_key_middleware(self.mock_request, api_key_header=self.mock_api_key_header)
        self.assertEqual(response, self.mock_request)

    async def test_missing_api_key(self):
        self.mock_request.headers = {}
        with self.assertRaises(HTTPException) as context:
            await api_key_middleware(self.mock_request, api_key_header=self.mock_api_key_header)
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(str(context.exception.detail), "Invalid API key")

    async def test_wrong_api_key(self):
        self.mock_request.headers = {"X-API-Key": "wrong_api_key"}
        with self.assertRaises(HTTPException) as context:
            await api_key_middleware(self.mock_request, api_key_header=self.mock_api_key_header)
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(str(context.exception.detail), "Invalid API key")
