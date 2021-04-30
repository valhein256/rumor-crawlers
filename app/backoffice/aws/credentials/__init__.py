import boto3


def gen_sts_credentials(setting):
    sts_client = boto3.client('sts')

    assumed_role_object = sts_client.assume_role(
        RoleArn=setting.role,
        RoleSessionName=setting.session_name,
    )

    credentials = assumed_role_object['Credentials']
    return credentials
