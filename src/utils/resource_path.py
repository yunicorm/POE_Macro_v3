"""Resource path handling for executable compatibility."""

import os
import sys


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def get_config_path(filename):
    """Get path to config file."""
    return get_resource_path(os.path.join('config', filename))


def get_asset_path(filename):
    """Get path to asset file."""
    return get_resource_path(os.path.join('assets', filename))


def get_template_path(filename):
    """Get path to template image."""
    return get_resource_path(os.path.join('assets', 'templates', filename))


def get_data_path(filename):
    """Get path to data file."""
    return get_resource_path(os.path.join('data', filename))


def get_flask_data_path(filename):
    """Get path to flask data file."""
    return get_resource_path(os.path.join('data', 'flasks', filename))


def ensure_directory_exists(path):
    """Ensure directory exists, create if not."""
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return path


def get_user_config_dir():
    """Get user config directory for saving user settings."""
    if getattr(sys, 'frozen', False):
        # If running as exe, use AppData directory
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        config_dir = os.path.join(app_data, 'POE_Macro_v3')
    else:
        # Development mode - use project directory
        config_dir = os.path.join(os.path.abspath("."), 'config')
    
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


def get_user_config_path(filename):
    """Get path for user-modifiable config files."""
    return os.path.join(get_user_config_dir(), filename)