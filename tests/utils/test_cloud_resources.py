import boto3
from botocore.stub import Stubber

from scout.utils.cloud_resources import amazon_s3_url

MOCK_CREDENTIALS = {
    "region" : "eu-north-1",
    "key": "mock_key",
    "secret_key" : "mock_secret_access_key",
    "bucket": "mock_bucket_name",
    "folder": "mock_folder"
}

def test_amazon_s3_url(monkeypatch):
    """Test function that returns a presigned url to an Amazon S3 resource"""

    # Having some track file on an Amazon S3 bucket
    key = "CosmicCodingMuts_v90_hg38.vcf.gz"

    client = boto3.client('s3')
    stubber = Stubber(client)

    with stubber:
        # WHEN the function to retrieve a presigned url is involked with credentials
        url = amazon_s3_url(MOCK_CREDENTIALS, key)
        region = MOCK_CREDENTIALS["region"]
        bucket = MOCK_CREDENTIALS["bucket"]
        folder = MOCK_CREDENTIALS["folder"]

        # THEN it should return a well formatted link to the file in the cloud
        assert f'https://s3.{region}.amazonaws.com/{bucket}/{folder}/{key}' in url
