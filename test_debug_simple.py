#!/usr/bin/env python3
"""
Simple test of debug logging without database dependencies
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.logger import debug, info, error, warning, enable_debug, disable_debug, is_debug_enabled

def demo_logging():
    """Demonstrate different logging levels"""
    print("\n=== Testing different log levels ===")
    
    debug("This is a debug message - only shown in debug mode")
    info("This is an info message - only shown in debug mode")  
    warning("This is a warning message - only shown in debug mode")
    error("This is an error message - always shown")
    
    print("=== End of log test ===\n")

def main():
    print("=== Poke-Scrapper Debug Mode Simple Test ===")
    
    # Test with debug mode OFF (default)
    print("Testing with debug mode OFF (default):")
    print(f"Debug enabled: {is_debug_enabled()}")
    demo_logging()
    
    # Test with debug mode ON
    print("Enabling debug mode...")
    enable_debug()
    print(f"Debug enabled: {is_debug_enabled()}")
    demo_logging()
    
    # Test with debug mode OFF again
    print("Disabling debug mode...")
    disable_debug()
    print(f"Debug enabled: {is_debug_enabled()}")
    demo_logging()
    
    print("Simple test completed successfully!")

if __name__ == "__main__":
    main()