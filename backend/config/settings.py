"""
Configuration Management Service

Handles encrypted storage and retrieval of application configuration.
Provides runtime decryption of sensitive settings.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    jwt_secret: str
    api_key: str
    api_secret: str
    session_timeout: int = 30  # minutes
    rate_limit: int = 60  # requests per minute
    max_file_size: int = 10 * 1024 * 1024  # 10MB


@dataclass
class ClaudeConfig:
    """Claude API configuration"""
    api_key: str
    base_url: str = "https://api.anthropic.com"
    timeout: int = 30


@dataclass
class AppConfig:
    """Complete application configuration"""
    database: DatabaseConfig
    security: SecurityConfig
    claude: ClaudeConfig
    environment: str = "development"
    log_level: str = "INFO"
    frontend_url: str = "http://localhost:3000"


class ConfigurationError(Exception):
    """Raised when configuration cannot be loaded or decrypted"""
    pass


class ConfigManager:
    """
    Secure configuration manager with encrypted storage.
    
    Handles:
    - Loading encryption keys
    - Decrypting configuration files
    - Providing typed configuration objects
    - Environment variable overrides
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path(__file__).parent
        self.key_file = self.config_dir / "encryption.key"
        self.config_file = self.config_dir / "config.enc"
        self._config: Optional[AppConfig] = None
        self._fernet: Optional[Fernet] = None
        
    def _load_encryption_key(self) -> Fernet:
        """Load and validate encryption key"""
        if not self.key_file.exists():
            raise ConfigurationError(
                f"Encryption key not found at {self.key_file}. "
                "Run setup.py to initialize configuration."
            )
        
        try:
            with open(self.key_file, 'rb') as f:
                key = f.read()
            return Fernet(key)
        except Exception as e:
            raise ConfigurationError(f"Failed to load encryption key: {e}")
    
    def _decrypt_config(self) -> Dict[str, Any]:
        """Decrypt and parse configuration file"""
        if not self.config_file.exists():
            raise ConfigurationError(
                f"Configuration file not found at {self.config_file}. "
                "Run setup.py to initialize configuration."
            )
        
        if not self._fernet:
            self._fernet = self._load_encryption_key()
        
        try:
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            raise ConfigurationError(f"Failed to decrypt configuration: {e}")
    
    def _apply_env_overrides(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides"""
        env_mappings = {
            'CLAUDE_API_KEY': ['claude_api_key'],
            'DATABASE_URL': ['database_url'],
            'JWT_SECRET': ['jwt_secret'],
            'API_KEY': ['api_key'],
            'API_SECRET': ['api_secret'],
            'SESSION_TIMEOUT': ['session_timeout'],
            'MAX_FILE_SIZE': ['max_file_size'],
            'RATE_LIMIT': ['rate_limit'],
            'ENVIRONMENT': ['environment'],
            'LOG_LEVEL': ['log_level'],
            'FRONTEND_URL': ['frontend_url'],
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                # Handle nested configuration paths if needed
                current = config_dict
                for key in config_path[:-1]:
                    current = current.setdefault(key, {})
                
                # Type conversion for numeric values
                final_key = config_path[-1]
                if final_key in ['session_timeout', 'max_file_size', 'rate_limit']:
                    try:
                        env_value = int(env_value)
                    except ValueError:
                        logger.warning(f"Invalid numeric value for {env_var}: {env_value}")
                        continue
                
                current[final_key] = env_value
                logger.info(f"Applied environment override for {env_var}")
        
        return config_dict
    
    def _create_config_objects(self, config_dict: Dict[str, Any]) -> AppConfig:
        """Create typed configuration objects from dictionary"""
        try:
            database_config = DatabaseConfig(
                url=config_dict['database_url'],
                echo=config_dict.get('database_echo', False),
                pool_size=config_dict.get('database_pool_size', 5),
                max_overflow=config_dict.get('database_max_overflow', 10)
            )
            
            security_config = SecurityConfig(
                jwt_secret=config_dict['jwt_secret'],
                api_key=config_dict['api_key'],
                api_secret=config_dict['api_secret'],
                session_timeout=config_dict.get('session_timeout', 30),
                rate_limit=config_dict.get('rate_limit', 60),
                max_file_size=config_dict.get('max_file_size', 10 * 1024 * 1024)
            )
            
            claude_config = ClaudeConfig(
                api_key=config_dict['claude_api_key'],
                base_url=config_dict.get('claude_base_url', "https://api.anthropic.com"),
                timeout=config_dict.get('claude_timeout', 30)
            )
            
            return AppConfig(
                database=database_config,
                security=security_config,
                claude=claude_config,
                environment=config_dict.get('environment', 'development'),
                log_level=config_dict.get('log_level', 'INFO'),
                frontend_url=config_dict.get('frontend_url', 'http://localhost:3000')
            )
        except KeyError as e:
            raise ConfigurationError(f"Missing required configuration key: {e}")
    
    def load_config(self) -> AppConfig:
        """
        Load and return complete application configuration.
        
        Returns:
            AppConfig: Typed configuration object
            
        Raises:
            ConfigurationError: If configuration cannot be loaded
        """
        if self._config is not None:
            return self._config
        
        logger.info("Loading application configuration")
        
        # Decrypt configuration
        config_dict = self._decrypt_config()
        
        # Apply environment variable overrides
        config_dict = self._apply_env_overrides(config_dict)
        
        # Create typed configuration objects
        self._config = self._create_config_objects(config_dict)
        
        logger.info(f"Configuration loaded successfully for environment: {self._config.environment}")
        return self._config
    
    def get_config(self) -> AppConfig:
        """Get cached configuration or load if not cached"""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def reload_config(self) -> AppConfig:
        """Force reload configuration from encrypted file"""
        self._config = None
        self._fernet = None
        return self.load_config()
    
    def validate_config(self) -> bool:
        """
        Validate that all required configuration is present and valid.
        
        Returns:
            bool: True if configuration is valid
        """
        try:
            config = self.get_config()
            
            # Validate required fields are not empty
            required_checks = [
                (config.claude.api_key, "Claude API key"),
                (config.security.jwt_secret, "JWT secret"),
                (config.security.api_key, "API key"),
                (config.security.api_secret, "API secret"),
                (config.database.url, "Database URL"),
            ]
            
            for value, name in required_checks:
                if not value or len(str(value).strip()) == 0:
                    logger.error(f"Invalid or missing {name}")
                    return False
            
            # Validate numeric ranges
            if config.security.session_timeout <= 0:
                logger.error("Session timeout must be positive")
                return False
            
            if config.security.rate_limit <= 0:
                logger.error("Rate limit must be positive")
                return False
            
            if config.security.max_file_size <= 0:
                logger.error("Max file size must be positive")
                return False
            
            logger.info("Configuration validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get or create global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AppConfig:
    """Convenience function to get application configuration"""
    return get_config_manager().get_config()


def reload_config() -> AppConfig:
    """Convenience function to reload application configuration"""
    return get_config_manager().reload_config()


def validate_config() -> bool:
    """Convenience function to validate application configuration"""
    return get_config_manager().validate_config()