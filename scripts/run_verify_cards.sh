#!/bin/bash
# Wrapper script to run verify_serie_cards.py with correct environment

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to poke-scrapper directory (where .env is located)
cd "$PROJECT_ROOT/poke-scrapper"

# Activate virtual environment
source venv/bin/activate

# Set Python path to include src directory
export PYTHONPATH="$PROJECT_ROOT/poke-scrapper/src:$PYTHONPATH"

# Run the verification script
python3 "$SCRIPT_DIR/verify_serie_cards.py" "$@"
