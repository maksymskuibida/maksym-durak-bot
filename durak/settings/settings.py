from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseModel):
    token: str


class MongoSettings(BaseModel):
    uri: str = 'mongodb://localhost:27017'
    database: str = 'durak'


class RedisSettings(BaseModel):
    uri: str = 'redis://localhost:6379/1'
    timeout: int = 62


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter='__')

    bot: BotSettings
    mongo: MongoSettings = MongoSettings()
    redis: RedisSettings = RedisSettings()
