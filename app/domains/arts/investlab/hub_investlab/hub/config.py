"""
Configuration management for the Data Hub
"""

import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management class"""
    
    # API Keys and Secrets
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    
    AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
    AZURE_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
    AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID')
    
    # Data Hub Settings
    FETCH_INTERVAL_MINUTES = int(os.getenv('FETCH_INTERVAL_MINUTES', 60))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', 5000))
    DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', 30))
    
    # Notification Settings
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', 587))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    # Data Sources Configuration
    DATA_SOURCES = {
        'microsoft': {
            'enabled': True,
            'endpoints': {
                'azure_status': 'https://status.azure.com/en-us/status',
                'microsoft_blog': 'https://blogs.microsoft.com/feed/',
                'github_microsoft': 'https://api.github.com/orgs/microsoft',
                'office365_status': 'https://status.office365.com/api/v2.0/status'
            }
        },
        'google': {
            'enabled': True,
            'endpoints': {
                'google_cloud_status': 'https://status.cloud.google.com',
                'google_blog': 'https://blog.google/feeds/posts/default',
                'android_blog': 'https://android-developers.googleblog.com/feeds/posts/default',
                'workspace_status': 'https://www.google.com/appsstatus/json/en'
            }
        },
        'x': {
            'enabled': True,
            'endpoints': {
                'trending_topics': 'https://trends24.in/united-states/',
                'twitter_blog': 'https://blog.twitter.com/feed',
                'x_updates': 'https://x.com/en/what-is-happening'
            },
            'api_enabled': bool(TWITTER_BEARER_TOKEN)
        }
    }
    
    # Cache Settings
    CACHE_SETTINGS = {
        'enabled': True,
        'ttl_minutes': 30,
        'max_entries': 1000
    }
    
    # Rate Limiting
    RATE_LIMITS = {
        'requests_per_minute': 60,
        'requests_per_hour': 1000,
        'retry_attempts': 3,
        'retry_delay_seconds': 5
    }
    
    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """Get a summary of current configuration"""
        return {
            'data_sources': {
                source: {
                    'enabled': config['enabled'],
                    'api_enabled': config.get('api_enabled', True)
                }
                for source, config in cls.DATA_SOURCES.items()
            },
            'fetch_interval_minutes': cls.FETCH_INTERVAL_MINUTES,
            'dashboard_port': cls.DASHBOARD_PORT,
            'data_retention_days': cls.DATA_RETENTION_DAYS,
            'cache_enabled': cls.CACHE_SETTINGS['enabled'],
            'log_level': cls.LOG_LEVEL
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return any issues"""
        issues = []
        warnings = []
        
        # Check API keys
        if not cls.TWITTER_BEARER_TOKEN:
            warnings.append("Twitter Bearer Token not provided - API features disabled")
        
        if not cls.GOOGLE_API_KEY:
            warnings.append("Google API Key not provided - Some features may be limited")
        
        if not cls.AZURE_CLIENT_ID:
            warnings.append("Azure Client ID not provided - Azure features may be limited")
        
        # Check critical settings
        if cls.FETCH_INTERVAL_MINUTES < 5:
            issues.append("Fetch interval too low - may hit rate limits")
        
        if cls.DASHBOARD_PORT < 1024:
            issues.append("Dashboard port below 1024 - may require admin privileges")
        
        return {
            'issues': issues,
            'warnings': warnings,
            'is_valid': len(issues) == 0
        }
    
    @classmethod
    def save_config_to_file(cls, filename: str = 'config.json'):
        """Save current configuration to JSON file"""
        config_data = {
            'data_sources': cls.DATA_SOURCES,
            'fetch_interval_minutes': cls.FETCH_INTERVAL_MINUTES,
            'log_level': cls.LOG_LEVEL,
            'dashboard_port': cls.DASHBOARD_PORT,
            'data_retention_days': cls.DATA_RETENTION_DAYS,
            'cache_settings': cls.CACHE_SETTINGS,
            'rate_limits': cls.RATE_LIMITS
        }
        
        with open(filename, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        return filename
    
    @classmethod
    def load_config_from_file(cls, filename: str = 'config.json'):
        """Load configuration from JSON file"""
        try:
            with open(filename, 'r') as f:
                config_data = json.load(f)
            
            # Update class variables
            for key, value in config_data.items():
                if hasattr(cls, key.upper()):
                    setattr(cls, key.upper(), value)
            
            return True
            
        except FileNotFoundError:
            return False
        except json.JSONDecodeError:
            return False
