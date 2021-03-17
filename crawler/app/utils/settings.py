from pydantic import BaseSettings


class Settings(BaseSettings):
    info_log: str
    warn_log: str
    error_log: str
    result_bucket: str
    cache_bucket: str
    openapi_url: str = None
    docs_url: str = None
    redoc_url: str = None
    isdebug: bool = False
    proxycrawl_token: str
    proxycrawl_device: str
    proxycrawl_country: str
    proxycrawl_api_url: str
    proxycrawl_enabled_for_instagram: bool = False
    proxycrawl_enabled_for_facebook: bool = False
    proxycrawl_enabled_for_surveycake: bool = False
    proxycrawl_enabled_for_twitter: bool = False
    youtube_api_key: str
    youtube_api_url: str

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
            'info_log': {'env': 'APP_LOG_INFO'},
            'warn_log': {'env': 'APP_LOG_WARN'},
            'error_log': {'env': 'APP_LOG_ERROR'},
            'result_bucket': {'env': 'APP_SR_CACHE_LOC'},
            'cache_bucket': {'env': 'APP_CACHE_LOC'},
            'openapi_url': {'env': 'APP_OPENAPI_SCHEMA'},
            'docs_url': {'env': 'APP_SWAGGER'},
            'redoc_url': {'env': 'APP_REDOC'},
            'isdebug': {'env': 'APP_DEBUG'},
            'proxycrawl_token': {'env': 'PROXYCRAWL_TOKEN'},
            'proxycrawl_device': {'env': 'PROXYCRAWL_DEVICE'},
            'proxycrawl_country': {'env': 'PROXYCRAWL_COUNTRY'},
            'proxycrawl_api_url': {'env': 'PROXYCRAWL_API_URL'},
            'proxycrawl_enabled_for_instagram': {'env': 'PROXYCRAWL_ENABLED_FOR_INSTAGRAM'},
            'proxycrawl_enabled_for_facebook': {'env': 'PROXYCRAWL_ENABLED_FOR_FACEBOOK'},
            'proxycrawl_enabled_for_surveycake': {'env': 'PROXYCRAWL_ENABLED_FOR_SURVEYCAKE'},
            'proxycrawl_enabled_for_twitter': {'env': 'PROXYCRAWL_ENABLED_FOR_TWITTER'},
            'proxycrawl_api_url': {'env': 'PROXYCRAWL_API_URL'},
            'proxycrawl_api_url': {'env': 'PROXYCRAWL_API_URL'},
            'proxycrawl_api_url': {'env': 'PROXYCRAWL_API_URL'},
            'proxycrawl_api_url': {'env': 'PROXYCRAWL_API_URL'},
            'youtube_api_key': {'env': 'YOUTUBE_API_KEY'},
            'youtube_api_url': {'env': 'YOUTUBE_API_URL'}
        }
