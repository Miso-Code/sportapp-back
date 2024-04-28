import boto3

from app.config.settings import Config
from app.exceptions.exceptions import AWSException


class S3:
    def __init__(self, session):
        self.client = session.client("s3")

    def upload_file(self, file_path, bucket_name, key):
        response = self.client.put_object(
            Body=open(file_path, "rb"),
            Bucket=bucket_name,
            Key=key,
        )

        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise AWSException(f"Error uploading file to S3: {response['ResponseMetadata']}")

        return f"https://{bucket_name}.s3.{Config.AWS_REGION}.amazonaws.com/{key}"


class AWSClient:
    def __init__(self):
        self.session = boto3.Session(
            region_name=Config.AWS_REGION,
        )

        self.s3 = S3(self.session)
