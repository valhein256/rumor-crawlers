from pydantic import BaseSettings


class Settings(BaseSettings):
    region: str
    role: str
    session_name: str

    class Config:
        case_sensitive = True
        env_file_encoding = 'utf-8'
        fields = {
            'region': {'env': 'REGION'},
            'role': {'env': 'ROLE'},
            'session_name': {'env': 'SESSION_NAME'},
        }
