"""
Configuration module for poke-scrapper

Debug mode can be enabled via:
1. Environment variable: DEBUG_MODE=1
2. Programmatically: from utils.logger import enable_debug; enable_debug()
"""
import os
from .utils.logger import enable_debug, disable_debug, is_debug_enabled

def setup_debug_mode():
    """Setup debug mode based on environment variables or other configuration"""
    debug_mode = os.getenv('DEBUG_MODE', '0').lower() in ('1', 'true', 'on', 'yes')
    
    if debug_mode:
        enable_debug()
        print("Debug mode: ON - All debug logs will be shown")
    else:
        disable_debug()
        print("Debug mode: OFF - Only error logs will be shown")
    
    return is_debug_enabled()

def enable_debug_mode():
    """Enable debug mode programmatically"""
    enable_debug()
    print("Debug mode enabled - All debug logs will be shown")

def disable_debug_mode():
    """Disable debug mode programmatically"""
    disable_debug()
    print("Debug mode disabled - Only error logs will be shown")