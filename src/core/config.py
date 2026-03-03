from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./src/travel_planner.db"

    @property
    def database_url_async(self) -> str:
        return self.DATABASE_URL

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
