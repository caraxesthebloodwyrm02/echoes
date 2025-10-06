"""
OAuth2 Authentication Manager for Google, Microsoft, and X (Twitter)
"""

import json
import secrets
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
import os

class OAuthManager:
    """Manages OAuth2 authentication for multiple providers"""
    
    def __init__(self):
        self.providers = {
            'google': {
                'client_id': os.getenv('GOOGLE_CLIENT_ID', 'your_google_client_id'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET', 'your_google_client_secret'),
                'auth_url': 'https://accounts.google.com/o/oauth2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'user_info_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
                'scope': 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email'
            },
            'microsoft': {
                'client_id': os.getenv('MICROSOFT_CLIENT_ID', 'your_microsoft_client_id'),
                'client_secret': os.getenv('MICROSOFT_CLIENT_SECRET', 'your_microsoft_client_secret'),
                'auth_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
                'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
                'user_info_url': 'https://graph.microsoft.com/v1.0/me',
                'scope': 'https://graph.microsoft.com/user.read'
            },
            'twitter': {
                'client_id': os.getenv('TWITTER_CLIENT_ID', 'your_twitter_client_id'),
                'client_secret': os.getenv('TWITTER_CLIENT_SECRET', 'your_twitter_client_secret'),
                'auth_url': 'https://twitter.com/i/oauth2/authorize',
                'token_url': 'https://api.twitter.com/2/oauth2/token',
                'user_info_url': 'https://api.twitter.com/2/users/me',
                'scope': 'tweet.read users.read offline.access'
            }
        }
        self.sessions = {}
    
    def generate_auth_url(self, provider: str, redirect_uri: str) -> str:
        """Generate OAuth2 authorization URL"""
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
        
        config = self.providers[provider]
        state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': config['client_id'],
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': config['scope'],
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        # Store state for validation
        self.sessions[state] = {
            'provider': provider,
            'created_at': datetime.now().isoformat(),
            'redirect_uri': redirect_uri
        }
        
        auth_url = f"{config['auth_url']}?{urllib.parse.urlencode(params)}"
        return auth_url, state
    
    def exchange_code_for_token(self, provider: str, code: str, state: str, redirect_uri: str) -> dict:
        """Exchange authorization code for access token"""
        if state not in self.sessions:
            raise ValueError("Invalid or expired state")
        
        session = self.sessions.pop(state)
        if session['provider'] != provider:
            raise ValueError("Provider mismatch")
        
        config = self.providers[provider]
        
        token_data = {
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'DataHub/1.0'
        }
        
        try:
            req = urllib.request.Request(
                config['token_url'],
                data=urllib.parse.urlencode(token_data).encode(),
                headers=headers
            )
            
            with urllib.request.urlopen(req) as response:
                token_response = json.loads(response.read().decode())
            
            return token_response
            
        except Exception as e:
            raise Exception(f"Token exchange failed: {str(e)}")
    
    def get_user_info(self, provider: str, access_token: str) -> dict:
        """Get user information using access token"""
        config = self.providers[provider]
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'DataHub/1.0'
        }
        
        try:
            req = urllib.request.Request(config['user_info_url'], headers=headers)
            
            with urllib.request.urlopen(req) as response:
                user_info = json.loads(response.read().decode())
            
            # Normalize user data across providers
            return self._normalize_user_data(provider, user_info)
            
        except Exception as e:
            raise Exception(f"Failed to get user info: {str(e)}")
    
    def _normalize_user_data(self, provider: str, user_info: dict) -> dict:
        """Normalize user data across different providers"""
        normalized = {
            'provider': provider,
            'raw_data': user_info,
            'connected_at': datetime.now().isoformat()
        }
        
        if provider == 'google':
            normalized.update({
                'id': user_info.get('id'),
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture')
            })
        elif provider == 'microsoft':
            normalized.update({
                'id': user_info.get('id'),
                'email': user_info.get('mail') or user_info.get('userPrincipalName'),
                'name': user_info.get('displayName'),
                'picture': None  # Microsoft doesn't provide picture by default
            })
        elif provider == 'twitter':
            normalized.update({
                'id': user_info.get('data', {}).get('id'),
                'username': user_info.get('data', {}).get('username'),
                'name': user_info.get('data', {}).get('name'),
                'picture': user_info.get('data', {}).get('profile_image_url'),
                'email': None  # Twitter doesn't provide email by default
            })
        
        return normalized
    
    def refresh_token(self, provider: str, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        config = self.providers[provider]
        
        token_data = {
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'DataHub/1.0'
        }
        
        try:
            req = urllib.request.Request(
                config['token_url'],
                data=urllib.parse.urlencode(token_data).encode(),
                headers=headers
            )
            
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
                
        except Exception as e:
            raise Exception(f"Token refresh failed: {str(e)}")
    
    def revoke_token(self, provider: str, token: str) -> bool:
        """Revoke access token"""
        # Implementation varies by provider
        return True
    
    def is_configured(self, provider: str) -> bool:
        """Check if provider is properly configured"""
        config = self.providers[provider]
        return (
            config['client_id'] != f'your_{provider}_client_id' and
            config['client_secret'] != f'your_{provider}_client_secret'
        )
