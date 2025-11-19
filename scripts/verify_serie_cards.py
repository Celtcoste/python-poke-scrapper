#!/usr/bin/env python3
"""
Card Data Integrity Verification Script

This script verifies that all cards in a Pokemon serie have complete data
by checking for missing entries in related tables (pokemon_card, energy_card,
trainer_card, illustrator, card_translation).

Usage:
    python verify_serie_cards.py <serie_id>
    python verify_serie_cards.py --all
    python verify_serie_cards.py 176 --json
    python verify_serie_cards.py 176 --verbose
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Import database connection
create_connection = None

try:
    # Try to import from poke-scrapper (when run from poke-scrapper directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scrapper_root = os.path.join(script_dir, '..', 'poke-scrapper')
    scrapper_root = os.path.abspath(scrapper_root)

    if scrapper_root not in sys.path:
        sys.path.insert(0, scrapper_root)

    from src.database.database import create_connection as _create_connection
    create_connection = _create_connection
except ImportError as import_err:
    # Fallback: create our own connection function
    try:
        import mysql.connector
        from dotenv import load_dotenv

        def create_connection():
            # Try to find .env file in project root
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            env_files = [
                os.path.join(project_root, '.env'),
                os.path.join(project_root, 'poke-scrapper', '.env'),
                os.path.join(os.getcwd(), '.env')
            ]

            # Load from first existing .env file
            for env_file in env_files:
                if os.path.exists(env_file):
                    load_dotenv(env_file)
                    break
            else:
                load_dotenv()  # Try default locations

            connection = None
            try:
                connection = mysql.connector.connect(
                    host=os.environ.get('DATABASE_ADDRESS', 'localhost'),
                    port=os.environ.get('DATABASE_PORT', '3306'),
                    user=os.environ.get('DATABASE_USERNAME', 'root'),
                    password=os.environ.get('DATABASE_PASSWORD', ''),
                    database=os.environ.get('DATABASE_NAME', 'atticardex')
                )
                print("Connection to MySQL DB successful")
            except Exception as e:
                print(f"The error '{e}' occurred")
            return connection
    except ImportError as e:
        print("Error: Could not import required modules.")
        print("Make sure mysql-connector-python and python-dotenv are installed:")
        print("  pip install mysql-connector-python python-dotenv")
        sys.exit(1)

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Category IDs (from database schema)
CATEGORY_POKEMON = 1
CATEGORY_ENERGY = 2
CATEGORY_TRAINER = 3

CATEGORY_NAMES = {
    CATEGORY_POKEMON: "Pokemon",
    CATEGORY_ENERGY: "Energy",
    CATEGORY_TRAINER: "Trainer"
}


def get_serie_info(connection, serie_id: int) -> Dict[str, Any]:
    """Get information about a serie."""
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT s.id, s.slug, st.name, st.translation_language_id, s.card_number as total_cards
        FROM serie s
        LEFT JOIN serie_translation st ON s.id = st.serie_id
        WHERE s.id = %s AND st.translation_language_id = 1
    """

    cursor.execute(query, (serie_id,))
    result = cursor.fetchone()
    cursor.close()

    return result


