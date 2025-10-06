"""
User management and session handling for personalized data
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any


class UserManager:
    """Manages user profiles and personalized data access"""

    def __init__(self):
        self.users_dir = "data/users"
        self.profiles_dir = "data/profiles"
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure user data directories exist"""
        os.makedirs(self.users_dir, exist_ok=True)
        os.makedirs(self.profiles_dir, exist_ok=True)

    def create_user_profile(
        self, user_data: Dict[str, Any], provider: str, tokens: Dict[str, Any]
    ) -> str:
        """Create or update user profile"""
        user_id = user_data.get("id")
        if not user_id:
            raise ValueError("User ID is required")

        profile = {
            "user_id": user_id,
            "provider": provider,
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "picture": user_data.get("picture"),
            "username": user_data.get("username"),
            "preferences": {
                "microsoft": {
                    "subscriptions": ["azure", "office365", "github"],
                    "notifications": True,
                },
                "google": {"subscriptions": ["gcp", "workspace", "android"], "notifications": True},
                "twitter": {
                    "subscriptions": ["timeline", "mentions", "trends"],
                    "notifications": True,
                },
            },
            "tokens": {
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "expires_at": (
                    datetime.now() + timedelta(seconds=tokens.get("expires_in", 3600))
                ).isoformat(),
                "token_type": tokens.get("token_type", "Bearer"),
            },
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }

        filename = f"{self.profiles_dir}/{provider}_{user_id}.json"
        with open(filename, "w") as f:
            json.dump(profile, f, indent=2)

        return filename

    def get_user_profile(self, provider: str, user_id: str) -> Dict[str, Any]:
        """Get user profile by provider and user ID"""
        filename = f"{self.profiles_dir}/{provider}_{user_id}.json"

        try:
            with open(filename, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def update_user_preferences(
        self, provider: str, user_id: str, preferences: Dict[str, Any]
    ) -> bool:
        """Update user preferences"""
        profile = self.get_user_profile(provider, user_id)
        if not profile:
            return False

        profile["preferences"].update(preferences)
        profile["last_updated"] = datetime.now().isoformat()

        filename = f"{self.profiles_dir}/{provider}_{user_id}.json"
        with open(filename, "w") as f:
            json.dump(profile, f, indent=2)

        return True

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all user profiles"""
        users = []
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith(".json"):
                with open(f"{self.profiles_dir}/{filename}", "r") as f:
                    users.append(json.load(f))
        return users

    def get_personalized_microsoft_data(self, user_id: str) -> Dict[str, Any]:
        """Get personalized Microsoft data for user"""
        profile = self.get_user_profile("microsoft", user_id)
        if not profile:
            return {}

        preferences = profile.get("preferences", {}).get("microsoft", {})

        return {
            "user_id": user_id,
            "subscriptions": preferences.get("subscriptions", []),
            "azure_resources": [],
            "office365_activity": [],
            "github_repositories": [],
            "personalized_alerts": [],
            "generated_at": datetime.now().isoformat(),
        }

    def get_personalized_google_data(self, user_id: str) -> Dict[str, Any]:
        """Get personalized Google data for user"""
        profile = self.get_user_profile("google", user_id)
        if not profile:
            return {}

        preferences = profile.get("preferences", {}).get("google", {})

        return {
            "user_id": user_id,
            "subscriptions": preferences.get("subscriptions", []),
            "gcp_projects": [],
            "google_workspace_activity": [],
            "android_developer_updates": [],
            "personalized_alerts": [],
            "generated_at": datetime.now().isoformat(),
        }

    def get_personalized_twitter_data(self, user_id: str) -> Dict[str, Any]:
        """Get personalized Twitter data for user"""
        profile = self.get_user_profile("twitter", user_id)
        if not profile:
            return {}

        preferences = profile.get("preferences", {}).get("twitter", {})

        return {
            "user_id": user_id,
            "subscriptions": preferences.get("subscriptions", []),
            "timeline_feed": [],
            "mentions": [],
            "trending_in_network": [],
            "personalized_alerts": [],
            "generated_at": datetime.now().isoformat(),
        }

    def get_user_tokens(self, provider: str, user_id: str) -> Dict[str, Any]:
        """Get user tokens (safely - without exposing sensitive data)"""
        profile = self.get_user_profile(provider, user_id)
        if not profile:
            return {}

        tokens = profile.get("tokens", {})
        return {
            "token_type": tokens.get("token_type"),
            "expires_at": tokens.get("expires_at"),
            "is_expired": datetime.fromisoformat(tokens.get("expires_at", "")) < datetime.now(),
        }

    def refresh_user_token(self, provider: str, user_id: str, new_tokens: Dict[str, Any]) -> bool:
        """Update user tokens"""
        profile = self.get_user_profile(provider, user_id)
        if not profile:
            return False

        profile["tokens"].update(
            {
                "access_token": new_tokens.get("access_token"),
                "refresh_token": new_tokens.get(
                    "refresh_token", profile["tokens"].get("refresh_token")
                ),
                "expires_at": (
                    datetime.now() + timedelta(seconds=new_tokens.get("expires_in", 3600))
                ).isoformat(),
                "token_type": new_tokens.get("token_type", "Bearer"),
            }
        )
        profile["last_updated"] = datetime.now().isoformat()

        filename = f"{self.profiles_dir}/{provider}_{user_id}.json"
        with open(filename, "w") as f:
            json.dump(profile, f, indent=2)

        return True

    def delete_user(self, provider: str, user_id: str) -> bool:
        """Delete user profile"""
        filename = f"{self.profiles_dir}/{provider}_{user_id}.json"
        try:
            os.remove(filename)
            return True
        except FileNotFoundError:
            return False

    def get_user_activity_summary(self, provider: str, user_id: str) -> Dict[str, Any]:
        """Get user activity summary"""
        profile = self.get_user_profile(provider, user_id)
        if not profile:
            return {}

        return {
            "user_id": user_id,
            "provider": provider,
            "account_age": (datetime.now() - datetime.fromisoformat(profile["created_at"])).days,
            "last_login": profile["last_login"],
            "preferences_count": len(profile.get("preferences", {})),
            "total_interactions": 0,  # This would be populated from actual usage
            "generated_at": datetime.now().isoformat(),
        }
