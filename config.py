from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    android_gateway_url: str = "http://localhost:8081"
    android_gateway_user: str = "admin"
    android_gateway_pass: str = "secret"
    android_gateway_port: int = 8081  # ADB forward port

    api_host: str = "0.0.0.0"
    api_port: int = 8080
    api_key: str = "change-me-to-random-string"

    model_config = {"env_file": ".env"}


settings = Settings()
