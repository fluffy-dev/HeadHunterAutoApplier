from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    host: str = Field("0.0.0.0", alias="APP_HOST")
    port: int = Field(8000, alias="APP_PORT")
    debug: bool = Field(default=True, alias="APP_DEBUG")
    version: str = Field("1.0.0", alias="APP_VERSION")
    hooks_enabled: bool = Field(default=True, alias="APP_HOOKS_ENABLED")
    root_path: str = Field(default="", alias="APP_ROOT_PATH")
    timezone_shift: int = Field(default=3, alias="APP_TIMEZONE_SHIFT")


settings = Settings()
