from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Roamly API"
    app_version: str = "0.1.0"
    roamly_env: str = Field(default="development", alias="ROAMLY_ENV")
    
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    # CORS origins: accept either JSON list string or Python list
    api_cors_origins: Union[List[str], str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8081",
            "exp://localhost:8081",
        ],
        alias="API_CORS_ORIGINS",
    )

    @field_validator("api_cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    database_url: str = Field(
        default="sqlite+aiosqlite:///./roamly_dev.db",
        alias="DATABASE_URL",
    )

    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_anon_key: str = Field(default="", alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")
    supabase_jwt_secret: str = Field(default="", alias="SUPABASE_JWT_SECRET")
    jwt_audience: str = Field(default="authenticated", alias="JWT_AUDIENCE")
    jwt_algorithms: List[str] = Field(default=["HS256", "RS256", "ES256"], alias="JWT_ALGORITHMS")
    jwt_verify_exp: bool = Field(default=True, alias="JWT_VERIFY_EXP")
    jwt_verify_iss: bool = Field(default=True, alias="JWT_VERIFY_ISS")

    provider_mode: str = Field(default="mock", alias="PROVIDER_MODE")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")


settings = Settings()
