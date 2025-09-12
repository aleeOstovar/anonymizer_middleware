"""Environment variable loader for PII module.

This module loads environment variables from a .env file if it exists.
"""

import os
from pathlib import Path


def load_env_file(env_path=None):
    """Load environment variables from .env file
    
    Args:
        env_path: Path to .env file. If None, looks for .env in current directory
    """
    if env_path is None:
        env_path = Path(os.path.dirname(os.path.abspath(__file__))) / '.env'
    
    if not os.path.exists(env_path):
        return
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()


# Load environment variables when module is imported
load_env_file()