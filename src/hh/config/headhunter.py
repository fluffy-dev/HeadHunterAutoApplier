from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    client_id: str = Field(..., alias="HH_CLIENT_ID")
    client_secret: str = Field(..., alias="HH_CLIENT_SECRET")
    redirect_uri: str = Field(..., alias="HH_REDIRECT_URI")

    # URL to redirect user for login
    auth_url: str = "https://hh.ru/oauth/authorize"
    token_url: str = "https://hh.ru/oauth/token"


settings = Settings()