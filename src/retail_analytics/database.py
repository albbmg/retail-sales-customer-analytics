import os
from dataclasses import dataclass

from dotenv import load_dotenv


class DatabaseConfigError(ValueError):
    """Raised when database environment configuration is invalid."""


@dataclass(frozen=True)
class DatabaseSettings:
    database: str
    user: str
    password: str
    host: str
    port: int

    @classmethod
    def from_environment(cls) -> "DatabaseSettings":
        load_dotenv()

        port_value = os.getenv("POSTGRES_PORT", "5432")
        try:
            port = int(port_value)
        except ValueError as exc:
            raise DatabaseConfigError(
                f"POSTGRES_PORT must be an integer, got {port_value!r}"
            ) from exc

        if not 1 <= port <= 65535:
            raise DatabaseConfigError(
                f"POSTGRES_PORT must be between 1 and 65535, got {port}"
            )

        return cls(
            database=os.getenv("POSTGRES_DB", "retail_analytics"),
            user=os.getenv("POSTGRES_USER", "retail_user"),
            password=os.getenv("POSTGRES_PASSWORD", "change-me"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=port,
        )

    def connect_kwargs(self) -> dict[str, str | int]:
        return {
            "dbname": self.database,
            "user": self.user,
            "password": self.password,
            "host": self.host,
            "port": self.port,
        }
