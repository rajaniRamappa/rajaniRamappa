from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    opend_host: str = "127.0.0.1"
    opend_port: int = 11111
    trade_env: str = "REAL"
    default_symbols: List[str] = ["SG.D05", "SG.U11", "SG.C6L"]

    class Config:
        env_file = ".env"


settings = Settings()
