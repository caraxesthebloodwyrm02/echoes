"""
Unified Code Runtime (UCR) - Mock implementation for testing.

This is a mock implementation of the UCR module to allow tests to run.
In a real implementation, this would provide environment and project management.
"""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class UCREnvironment:
    """Mock UCR Environment class."""
    
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.variables = {}
    
    def set_variable(self, key: str, value: str):
        """Set an environment variable."""
        self.variables[key] = value
    
    def get_variable(self, key: str) -> Optional[str]:
        """Get an environment variable."""
        return self.variables.get(key)


class UCRProject:
    """Mock UCR Project class."""
    
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.environments = []


class UCR:
    """Mock UCR main class."""
    
    def __init__(self):
        self.config = {
            'projectsRoot': str(Path.home() / 'projects'),
            'environmentsRoot': str(Path.home() / '.ucr' / 'envs')
        }
        self.active_env = {'name': 'default', 'path': str(Path.home())}
        self.environments = {}
        self.projects = {}
    
    def create_environment(self, name: str, path: str) -> UCREnvironment:
        """Create a new environment."""
        env = UCREnvironment(name, path)
        self.environments[name] = env
        return env
    
    def activate_environment(self, name: str):
        """Activate an environment."""
        if name in self.environments:
            self.active_env = {
                'name': name,
                'path': self.environments[name].path
            }
        else:
            raise ValueError(f"Environment {name} not found")
    
    def create_project(self, name: str, path: str) -> UCRProject:
        """Create a new project."""
        project = UCRProject(name, path)
        self.projects[name] = project
        return project
    
    def get_env_vars(self) -> Dict[str, str]:
        """Get environment variables."""
        return dict(os.environ)


# Create global UCR instance
ucr = UCR()

__all__ = ['ucr', 'UCR', 'UCREnvironment', 'UCRProject']
