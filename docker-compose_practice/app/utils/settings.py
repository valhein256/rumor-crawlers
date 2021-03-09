from pydantic import BaseSettings


class Settings(BaseSettings):
    info_log:
        str
    warn_log:
        str
    error_log:
        str
    result_bucket:
        str
    cache_bucket:
        str
    openapi_url:
        str = None
    docs_url:
        str = None
    redoc_url:
        str = None
    isdebug:
        bool = False

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
            'isdebug': {'env': 'APP_DEBUG'}
        }
