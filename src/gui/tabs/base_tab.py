"""
Base tab class for POE Macro GUI tabs
"""
import logging
from PyQt5.QtWidgets import QWidget

logger = logging.getLogger(__name__)

class BaseTab:
    """Base class for all GUI tabs"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.config_manager = main_window.config_manager
        self.config = main_window.config
        self.macro_controller = main_window.macro_controller
        self.logger = logger
    
    def log_message(self, message):
        """Log message to both file and GUI"""
        self.logger.info(message)
        if self.main_window.log_text:
            self.main_window.log_message(message)
    
    def get_config_value(self, section, key, default=None):
        """Get configuration value safely"""
        return self.config.get(section, {}).get(key, default)
    
    def create_widget(self):
        """Create and return the tab widget. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement create_widget()")