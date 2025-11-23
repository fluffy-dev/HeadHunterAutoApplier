from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration for the Redis client, read from environment variables.
    """
    redis_host: str = Field("localhost", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")


    def redis_url(self, queue_num: int = 0) -> RedisDsn | str:
        """
        function to get redis url from environment variables.

        Args:
            queue_num (int): redis queue number, default 0

        Returns:
             Redis url in string format
        """
        return f"redis://{self.redis_host}:{self.redis_port}/{queue_num}"

settings = Settings()