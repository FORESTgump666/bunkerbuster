"""
Configuration Management

Centralized configuration for all BunkerBuster services
"""

import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

load_dotenv()

@dataclass
class DatabaseConfig:
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', '5432'))
    name: str = os.getenv('DB_NAME', 'bunkerbuster')
    user: str = os.getenv('DB_USER', 'postgres')
    password: str = os.getenv('DB_PASSWORD', 'postgres')
    pool_size: int = int(os.getenv('DB_POOL_SIZE', '20'))
    
    @property
    def connection_string(self) -> str:
        return f'postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'

@dataclass
class RedisConfig:
    host: str = os.getenv('REDIS_HOST', 'localhost')
    port: int = int(os.getenv('REDIS_PORT', '6379'))
    password: Optional[str] = os.getenv('REDIS_PASSWORD')
    db: int = int(os.getenv('REDIS_DB', '0'))
    
    @property
    def connection_string(self) -> str:
        auth = f':{self.password}@' if self.password else ''
        return f'redis://{auth}{self.host}:{self.port}/{self.db}'

@dataclass
class APIConfig:
    adsb_url: str = os.getenv('ADSB_API_URL', 'https://api.adsb.one')
    celestrak_url: str = 'https://celestrak.org/NORAD/elements/active.txt'
    opensky_user: str = os.getenv('OPENSKY_USER', '')
    opensky_pass: str = os.getenv('OPENSKY_PASS', '')
    nasa_api_key: str = os.getenv('NASA_API_KEY', '')
    
    # Poll intervals (seconds)
    adsb_interval: int = 10
    satellite_interval: int = 300
    news_interval: int = 600

@dataclass
class AppConfig:
    debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    timezone: str = 'UTC'
    
    db: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    api: APIConfig = APIConfig()

# Global config instance
config = AppConfig()

def get_config() -> AppConfig:
    """Get global configuration"""
    return config
