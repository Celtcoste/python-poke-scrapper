# Card Data Verification Scripts

This directory contains scripts to verify and fix data integrity issues in the Pokemon card database.

## verify_serie_cards.py

A comprehensive Python script that verifies all cards in a Pokemon serie have complete data by checking for missing entries in related tables.

### Features

- Identifies cards with missing `pokemon_card`, `energy_card`, or `trainer_card` entries
- Checks for missing or invalid illustrator references
- Detects cards without translations
- Validates required fields (HP, level, dex ID for Pokemon cards)
- Generates detailed reports with color-coded severity levels
- Can export results as JSON
- Can generate SQL fix suggestions

### Usage

#### Quick Start (Recommended)

Use the wrapper script that handles all environment setup:

```bash
./scripts/run_verify_cards.sh <serie_id>
```

Examples:
```bash
# Verify serie 176
./scripts/run_verify_cards.sh 176

# Verbose output with SQL query
./scripts/run_verify_cards.sh 176 --verbose

# Generate JSON output
./scripts/run_verify_cards.sh 176 --json

# Generate SQL fix suggestions
./scripts/run_verify_cards.sh 176 --fixes > fixes.sql
```

#### Manual Execution

If you need to run the script directly:

```bash
cd poke-scrapper
source venv/bin/activate
export PYTHONPATH="$(pwd):$PYTHONPATH"
python3 ../scripts/verify_serie_cards.py <serie_id>
```

### Understanding the Output

The script provides:

1. **Summary Statistics**
   - Serie information (name, ID, slug)
   - Total cards found vs expected
   - Number of cards with issues

2. **Issues by Category**
   - Breakdown of problems by card type (Pokemon, Energy, Trainer)

3. **Issues by Type**
   - Count of each specific issue type

4. **Detailed Card-by-Card Report**
   - Card position, ID, name, and slug
   - Severity-coded issues:
     - **[CRITICAL]** (Red): Missing required data that causes GraphQL errors
     - **[WARNING]** (Yellow): Missing optional data with fallbacks
     - **[INFO]** (Cyan): Missing truly optional data

### Common Issues and What They Mean

#### Missing pokemon_card Entry
**Severity:** CRITICAL

This is the most serious issue. When a card has `category_id = 1` (Pokemon) but no row in the `pokemon_card` table, the DataLoader silently drops it, causing `null` values in GraphQL responses.

**Required fields in pokemon_card:**
- `pokemon_id` - Pokedex ID (dexID in GraphQL)
- `hp` - Hit points
- `level` - Pokemon level

**Fix:** Re-scrape the card or manually insert a `pokemon_card` row with correct data.

#### Missing energy_card Entry
**Severity:** WARNING

Energy cards have fallback handling in the code, so this won't cause GraphQL errors, but the data is incomplete.

**Fix:** Insert an `energy_card` row with the correct `element_id`.

#### Missing trainer_card Entry
**Severity:** INFO

Trainer cards don't require a separate `trainer_card` entry in the current schema.

**Fix:** Optional - can be ignored unless you need complete data.

### Generating Fix Queries

Use the `--fixes` flag to generate INSERT statements for missing data:

```bash
./scripts/run_verify_cards.sh 176 --fixes > fixes.sql
```

Review and edit the generated SQL before running it. You'll need to fill in correct values for:
- Pokemon ID (dex ID)
- HP values
- Level values
- Element IDs

### Troubleshooting

**"Connection refused" or "Access denied"**
- Ensure your database is running
- Check that `.env` file exists in `poke-scrapper/` directory
- Verify database credentials in `.env`

**"Module not found" errors**
- Make sure you're using the wrapper script (`run_verify_cards.sh`)
- Or ensure you've activated the poke-scrapper virtual environment

**Schema mismatch errors**
- The script matches the current database schema
- If you've made schema changes, you may need to update the script queries

### Integration with Scraper

When you scrape a new serie, run this verification script immediately to catch any issues:

```bash
# After scraping
cd poke-scrapper
python3 main.py  # Your scraping command

# Verify the data
cd ..
./scripts/run_verify_cards.sh <serie_id>
```

### Example Output

```
================================================================================
Card Data Integrity Report
================================================================================

Serie Information:
  ID:            176
  Name:          Flammes Fantasmagoriques
  Slug:          poke-fr/me/me02
  Expected:      130 cards
  Found:         130 cards

Status:
  ✓ Cards OK:        95
  ✗ Cards with issues: 35

Issues by Category:
  Pokemon: 15 card(s)
  Energy: 19 card(s)

Issues by Type:
  missing_pokemon_card: 15 occurrence(s)
  missing_energy_card: 19 occurrence(s)
```

## Files

- `verify_serie_cards.py` - Main verification script
- `run_verify_cards.sh` - Wrapper script for easy execution
- `README.md` - This file
