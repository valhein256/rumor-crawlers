import boto3
import sys
import os
from pydantic import BaseSettings

_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_path, '../app'))
CONFIG_ROLE_FILE = "config/role"


class RoleSettings(BaseSettings):
    role: str
    session_name: str
    config_s3_bucket_name: str
    config_key: str
    config_filename: str

    class Config:
        case_sensitive = True
        env_file_encoding = 'utf-8'
        fields = {
            'role': {'env': 'ROLE'},
            'session_name': {'env': 'SESSION_NAME'},
            'config_s3_bucket_name': {'env': 'CONFIG_S3_BUCKET_NAME'},
            'config_key': {'env': 'CONFIG_KEY'},
            'config_filename': {'env': 'CONFIG_FILENAME'},
        }


if __name__ == "__main__":
    from backoffice.aws.credentials import gen_sts_credentials

    print("Download config file via aws-assumerole...")
    setting = RoleSettings(_env_file=CONFIG_ROLE_FILE)
    credentials = gen_sts_credentials(setting)

    s3_client = boto3.client(
        's3',
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"]
    )

    with open(setting.config_filename, 'wb') as f:
        s3_client.download_fileobj(setting.config_s3_bucket_name,
                                   setting.config_key,
                                   f)
    print("Download config/env from s3.")