def get_all_cards_in_serie(connection, serie_id: int) -> List[Dict[str, Any]]:
    """Get all cards in a serie with basic information."""
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            c.id,
            c.slug,
            c.category_id,
            c.rarity_id,
            c.serie_id,
            c.illustrator_id,
            ct.name,
            ct.translation_language_id,
            c.position
        FROM card c
        LEFT JOIN card_translation ct ON c.id = ct.card_id AND ct.translation_language_id = 1
        WHERE c.serie_id = %s
        ORDER BY c.position
    """

    cursor.execute(query, (serie_id,))
    results = cursor.fetchall()
    cursor.close()

    return results


def check_pokemon_card_data(connection, card_ids: List[int]) -> Dict[int, Dict[str, Any]]:
    """Check which pokemon cards have complete pokemon_card data."""
    if not card_ids:
        return {}

    cursor = connection.cursor(dictionary=True)

    placeholders = ','.join(['%s'] * len(card_ids))
    query = f"""
        SELECT
            pc.card_id,
            pc.pokemon_id,
            pc.hp,
            pc.level
        FROM pokemon_card pc
        WHERE pc.card_id IN ({placeholders})
    """

    cursor.execute(query, card_ids)
    results = cursor.fetchall()
    cursor.close()

    # Create a map of card_id -> pokemon_card data
    return {row['card_id']: row for row in results}


def check_energy_card_data(connection, card_ids: List[int]) -> Dict[int, Dict[str, Any]]:
    """Check which energy cards have energy_card data."""
    if not card_ids:
        return {}

    cursor = connection.cursor(dictionary=True)

    placeholders = ','.join(['%s'] * len(card_ids))
    query = f"""
        SELECT
            ec.card_id,
            ec.element_id
        FROM energy_card ec
        WHERE ec.card_id IN ({placeholders})
    """

    cursor.execute(query, card_ids)
    results = cursor.fetchall()
    cursor.close()

    return {row['card_id']: row for row in results}


def check_trainer_card_data(connection, card_ids: List[int]) -> Dict[int, Dict[str, Any]]:
    """Check which trainer cards have trainer_card data."""
    if not card_ids:
        return {}

    cursor = connection.cursor(dictionary=True)

    placeholders = ','.join(['%s'] * len(card_ids))
    query = f"""
        SELECT
            tc.card_id,
            tc.id
        FROM trainer_card tc
        WHERE tc.card_id IN ({placeholders})
    """

    cursor.execute(query, card_ids)
    results = cursor.fetchall()
    cursor.close()

    return {row['card_id']: row for row in results}


def check_illustrator_exists(connection, illustrator_ids: List[int]) -> Dict[int, bool]:
    """Check which illustrators exist."""
    if not illustrator_ids:
        return {}

    cursor = connection.cursor(dictionary=True)

    placeholders = ','.join(['%s'] * len(illustrator_ids))
    query = f"""
        SELECT id
        FROM illustrator
        WHERE id IN ({placeholders})
    """

    cursor.execute(query, illustrator_ids)
    results = cursor.fetchall()
    cursor.close()

    existing_ids = {row['id'] for row in results}
    return {illus_id: illus_id in existing_ids for illus_id in illustrator_ids}


def analyze_cards(connection, serie_id: int, verbose: bool = False) -> Dict[str, Any]:
    """Analyze all cards in a serie for missing data."""

    # Get serie information
    serie_info = get_serie_info(connection, serie_id)
    if not serie_info:
        return {
            'error': f'Serie {serie_id} not found',
            'serie_id': serie_id
        }

    # Get all cards
    cards = get_all_cards_in_serie(connection, serie_id)
    if not cards:
        return {
            'error': f'No cards found for serie {serie_id}',
            'serie_id': serie_id,
            'serie_info': serie_info
        }

    # Separate cards by category
    pokemon_card_ids = [c['id'] for c in cards if c['category_id'] == CATEGORY_POKEMON]
    energy_card_ids = [c['id'] for c in cards if c['category_id'] == CATEGORY_ENERGY]
    trainer_card_ids = [c['id'] for c in cards if c['category_id'] == CATEGORY_TRAINER]

    # Get illustrator IDs
    illustrator_ids = list(set(c['illustrator_id'] for c in cards if c['illustrator_id']))

    # Check for missing data
    pokemon_data = check_pokemon_card_data(connection, pokemon_card_ids)
    energy_data = check_energy_card_data(connection, energy_card_ids)
    trainer_data = check_trainer_card_data(connection, trainer_card_ids)
    illustrator_exists = check_illustrator_exists(connection, illustrator_ids)

    # Analyze issues
    issues = []

    for card in cards:
        card_issues = []

        # Check translation
        if not card['name']:
            card_issues.append({
                'type': 'missing_translation',
                'severity': 'critical',
                'message': 'Missing card_translation entry'
            })

        # Check illustrator
        if not card['illustrator_id']:
            card_issues.append({
                'type': 'missing_illustrator_id',
                'severity': 'critical',
                'message': 'Card has NULL illustrator_id'
            })
        elif not illustrator_exists.get(card['illustrator_id'], False):
            card_issues.append({
                'type': 'invalid_illustrator',
                'severity': 'critical',
                'message': f'Illustrator ID {card["illustrator_id"]} does not exist'
            })

        # Check category-specific data
        if card['category_id'] == CATEGORY_POKEMON:
            if card['id'] not in pokemon_data:
                card_issues.append({
                    'type': 'missing_pokemon_card',
                    'severity': 'critical',
                    'message': 'Missing pokemon_card entry (required for pokemon_id/dexID, hp, level)'
                })
            else:
                poke_data = pokemon_data[card['id']]
                if poke_data['pokemon_id'] is None or poke_data['pokemon_id'] == 0:
                    card_issues.append({
                        'type': 'invalid_pokemon_id',
                        'severity': 'warning',
                        'message': 'pokemon_id is NULL or 0'
                    })
                if poke_data['hp'] is None or poke_data['hp'] == 0:
                    card_issues.append({
                        'type': 'invalid_hp',
                        'severity': 'warning',
                        'message': 'HP is NULL or 0'
                    })
                if poke_data['level'] is None or poke_data['level'] == '':
                    card_issues.append({
                        'type': 'invalid_level',
                        'severity': 'warning',
                        'message': 'Level is NULL or empty'
                    })

        elif card['category_id'] == CATEGORY_ENERGY:
            if card['id'] not in energy_data:
                card_issues.append({
                    'type': 'missing_energy_card',
                    'severity': 'warning',
                    'message': 'Missing energy_card entry (has fallback in code)'
                })

        elif card['category_id'] == CATEGORY_TRAINER:
            if card['id'] not in trainer_data:
                card_issues.append({
                    'type': 'missing_trainer_card',
                    'severity': 'info',
                    'message': 'Missing trainer_card entry (optional)'
                })

        if card_issues:
            issues.append({
                'card': card,
                'issues': card_issues
            })

    # Generate summary
    summary = {
        'serie_id': serie_id,
        'serie_name': serie_info['name'],
        'serie_slug': serie_info['slug'],
        'expected_cards': serie_info['total_cards'],
        'actual_cards': len(cards),
        'cards_with_issues': len(issues),
        'cards_ok': len(cards) - len(issues),
        'issues_by_category': {
            'Pokemon': len([i for i in issues if i['card']['category_id'] == CATEGORY_POKEMON]),
            'Energy': len([i for i in issues if i['card']['category_id'] == CATEGORY_ENERGY]),
            'Trainer': len([i for i in issues if i['card']['category_id'] == CATEGORY_TRAINER]),
        },
        'issue_types': {}
    }

    # Count issue types
    for issue_record in issues:
        for issue in issue_record['issues']:
            issue_type = issue['type']
            if issue_type not in summary['issue_types']:
                summary['issue_types'][issue_type] = 0
            summary['issue_types'][issue_type] += 1

    return {
        'summary': summary,
        'issues': issues,
        'timestamp': datetime.now().isoformat()
    }


def print_report(analysis: Dict[str, Any], verbose: bool = False):
    """Print a formatted report of the analysis."""

    if 'error' in analysis:
        print(f"{Colors.FAIL}Error: {analysis['error']}{Colors.ENDC}")
        return

    summary = analysis['summary']
    issues = analysis['issues']

    # Print header
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}Card Data Integrity Report{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    # Print summary
    print(f"{Colors.OKBLUE}{Colors.BOLD}Serie Information:{Colors.ENDC}")
    print(f"  ID:            {summary['serie_id']}")
    print(f"  Name:          {summary['serie_name']}")
    print(f"  Slug:          {summary['serie_slug']}")
    print(f"  Expected:      {summary['expected_cards']} cards")
    print(f"  Found:         {summary['actual_cards']} cards")

    # Print status
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}Status:{Colors.ENDC}")
    if summary['cards_with_issues'] == 0:
        print(f"  {Colors.OKGREEN}✓ All cards have complete data!{Colors.ENDC}")
    else:
        print(f"  {Colors.OKGREEN}✓ Cards OK:        {summary['cards_ok']}{Colors.ENDC}")
        print(f"  {Colors.FAIL}✗ Cards with issues: {summary['cards_with_issues']}{Colors.ENDC}")

    # Print issues by category
    if summary['cards_with_issues'] > 0:
        print(f"\n{Colors.WARNING}{Colors.BOLD}Issues by Category:{Colors.ENDC}")
        for category, count in summary['issues_by_category'].items():
            if count > 0:
                print(f"  {category}: {count} card(s)")

        print(f"\n{Colors.WARNING}{Colors.BOLD}Issues by Type:{Colors.ENDC}")
        for issue_type, count in summary['issue_types'].items():
            print(f"  {issue_type}: {count} occurrence(s)")

    # Print detailed issues
    if issues:
        print(f"\n{Colors.FAIL}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.FAIL}{Colors.BOLD}Detailed Issues ({len(issues)} cards){Colors.ENDC}")
        print(f"{Colors.FAIL}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

        for idx, issue_record in enumerate(issues, 1):
            card = issue_record['card']
            card_issues = issue_record['issues']

            # Determine severity color
            has_critical = any(i['severity'] == 'critical' for i in card_issues)
            severity_color = Colors.FAIL if has_critical else Colors.WARNING

            print(f"{severity_color}{Colors.BOLD}[{idx}] Card #{card['position']}{Colors.ENDC} "
                  f"(ID: {card['id']}, Category: {CATEGORY_NAMES.get(card['category_id'], 'Unknown')})")
            print(f"    Name:  {card['name'] or '(missing)'}")
            print(f"    Slug:  {card['slug']}")
            print(f"    Issues:")

            for issue in card_issues:
                severity_marker = {
                    'critical': f"{Colors.FAIL}[CRITICAL]",
                    'warning': f"{Colors.WARNING}[WARNING]",
                    'info': f"{Colors.OKCYAN}[INFO]"
                }.get(issue['severity'], '[UNKNOWN]')

                print(f"      {severity_marker} {issue['message']}{Colors.ENDC}")

            print()

    # Print SQL query to find problematic cards
    if issues and verbose:
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}SQL Query to Find These Cards:{Colors.ENDC}")
        card_ids = [str(i['card']['id']) for i in issues]
        print(f"""
