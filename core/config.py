"""
Configuration management for Darwin Godel Machine Voice Agent.

This module handles loading configuration from YAML files and environment
variables, with validation and defaults.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Central configuration management class.

    Loads settings from YAML files and environment variables,
    with environment variables taking precedence.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to settings.yaml file
                        (defaults to config/settings.yaml)
        """
        if config_path is None:
            config_path = "config/settings.yaml"

        self.config_path = Path(config_path)
        self._config = self._load_config()
        self._apply_env_overrides()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            print(f"⚠️  Config file not found at {self.config_path}, using defaults")
            return self._get_defaults()

        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                print(f"✅ Loaded config from {self.config_path}")
                return config or {}
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return self._get_defaults()

    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'llm': {
                'provider': 'openai',
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.7,
                'max_tokens': 2000,
                'timeout': 30
            },
            'evolution': {
                'max_generations': 20,
                'success_threshold': 85.0,
                'plateau_generations': 5,
                'variants_per_generation': 3,
                'selection_strategy': 'greedy'
            },
            'simulation': {
                'conversations_per_persona': 3,
                'max_turns': 20,
                'timeout_seconds': 300
            },
            'evaluation': {
                'metrics': {
                    'goal_completion': {'weight': 0.4, 'enabled': True},
                    'conversational_quality': {'weight': 0.3, 'enabled': True},
                    'compliance': {'weight': 0.3, 'enabled': True}
                }
            },
            'logging': {
                'level': 'INFO',
                'format': 'json',
                'save_conversations': True,
                'save_evaluations': True
            },
            'database': {
                'type': 'sqlite',
                'path': 'data/agents.db'
            }
        }

    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        # LLM settings
        if os.getenv('LLM_PROVIDER'):
            self._config['llm']['provider'] = os.getenv('LLM_PROVIDER')
        if os.getenv('LLM_MODEL'):
            self._config['llm']['model'] = os.getenv('LLM_MODEL')
        if os.getenv('LLM_TEMPERATURE'):
            self._config['llm']['temperature'] = float(os.getenv('LLM_TEMPERATURE'))

        # Evolution settings
        if os.getenv('MAX_GENERATIONS'):
            self._config['evolution']['max_generations'] = int(os.getenv('MAX_GENERATIONS'))
        if os.getenv('SUCCESS_THRESHOLD'):
            self._config['evolution']['success_threshold'] = float(os.getenv('SUCCESS_THRESHOLD'))

        # Database settings
        if os.getenv('DATABASE_URL'):
            self._config['database']['url'] = os.getenv('DATABASE_URL')

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key_path: Dot-separated path (e.g., 'llm.model')
            default: Default value if key not found

        Returns:
            Configuration value

        Example:
            >>> config = Config()
            >>> model = config.get('llm.model')
            >>> print(model)  # 'gpt-4-turbo-preview'
        """
        keys = key_path.split('.')
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any):
        """
        Set a configuration value using dot notation.

        Args:
            key_path: Dot-separated path (e.g., 'llm.temperature')
            value: Value to set

        Example:
            >>> config = Config()
            >>> config.set('llm.temperature', 0.9)
        """
        keys = key_path.split('.')
        current = self._config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration with API key."""
        llm_config = self._config.get('llm', {}).copy()

        # Add API key from environment
        provider = llm_config.get('provider', 'openai')
        if provider == 'openai':
            llm_config['api_key'] = os.getenv('OPENAI_API_KEY')
        elif provider == 'anthropic':
            llm_config['api_key'] = os.getenv('ANTHROPIC_API_KEY')

        return llm_config

    def get_database_url(self) -> str:
        """Get database connection URL."""
        db_config = self._config.get('database', {})

        # Check for explicit URL first
        if 'url' in db_config:
            return db_config['url']

        # Otherwise construct from type and path
        db_type = db_config.get('type', 'sqlite')
        db_path = db_config.get('path', 'data/agents.db')

        if db_type == 'sqlite':
            return f"sqlite:///{db_path}"
        else:
            return os.getenv('DATABASE_URL', f"sqlite:///{db_path}")

    def validate(self) -> bool:
        """
        Validate configuration.

        Returns:
            True if configuration is valid
        """
        required_keys = [
            'llm.provider',
            'llm.model',
            'evolution.max_generations',
            'evolution.success_threshold'
        ]

        for key in required_keys:
            if self.get(key) is None:
                print(f"❌ Missing required config: {key}")
                return False

        # Check API keys
        provider = self.get('llm.provider')
        if provider == 'openai' and not os.getenv('OPENAI_API_KEY'):
            print("❌ OPENAI_API_KEY environment variable not set")
            return False
        elif provider == 'anthropic' and not os.getenv('ANTHROPIC_API_KEY'):
            print("❌ ANTHROPIC_API_KEY environment variable not set")
            return False

        print("✅ Configuration validated")
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._config.copy()

    def __repr__(self):
        """String representation."""
        return f"<Config(provider={self.get('llm.provider')}, model={self.get('llm.model')})>"


# Global config instance (lazy-loaded)
_global_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Get the global configuration instance.

    Args:
        config_path: Optional path to config file

    Returns:
        Config instance
    """
    global _global_config
    if _global_config is None:
        _global_config = Config(config_path)
    return _global_config


def reset_config():
    """Reset the global configuration instance."""
    global _global_config
    _global_config = None
