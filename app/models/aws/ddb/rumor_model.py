from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute, ListAttribute
from utils.settings import Settings
from backoffice.aws.credentials import gen_sts_credentials


setting = Settings(_env_file='config/env')


class SourceCreateDateIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'source-create_date-index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()
    source = UnicodeAttribute(hash_key=True)
    create_date = UnicodeAttribute(range_key=True)


class RumorModel(Model):
    class Meta:
        region = setting.region if setting.region else 'ap-northeast-1'
        table_name = setting.rumor_ddb_table if setting.rumor_ddb_table else 'stg-rumor_source'
        if setting.role:
            credentials = gen_sts_credentials(setting)
            aws_access_key_id = credentials["AccessKeyId"]
            aws_secret_access_key = credentials["SecretAccessKey"]
            aws_session_token = credentials["SessionToken"]

    id = UnicodeAttribute(hash_key=True)
    clarification = UnicodeAttribute(null=True)
    preface = UnicodeAttribute(null=True)
    create_date = UnicodeAttribute(null=True)
    link = UnicodeAttribute(null=True)
    rumors = ListAttribute(null=True)
    source = UnicodeAttribute(null=True)
    title = UnicodeAttribute(null=True)
    original_title = UnicodeAttribute(null=True)
    image_link = UnicodeAttribute(null=True)
    tags = UnicodeAttribute(null=True)
    sensitive_categories = UnicodeAttribute(null=True)
    rating = UnicodeAttribute(null=True)

    source_create_date_index = SourceCreateDateIndex()
