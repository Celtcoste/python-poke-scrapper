#!/usr/bin/env python3
"""
Test script for clean_pokemon_name function
Tests the removal of Mega prefixes and variant suffixes
"""

import re

def clean_pokemon_name(card_name: str) -> str:
    """
    Extract base pokemon name from card name by removing variant prefixes and suffixes.
    Handles prefixes: Méga-, M-, M (Mega evolutions)
    Handles suffixes: -ex, -EX, -GX, ex, EX, GX, V, VMAX, VSTAR, X, Y, etc.
    """
    # First, remove Mega/M prefixes
    # Matches: "Méga-", "Mega-", "M-", "M " at the start of the name
    prefix_pattern = r'^(Méga[\s\-]|Mega[\s\-]|M[\s\-])'
    cleaned_name = re.sub(prefix_pattern, '', card_name, flags=re.IGNORECASE).strip()

    # Then, remove variant suffixes
    # Matches: -ex, -EX, -GX, ex, EX, GX, V, VMAX, VSTAR, BREAK, Prism Star, etc.
    suffix_pattern = r'[\s\-]*(ex|EX|GX|V|VMAX|VSTAR|BREAK|Prism[\s\-]?Star|☆|★).*$'
    cleaned_name = re.sub(suffix_pattern, '', cleaned_name).strip()

    # Finally, remove single-letter variant indicators (X, Y, etc.) at the end
    # Matches: " X", " Y", "-X", "-Y" at the end of the name
    # Common for Mega evolutions like "Charizard X" or "Mewtwo Y"
    variant_letter_pattern = r'[\s\-]+[XY]$'
    cleaned_name = re.sub(variant_letter_pattern, '', cleaned_name, flags=re.IGNORECASE).strip()

    return cleaned_name


# Test cases
test_cases = [
    # Original failing case
    ("Méga-Scarhino-ex", "Scarhino"),

    # Mega Pokemon with X/Y variants (CRITICAL FIX)
    ("Méga-Dracaufeu X-ex", "Dracaufeu"),
    ("Méga-Dracaufeu Y-ex", "Dracaufeu"),
    ("Mega-Charizard X-EX", "Charizard"),
    ("Mega-Charizard Y-EX", "Charizard"),
    ("M-Mewtwo X-EX", "Mewtwo"),
    ("M-Mewtwo Y-EX", "Mewtwo"),
    ("Méga-Dracaufeu X", "Dracaufeu"),
    ("Charizard X", "Charizard"),
    ("Mewtwo Y", "Mewtwo"),

    # Other Mega Pokemon with -ex
    ("Méga-Diancie-ex", "Diancie"),
    ("Méga-Ectoplasma-ex", "Ectoplasma"),
    ("Méga-Sharpedo-ex", "Sharpedo"),
    ("Méga-Lockpin-ex", "Lockpin"),

    # English variants
    ("Mega-Charizard-EX", "Charizard"),
    ("M-Charizard-EX", "Charizard"),
    ("M Charizard-EX", "Charizard"),

    # Regular Pokemon (should not be affected)
    ("Pikachu", "Pikachu"),
    ("Dracaufeu", "Dracaufeu"),
    ("Scarhino", "Scarhino"),

    # Pokemon with -ex suffix only
    ("Pikachu-ex", "Pikachu"),
    ("Dracaufeu-ex", "Dracaufeu"),

    # Other variant suffixes
    ("Charizard-GX", "Charizard"),
    ("Pikachu V", "Pikachu"),
    ("Pikachu VMAX", "Pikachu"),
    ("Pikachu VSTAR", "Pikachu"),
    ("Zoroark BREAK", "Zoroark"),

    # Combined Mega + other suffixes
    ("Méga-Rayquaza-GX", "Rayquaza"),
    ("Mega Charizard VMAX", "Charizard"),

    # Edge cases
    ("M-Tyranitar ex", "Tyranitar"),
    ("Méga-Ampharos-ex", "Ampharos"),
]

def run_tests():
    print("Testing clean_pokemon_name function")
    print("=" * 80)

    passed = 0
    failed = 0

    for input_name, expected_output in test_cases:
        actual_output = clean_pokemon_name(input_name)
        status = "✓ PASS" if actual_output == expected_output else "✗ FAIL"

        if actual_output == expected_output:
            passed += 1
            print(f"{status} | '{input_name}' -> '{actual_output}'")
        else:
            failed += 1
            print(f"{status} | '{input_name}'")
            print(f"       Expected: '{expected_output}'")
            print(f"       Got:      '{actual_output}'")

    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

    if failed == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(run_tests())
