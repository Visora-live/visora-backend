from app.core.config import settings


class S3StoragePlaceholder:
    """
    Placeholder for AWS S3 storage.
    boto3 is NOT installed. AWS credentials are NOT configured.
    This class will be activated when STORAGE_PROVIDER=s3 and AWS is ready.
    """

    def __init__(self):
        self.region = settings.AWS_REGION
        self.bucket = settings.AWS_S3_BUCKET

    def upload_placeholder(self, key: str, data: bytes) -> dict:
        # Not implemented — requires boto3 and valid AWS credentials
        return {
            "provider": "s3",
            "bucket": self.bucket,
            "key": key,
            "region": self.region,
            "status": "not_implemented",
            "note": "boto3 not installed. AWS integration pending.",
        }
