import boto3
from settings import Settings


if __name__ == "__main__":
    setting = Settings(_env_file='config/env')
    print(setting)
    sts_client = boto3.client('sts')

    assumed_role_object = sts_client.assume_role(
        RoleArn=setting.role,
        RoleSessionName=setting.session_name,
    )

    credentials = assumed_role_object['Credentials']
    for k in credentials:
        print(k, credentials[k])
