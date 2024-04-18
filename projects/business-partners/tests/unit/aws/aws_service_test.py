import unittest
from unittest import mock
from unittest.mock import MagicMock, patch
from app.aws.aws_service import S3, AWSClient

from app.config.settings import Config
from app.exceptions.exceptions import AWSException


class TestS3(unittest.TestCase):
    def setUp(self):
        mock_session = MagicMock()
        self.mock_client = MagicMock()
        self.mock_session = mock_session
        mock_session.client.return_value = self.mock_client
        self.s3 = S3(self.mock_session)

    @patch("builtins.open")
    def test_upload_file_success(self, mock_open):
        self.mock_client.put_object.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        mock_open.return_value = "file_content"

        file_path = "test_file_path"
        bucket_name = "test_bucket_name"
        key = "test_key"

        response = self.s3.upload_file(file_path, bucket_name, key)

        self.assertEqual(response, f"https://{bucket_name}.s3.{Config.AWS_REGION}.amazonaws.com/{key}")
        self.mock_client.put_object.assert_called_once_with(
            Body="file_content",
            Bucket=bucket_name,
            Key=key,
        )

    @patch("builtins.open")
    def test_upload_file_failure(self, mock_open):
        self.mock_client.put_object.return_value = {"ResponseMetadata": {"HTTPStatusCode": 500}}

        mock_open.return_value = "file_content"

        file_path = "test_file_path"
        bucket_name = "test_bucket_name"
        key = "test_key"

        with self.assertRaises(AWSException) as e:
            self.s3.upload_file(file_path, bucket_name, key)

        self.assertEqual(str(e.exception), f"Error uploading file to S3: {self.mock_client.put_object.return_value['ResponseMetadata']}")
        self.mock_client.put_object.assert_called_once_with(
            Body="file_content",
            Bucket=bucket_name,
            Key=key,
        )


class TestAWSClient(unittest.TestCase):
    def test_aws_client_initialization(self):
        aws_client = AWSClient()
        self.assertIsNotNone(aws_client.s3)
        self.assertIsInstance(aws_client.s3, S3)
