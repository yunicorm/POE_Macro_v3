"""
GUI helper functions for POE Macro
"""
import logging

logger = logging.getLogger(__name__)

def setup_tab_widget(tab_widget, tabs_config):
    """
    Setup tab widget with provided tabs configuration
    
    Args:
        tab_widget: QTabWidget instance
        tabs_config: List of (tab_class, tab_name) tuples
    """
    for tab_class, tab_name in tabs_config:
        try:
            widget = tab_class.create_widget()
            tab_widget.addTab(widget, tab_name)
            logger.debug(f"Added tab: {tab_name}")
        except Exception as e:
            logger.error(f"Failed to create tab {tab_name}: {e}")

def safe_disconnect_signal(signal, slot):
    """
    Safely disconnect signal from slot
    
    Args:
        signal: PyQt signal
        slot: Connected slot function
    """
    try:
        signal.disconnect(slot)
    except TypeError:
        # Signal was not connected
        pass
    except Exception as e:
        logger.warning(f"Error disconnecting signal: {e}")

def safe_set_value(widget, value, method_name="setValue"):
    """
    Safely set value to widget with error handling
    
    Args:
        widget: Qt widget
        value: Value to set
        method_name: Method name to call (default: setValue)
    """
    try:
        method = getattr(widget, method_name)
        method(value)
        return True
    except Exception as e:
        logger.warning(f"Failed to set value {value} to widget: {e}")
        return False