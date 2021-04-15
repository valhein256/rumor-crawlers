from pydantic import BaseSettings


class Settings(BaseSettings):
    region: str
    info_log: str
    warn_log: str
    error_log: str
    isdebug: bool = False
    proxycrawl_token: str
    proxycrawl_device: str
    proxycrawl_country: str
    proxycrawl_api_url: str
    proxycrawl_enabled_for_instagram: bool = False
    proxycrawl_enabled_for_facebook: bool = False
    proxycrawl_enabled_for_surveycake: bool = False
    proxycrawl_enabled_for_twitter: bool = False

    rumor_ddb_table: str
    fda_page_url: str
    fda_rumor_url: str
    fda_source: str
    cdc_page_url: str
    cdc_domain: str
    cdc_source: str
    mofa_page_url: str
    mofa_domain: str
    mofa_source: str
    tfc_page_url: str
    tfc_domain: str
    tfc_source: str
    mygopen_api: str
    mygopen_max_results: int
    mygopen_number: int
    mygopen_domain: str
    mygopen_source: str

    # @validator('sr_engine')
    # def google_credential_exists(cls, v, values):
    #     if v.startswith('recognition_api.engines.google.'):
    #         if 'engine_credential' not in values or values['engine_credential'] is None:
    #             raise ValidationError('Missing Google credential location.')
    #     return v

    class Config:
        case_sensitive = True
        env_file_encoding = 'utf-8'
        fields = {
            'region': {'env': 'REGION'},
            'info_log': {'env': 'APP_LOG_INFO'},
            'warn_log': {'env': 'APP_LOG_WARN'},
            'error_log': {'env': 'APP_LOG_ERROR'},
            'isdebug': {'env': 'APP_DEBUG'},
            'proxycrawl_token': {'env': 'PROXYCRAWL_TOKEN'},
            'proxycrawl_device': {'env': 'PROXYCRAWL_DEVICE'},
            'proxycrawl_country': {'env': 'PROXYCRAWL_COUNTRY'},
            'proxycrawl_api_url': {'env': 'PROXYCRAWL_API_URL'},
            'proxycrawl_enabled_for_instagram': {'env': 'PROXYCRAWL_ENABLED_FOR_INSTAGRAM'},
            'proxycrawl_enabled_for_facebook': {'env': 'PROXYCRAWL_ENABLED_FOR_FACEBOOK'},
            'proxycrawl_enabled_for_surveycake': {'env': 'PROXYCRAWL_ENABLED_FOR_SURVEYCAKE'},
            'proxycrawl_enabled_for_twitter': {'env': 'PROXYCRAWL_ENABLED_FOR_TWITTER'},
            'rumor_ddb_table': {'env': 'RUMOR_DDB_TABLE'},
            'fda_page_url': {'env': 'FDA_PAGE_URL'},
            'fda_rumor_url': {'env': 'FDA_RUMOR_URL'},
            'fda_source': {'env': 'FDA_SOURCE'},
            'cdc_page_url': {'env': 'CDC_PAGE_URL'},
            'cdc_domain': {'env': 'CDC_DOMAIN'},
            'cdc_source': {'env': 'CDC_SOURCE'},
            'mofa_page_url': {'env': 'MOFA_PAGE_URL'},
            'mofa_domain': {'env': 'MOFA_DOMAIN'},
            'mofa_source': {'env': 'MOFA_SOURCE'},
            'tfc_page_url': {'env': 'TFC_PAGE_URL'},
            'tfc_domain': {'env': 'TFC_DOMAIN'},
            'tfc_source': {'env': 'TFC_SOURCE'},
            'mygopen_api': {'env': 'MYGOPEN_API'},
            'mygopen_max_results': {'env': 'MYGOPEN_MAX_RESULTS'},
            'mygopen_number': {'env': 'MYGOPEN_NUMBER'},
            'mygopen_domain': {'env': 'MYGOPEN_DOMAIN'},
            'mygopen_source': {'env': 'MYGOPEN_SOURCE'},
        }
