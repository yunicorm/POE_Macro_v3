"""
POE Macro v3 Version Management
"""

VERSION = "3.0.0"
BUILD_DATE = "2025-01-06"
AUTHOR = "POE Macro Development Team"

def get_version_string():
    """Get formatted version string"""
    return f"v{VERSION}"

def get_full_version_info():
    """Get complete version information"""
    return {
        "version": VERSION,
        "build_date": BUILD_DATE,
        "author": AUTHOR,
        "display": f"POE Macro v{VERSION}"
    }