SELECT c.id, c.slug, c.position, ct.name, c.category_id
FROM card c
LEFT JOIN card_translation ct ON c.id = ct.card_id AND ct.translation_language_id = 1
WHERE c.id IN ({', '.join(card_ids)})
ORDER BY c.position;
""")

    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")


def generate_fix_suggestions(analysis: Dict[str, Any]) -> List[str]:
    """Generate SQL queries to help fix the issues."""

    if 'error' in analysis or not analysis.get('issues'):
        return []

    suggestions = []

    for issue_record in analysis['issues']:
        card = issue_record['card']

        for issue in issue_record['issues']:
            if issue['type'] == 'missing_pokemon_card':
                suggestions.append(f"""
-- Fix for Card #{card['position']} ({card['name']}) - Missing pokemon_card entry
INSERT INTO pokemon_card (slug, card_id, pokemon_id, hp, level, elements)
VALUES (
    '{card['slug']}',
    {card['id']},
    0,  -- TODO: Set correct pokemon_id (dex ID)
    0,  -- TODO: Set correct HP
    '0',  -- TODO: Set correct level
    '[]'  -- TODO: Set elements JSON array
);
""")

            elif issue['type'] == 'missing_energy_card':
                suggestions.append(f"""
-- Fix for Card #{card['position']} ({card['name']}) - Missing energy_card entry
INSERT INTO energy_card (slug, card_id, element_id)
VALUES (
    '{card['slug']}',
    {card['id']},
    1  -- TODO: Set correct element_id
);
""")

            elif issue['type'] == 'missing_trainer_card':
                suggestions.append(f"""
