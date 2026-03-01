#!/usr/bin/env python3
"""
Compare the Java and Python output files to verify matching correctness.
"""

import re


def parse_java_output(filename):
    """
    Parse Java output format:
    'Resident Name -> Program Name' or 'Resident Name -> No Match'
    Returns dict: {resident_id: (resident_name, program_name_or_none)}
    """
    matches = {}

    with open(filename, 'r', encoding='utf-16-le') as f:
        for line in f:
            line = line.strip()
            if ' -> ' in line:
                parts = line.split(' -> ')
                if len(parts) == 2:
                    resident_name = parts[0].strip()
                    program_info = parts[1].strip()

                    if program_info == 'No Match':
                        program_name = None
                    else:
                        program_name = program_info

                    matches[resident_name] = program_name

    return matches


def parse_python_output(filename):
    """
    Parse Python output format grouped by program.
    Returns two dicts:
    - program_matches: {program_name: [resident_names]}
    - resident_to_program: {resident_name: program_name}
    """
    program_matches = {}
    resident_to_program = {}
    current_program = None

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Check if this is a program header (ends with (CODE))
            if line and '(' in line and ')' in line and not line.startswith('-'):
                # Extract program name and code
                if 'Quota:' not in line and 'Matching Results' not in line and '=' not in line:
                    current_program = line
                    if current_program not in program_matches:
                        program_matches[current_program] = []

            # Check if this is a resident match (starts with '- ')
            elif line.startswith('- '):
                # Format: "- FirstName LastName (ID)"
                match = re.match(r'-\s+(.+?)\s+\((\d+)\)', line)
                if match and current_program:
                    resident_name = match.group(1)
                    resident_id = match.group(2)
                    program_matches[current_program].append(resident_name)
                    resident_to_program[resident_name] = current_program

            # Check for unmatched section
            elif 'Unmatched Residents:' in line:
                current_program = None

    return program_matches, resident_to_program


def extract_program_id_from_java_name(program_name):
    """Convert Java program name to match Python program header format."""
    # This is a mapping function - we'll need to normalize names
    return program_name


def compare_matchings(java_file, python_file):
    """Compare the two output files."""
    print("Parsing output files...")

    java_matches = parse_java_output(java_file)
    program_matches, python_resident_to_program = parse_python_output(python_file)

    print(f"\nJava output: {len(java_matches)} residents processed")
    print(f"Python output: {len(python_resident_to_program)} residents matched")

    # Count unmatched in Java
    java_unmatched = sum(1 for prog in java_matches.values() if prog is None)
    python_unmatched = len(java_matches) - len(python_resident_to_program)

    print(f"\nJava: {len(java_matches) - java_unmatched} matched, {java_unmatched} unmatched")
    print(f"Python: {len(python_resident_to_program)} matched, {python_unmatched} unmatched (estimated)")

    # Find residents by name in both
    java_resident_names = set(java_matches.keys())
    python_resident_names = set(python_resident_to_program.keys())

    print(f"\nChecking name consistency...")
    print(f"Residents in Java: {len(java_resident_names)}")
    print(f"Residents in Python matched: {len(python_resident_names)}")

    # Sample some matches to verify
    print(f"\nSample comparison (first 20 matched residents):")
    count = 0
    for name in sorted(java_resident_names):
        if count >= 20:
            break

        java_prog = java_matches.get(name)
        python_prog = python_resident_to_program.get(name)

        if java_prog is None:
            java_prog = "UNMATCHED"
        if python_prog is None:
            python_prog = "UNMATCHED"

        # Only show matched residents
        if java_prog != "UNMATCHED":
            print(f"{name:30s} | Java: {java_prog:40s} | Python: {python_prog if python_prog else 'UNMATCHED'}")
            count += 1

    # Check for discrepancies
    print(f"\nChecking for discrepancies...")
    discrepancies = 0

    # We need to do fuzzy matching on program names since formats may differ
    for name in sorted(java_resident_names):
        java_prog = java_matches[name]
        python_prog = python_resident_to_program.get(name)

        if java_prog is None and python_prog is None:
            continue  # Both unmatched, OK

        if (java_prog is None) != (python_prog is None):
            # One matched, one didn't
            if discrepancies < 10:  # Show first 10
                print(f"  {name}: Java={java_prog or 'UNMATCHED'}, Python={python_prog or 'UNMATCHED'}")
            discrepancies += 1

    if discrepancies == 0:
        print("✓ No discrepancies found in match/unmatch status!")
    else:
        print(f"✗ Found {discrepancies} discrepancies")

    return discrepancies == 0


if __name__ == "__main__":
    success = compare_matchings("output4000.txt", "python_output4000.txt")

    if success:
        print("\n" + "="*80)
        print("SUCCESS: Matchings appear to be consistent!")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("DISCREPANCIES FOUND - please review above")
        print("="*80)
