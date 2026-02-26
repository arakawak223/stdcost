from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://stdcost:stdcost_dev@db:5432/stdcost"
    database_url_sync: str = "postgresql+psycopg2://stdcost:stdcost_dev@db:5432/stdcost"
    secret_key: str = "dev-secret-key"
    anthropic_api_key: str = ""
    app_name: str = "StdCost - 標準原価計算システム"
    debug: bool = True

    model_config = {"env_file": ".env"}


settings = Settings()