-- Fix for Card #{card['position']} ({card['name']}) - Missing trainer_card entry
INSERT INTO trainer_card (slug, card_id)
VALUES (
    '{card['slug']}',
    {card['id']}
);
""")

    return suggestions


def main():
    parser = argparse.ArgumentParser(
        description='Verify data integrity for Pokemon cards in a serie',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verify_serie_cards.py 176
  python verify_serie_cards.py 176 --verbose
  python verify_serie_cards.py 176 --json
  python verify_serie_cards.py 176 --fixes > fixes.sql
        """
    )

    parser.add_argument('serie_id', type=int, help='Serie ID to verify')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show verbose output')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--fixes', action='store_true', help='Generate SQL fix suggestions')

    args = parser.parse_args()

    # Create database connection
    try:
        connection = create_connection()
        if not connection:
            print(f"{Colors.FAIL}Failed to connect to database{Colors.ENDC}")
            sys.exit(1)
    except Exception as e:
        print(f"{Colors.FAIL}Error connecting to database: {e}{Colors.ENDC}")
        sys.exit(1)

    try:
        # Analyze the serie
        analysis = analyze_cards(connection, args.serie_id, args.verbose)

        if args.json:
            # Output as JSON
            print(json.dumps(analysis, indent=2, default=str))
        elif args.fixes:
            # Output fix suggestions
            fixes = generate_fix_suggestions(analysis)
            if fixes:
                print("-- SQL Fix Suggestions")
                print(f"-- Generated: {datetime.now().isoformat()}")
                print(f"-- Serie: {analysis['summary']['serie_name']} (ID: {args.serie_id})")
                print()
                for fix in fixes:
                    print(fix)
            else:
                print("-- No fixes needed!")
        else:
            # Print formatted report
            print_report(analysis, args.verbose)

    finally:
        connection.close()


if __name__ == '__main__':
    main()
