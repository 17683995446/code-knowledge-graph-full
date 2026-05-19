"""
Utility functions and helpers
"""
import time
import hashlib
from typing import Any, Dict, Optional
from datetime import datetime


class Logger:
    """Simple logger class"""
    def __init__(self, name: str):
        self.name = name
    
    def _log(self, level: str, message: str):
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [{level}] [{self.name}] {message}")
    
    def info(self, message: str):
        self._log("INFO", message)
    
    def warning(self, message: str):
        self._log("WARNING", message)
    
    def error(self, message: str):
        self._log("ERROR", message)
    
    def debug(self, message: str):
        self._log("DEBUG", message)


class Cache:
    """Simple in-memory cache"""
    def __init__(self, ttl: int = 300):
        self._cache: Dict[str, Any] = {}
        self._ttl = ttl
        self._timestamps: Dict[str, float] = {}
        self._logger = Logger("Cache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            if time.time() - self._timestamps[key] < self._ttl:
                return self._cache[key]
            else:
                self.delete(key)
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache"""
        self._cache[key] = value
        self._timestamps[key] = time.time()
        self._logger.debug(f"Cached: {key}")
    
    def delete(self, key: str):
        """Delete value from cache"""
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]
            self._logger.debug(f"Deleted cache: {key}")
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._timestamps.clear()
        self._logger.info("Cache cleared")


class Config:
    """Configuration management"""
    _config: Dict[str, Any] = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "mydb"
        },
        "cache": {
            "ttl": 300
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000
        }
    }
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split(".")
        value = cls._config
        for k in keys:
            if k in value:
                value = value[k]
            else:
                return default
        return value
    
    @classmethod
    def set(cls, key: str, value: Any):
        """Set configuration value"""
        keys = key.split(".")
        current = cls._config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value


def generate_id() -> str:
    """Generate unique ID"""
    return hashlib.md5(str(time.time()).encode()).hexdigest()


def validate_email(email: str) -> bool:
    """Validate email format"""
    if "@" not in email:
        return False
    domain = email.split("@")[1]
    if "." not in domain:
        return False
    return True


def format_price(price: float) -> str:
    """Format price as currency"""
    return f"${price:.2f}"
