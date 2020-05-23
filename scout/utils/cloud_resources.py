import boto3
from botocore.config import Config


def amazon_s3_url(credentials, key):
    """Returns an url to download a resource from a cloud storage bucket

    Accepts:
        credentials(dict): {
            region(str): i.e. "eu-north-1",
            key(str): cos_hmac_keys.access_key_id,
            secret_key(str): cos_hmac_keys.secret_access_key,
            bucket(str): name of bucket
            folder(str): folder where files are stored (can be None)
        },
        key(str): name of file to download

    Returns:
        url(str): presigned url for downloading the file
    """

    s3_client = boto3.client(
        "s3",
        region_name=credentials["region"],
        aws_access_key_id=credentials["key"],
        aws_secret_access_key=credentials["secret_key"],
        config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"),
    )

    # if file is inside a bucket folder include folder name in the key path
    if credentials["folder"] is not None:
        key = "/".join([credentials["folder"], key])

    url = s3_client.generate_presigned_url(
        "get_object", Params={"Bucket": credentials["bucket"], "Key": key}, ExpiresIn=500,
    )

    return url
