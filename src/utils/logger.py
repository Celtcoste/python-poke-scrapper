import os
from typing import Any

class DebugLogger:
    """
    Debug logging utility for poke-scrapper
    By default, only error logs are shown
    Set DEBUG_MODE=1 environment variable or call enable_debug() to see debug logs
    """
    
    def __init__(self):
        self.debug_enabled = os.getenv('DEBUG_MODE', '0').lower() in ('1', 'true', 'on', 'yes')
    
    def enable_debug(self):
        """Enable debug mode programmatically"""
        self.debug_enabled = True
    
    def disable_debug(self):
        """Disable debug mode programmatically"""
        self.debug_enabled = False
    
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled"""
        return self.debug_enabled
    
    def debug(self, message: str, *args: Any):
        """Log debug message (only shown when debug mode is on)"""
        if self.debug_enabled:
            if args:
                message = message % args
            print(f"DEBUG: {message}")
    
    def info(self, message: str, *args: Any):
        """Log info message (only shown when debug mode is on)"""
        if self.debug_enabled:
            if args:
                message = message % args
            print(f"DEBUG: {message}")
    
    def error(self, message: str, *args: Any):
        """Log error message (always shown)"""
        if args:
            message = message % args
        print(f"Error: {message}")
    
    def warning(self, message: str, *args: Any):
        """Log warning message (only shown when debug mode is on)"""
        if self.debug_enabled:
            if args:
                message = message % args
            print(f"DEBUG: Warning: {message}")

# Global logger instance
logger = DebugLogger()

# Convenience functions
def debug(message: str, *args: Any):
    """Log debug message"""
    logger.debug(message, *args)

def info(message: str, *args: Any):
    """Log info message"""
    logger.info(message, *args)

def error(message: str, *args: Any):
    """Log error message"""
    logger.error(message, *args)

def warning(message: str, *args: Any):
    """Log warning message"""
    logger.warning(message, *args)

def enable_debug():
    """Enable debug mode"""
    logger.enable_debug()

def disable_debug():
    """Disable debug mode"""
    logger.disable_debug()

def is_debug_enabled() -> bool:
    """Check if debug mode is enabled"""
    return logger.is_debug_enabled()