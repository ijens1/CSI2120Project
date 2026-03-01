#!/usr/bin/env python3
"""
Compare matchings by resident ID rather than name.
"""

import re
import csv


def load_resident_names(residents_csv):
    """Load mapping of resident ID to full name."""
    id_to_name = {}
    with open(residents_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            res_id = row['id']
            full_name = f"{row['firstname']} {row['lastname']}"
            id_to_name[res_id] = full_name
    return id_to_name


def parse_java_output_by_id(filename, id_to_name):
    """
    Parse Java output and map to resident IDs.
    Returns dict: {resident_id: program_name_or_none}
    """
    name_to_ids = {}
    for res_id, name in id_to_name.items():
        if name not in name_to_ids:
            name_to_ids[name] = []
        name_to_ids[name].append(res_id)

    matches_by_id = {}

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

                    # Map name to ID(s)
                    res_ids = name_to_ids.get(resident_name, [])
                    for res_id in res_ids:
                        matches_by_id[res_id] = program_name

    return matches_by_id


def parse_python_output_by_id(filename):
    """
    Parse Python output and extract resident IDs.
    Returns dict: {resident_id: program_name}
    """
    resident_to_program = {}
    current_program = None

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Check if this is a program header
            if line and '(' in line and ')' in line and not line.startswith('-'):
                if 'Quota:' not in line and 'Matching Results' not in line and '=' not in line:
                    current_program = line

            # Check if this is a resident match
            elif line.startswith('- '):
                # Format: "- FirstName LastName (ID)"
                match = re.match(r'-\s+(.+?)\s+\((\d+)\)', line)
                if match and current_program:
                    resident_id = match.group(2)
                    resident_to_program[resident_id] = current_program

            # Check for unmatched section
            elif 'Unmatched Residents:' in line:
                current_program = None

    return resident_to_program


def normalize_program_name(prog_name):
    """Remove program code from Python output for comparison."""
    if prog_name and '(' in prog_name:
        # Remove trailing (CODE)
        return prog_name.rsplit('(', 1)[0].strip()
    return prog_name


def compare_by_id(java_file, python_file, residents_csv):
    """Compare matchings using resident IDs."""
    print("Loading resident data...")
    id_to_name = load_resident_names(residents_csv)
    print(f"Loaded {len(id_to_name)} residents")

    print("\nParsing Java output...")
    java_matches = parse_java_output_by_id(java_file, id_to_name)
    print(f"Java: {len(java_matches)} residents found in output")

    print("\nParsing Python output...")
    python_matches = parse_python_output_by_id(python_file)
    print(f"Python: {len(python_matches)} residents matched")

    # Count matched/unmatched
    java_matched = sum(1 for prog in java_matches.values() if prog is not None)
    python_matched = len(python_matches)

    print(f"\nJava: {java_matched} matched, {len(java_matches) - java_matched} unmatched")
    print(f"Python: {python_matched} matched")

    # Compare all residents
    all_ids = set(id_to_name.keys())
    matched_ids = 0
    mismatched_ids = 0
    mismatches = []

    print(f"\nComparing {len(all_ids)} residents...")

    for res_id in sorted(all_ids):
        java_prog = java_matches.get(res_id)
        python_prog = python_matches.get(res_id)

        # Normalize Python program name
        python_prog_normalized = normalize_program_name(python_prog) if python_prog else None

        # Both unmatched
        if java_prog is None and python_prog is None:
            matched_ids += 1
            continue

        # Both matched to same program
        if java_prog and python_prog_normalized:
            if java_prog == python_prog_normalized:
                matched_ids += 1
                continue

        # Mismatch
        mismatched_ids += 1
        resident_name = id_to_name.get(res_id, "Unknown")
        mismatches.append({
            'id': res_id,
            'name': resident_name,
            'java': java_prog or "UNMATCHED",
            'python': python_prog or "UNMATCHED"
        })

    print(f"\nResults:")
    print(f"  Matching: {matched_ids}")
    print(f"  Mismatches: {mismatched_ids}")

    if mismatched_ids > 0:
        print(f"\nShowing all {len(mismatches)} mismatches:")
        for m in mismatches[:50]:  # Show first 50
            print(f"  {m['id']:10s} {m['name']:30s} | Java: {m['java']:40s} | Python: {m['python']}")

        if len(mismatches) > 50:
            print(f"  ... and {len(mismatches) - 50} more")

    # Calculate percentage
    match_rate = (matched_ids / len(all_ids)) * 100
    print(f"\nMatch rate: {match_rate:.2f}%")

    if mismatched_ids == 0:
        print("\n" + "="*80)
        print("SUCCESS: All matchings are identical!")
        print("="*80)
        return True
    else:
        print("\n" + "="*80)
        print(f"FOUND {mismatched_ids} DIFFERENCES - see above for details")
        print("="*80)
        return False


if __name__ == "__main__":
    compare_by_id("output4000.txt", "python_output4000.txt", "residents4000.csv")
