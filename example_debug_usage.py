#!/usr/bin/env python3
"""
Example demonstrating debug mode usage in poke-scrapper

Run this script to see how debug mode works:
- python example_debug_usage.py  (debug mode off by default)
- DEBUG_MODE=1 python example_debug_usage.py  (debug mode on via env var)
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import setup_debug_mode, enable_debug_mode, disable_debug_mode
from src.utils.logger import debug, info, error, warning

def demo_logging():
    """Demonstrate different logging levels"""
    print("\n=== Testing different log levels ===")
    
    debug("This is a debug message - only shown in debug mode")
    info("This is an info message - only shown in debug mode")  
    warning("This is a warning message - only shown in debug mode")
    error("This is an error message - always shown")
    
    print("=== End of log test ===\n")

def main():
    print("=== Poke-Scrapper Debug Mode Demo ===")
    
    # Setup debug mode based on environment
    is_debug_on = setup_debug_mode()
    
    # Demonstrate logging with current mode
    demo_logging()
    
    # Toggle debug mode programmatically
    if is_debug_on:
        print("Disabling debug mode...")
        disable_debug_mode()
        demo_logging()
        
        print("Re-enabling debug mode...")
        enable_debug_mode()
        demo_logging()
    else:
        print("Enabling debug mode...")
        enable_debug_mode()
        demo_logging()
        
        print("Disabling debug mode...")
        disable_debug_mode()
        demo_logging()
    
    print("Demo completed!")
    print("\nTo use in your code:")
    print("1. Set DEBUG_MODE=1 environment variable")
    print("2. Or call: from src.config import enable_debug_mode; enable_debug_mode()")
    print("3. Use: from src.utils.logger import debug, info, error")

if __name__ == "__main__":
    main()