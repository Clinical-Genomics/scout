import boto3
from botocore.config import Config


def s3_resource_url(credentials, key):
    """Returns an url to download a resource from a cloud storage bucket

    Accepts:
        credentials(list): [
            endpoint(str): i.e. https://s3.eu-west-1.amazonaws.com,
            access_key(str): cos_hmac_keys.access_key_id,
            secret_access_key(str): cos_hmac_keys.secret_access_key,
            bucket(str): name of bucket
        ],
        key(str): name of file to download

    Returns:
        url(str): presigned url for downloading the file
    """

    s3_client = boto3.client(
        "s3",
        region_name=credentials[0],
        aws_access_key_id=credentials[1],
        aws_secret_access_key=credentials[2],
        config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"),
    )

    url = s3_client.generate_presigned_url(
        "get_object", Params={"Bucket": credentials[3], "Key": key}, ExpiresIn=500
    )

    return url
