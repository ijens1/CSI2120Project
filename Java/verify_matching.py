#!/usr/bin/env python3
"""
Independent implementation of Gale-Shapley algorithm for resident-program matching.
This serves as a reference to verify the correctness of the Java implementation.
"""

import csv
import json


class Resident:
    def __init__(self, res_id, first_name, last_name, rol):
        self.id = res_id
        self.first_name = first_name
        self.last_name = last_name
        self.rol = rol  # List of program IDs in preference order
        self.next_choice = 0  # Index of next program to propose to
        self.matched_program = None

    def next_proposal(self):
        """Get the next program to propose to, or None if list exhausted."""
        if self.next_choice < len(self.rol):
            program_id = self.rol[self.next_choice]
            self.next_choice += 1
            return program_id
        return None

    def is_matched(self):
        return self.matched_program is not None


class Program:
    def __init__(self, prog_id, name, quota, rol):
        self.id = prog_id
        self.name = name
        self.quota = quota
        self.rol = rol  # List of resident IDs in preference order
        self.matched_residents = []  # Currently matched residents

    def rank_of(self, resident_id):
        """Return the rank (0-indexed) of a resident, or None if not in ROL."""
        try:
            return self.rol.index(resident_id)
        except ValueError:
            return None

    def is_full(self):
        return len(self.matched_residents) >= self.quota

    def least_preferred_match(self):
        """Return the currently matched resident with lowest preference (highest rank)."""
        if not self.matched_residents:
            return None
        worst = self.matched_residents[0]
        worst_rank = self.rank_of(worst)
        for res_id in self.matched_residents[1:]:
            rank = self.rank_of(res_id)
            if rank is not None and (worst_rank is None or rank > worst_rank):
                worst = res_id
                worst_rank = rank
        return worst

    def accept(self, resident_id):
        """Try to accept a resident proposal. Return True if accepted."""
        rank = self.rank_of(resident_id)

        # Reject if resident not in our ROL
        if rank is None:
            return False

        # Accept if not full
        if not self.is_full():
            self.matched_residents.append(resident_id)
            return True

        # If full, compare with least preferred current match
        worst = self.least_preferred_match()
        worst_rank = self.rank_of(worst)

        if worst_rank is not None and rank < worst_rank:
            # New resident is preferred, replace worst
            self.matched_residents.remove(worst)
            self.matched_residents.append(resident_id)
            return True

        return False

    def remove(self, resident_id):
        """Remove a resident from matches."""
        if resident_id in self.matched_residents:
            self.matched_residents.remove(resident_id)


def parse_rol_list(rol_string):
    """Parse a ROL string like '[A,B,C]' into a list ['A', 'B', 'C']."""
    rol_string = rol_string.strip()
    if rol_string.startswith('[') and rol_string.endswith(']'):
        rol_string = rol_string[1:-1]
    if not rol_string:
        return []
    return [item.strip() for item in rol_string.split(',')]


def load_residents(filename):
    """Load residents from CSV file."""
    residents = {}
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            res_id = row['id']
            rol = parse_rol_list(row['rol'])
            residents[res_id] = Resident(res_id, row['firstname'], row['lastname'], rol)
    return residents


def load_programs(filename):
    """Load programs from CSV file."""
    programs = {}
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            prog_id = row['id']
            quota = int(row['numberOfPos'])
            rol = parse_rol_list(row['rol'])
            programs[prog_id] = Program(prog_id, row['name'], quota, rol)
    return programs


def gale_shapley(residents, programs):
    """
    Run the Gale-Shapley algorithm.
    Returns when stable matching is achieved (no changes in an iteration).
    """
    iteration = 0
    while True:
        iteration += 1
        changes = False

        # Each unmatched resident proposes to their next choice
        for res_id, resident in residents.items():
            if not resident.is_matched():
                program_id = resident.next_proposal()

                if program_id is None:
                    continue  # Exhausted preference list

                if program_id not in programs:
                    continue  # Invalid program

                program = programs[program_id]
                accepted = program.accept(res_id)

                if accepted:
                    # Remove from old match if any
                    if resident.matched_program:
                        old_prog = programs[resident.matched_program]
                        old_prog.remove(res_id)

                    resident.matched_program = program_id
                    changes = True
                else:
                    # Check if we were previously matched to this program and got rejected
                    if resident.matched_program == program_id:
                        resident.matched_program = None
                        changes = True

        # Check for residents who were displaced
        for res_id, resident in residents.items():
            if resident.matched_program:
                program = programs[resident.matched_program]
                if res_id not in program.matched_residents:
                    # We were displaced
                    resident.matched_program = None
                    changes = True

        if not changes:
            break

    return iteration


def print_results(residents, programs):
    """Print matching results."""
    print("Matching Results:")
    print("=" * 80)

    # Group by program
    for prog_id in sorted(programs.keys()):
        program = programs[prog_id]
        print(f"\n{program.name} ({prog_id})")
        print(f"Quota: {program.quota}, Matched: {len(program.matched_residents)}")

        if program.matched_residents:
            matched = []
            for res_id in sorted(program.matched_residents):
                resident = residents[res_id]
                matched.append(f"{resident.first_name} {resident.last_name} ({res_id})")

            for match in sorted(matched):
                print(f"  - {match}")

    # Unmatched residents
    unmatched = [res for res in residents.values() if not res.is_matched()]
    if unmatched:
        print(f"\nUnmatched Residents: {len(unmatched)}")
        for resident in sorted(unmatched, key=lambda r: r.id):
            print(f"  - {resident.first_name} {resident.last_name} ({resident.id})")


def save_results(residents, programs, filename):
    """Save results to a text file in a format matching the Java output."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Matching Results:\n")
        f.write("=" * 80 + "\n")

        # Group by program
        for prog_id in sorted(programs.keys()):
            program = programs[prog_id]
            f.write(f"\n{program.name} ({prog_id})\n")
            f.write(f"Quota: {program.quota}, Matched: {len(program.matched_residents)}\n")

            if program.matched_residents:
                matched = []
                for res_id in sorted(program.matched_residents):
                    resident = residents[res_id]
                    matched.append(f"{resident.first_name} {resident.last_name} ({res_id})")

                for match in sorted(matched):
                    f.write(f"  - {match}\n")

        # Unmatched residents
        unmatched = [res for res in residents.values() if not res.is_matched()]
        if unmatched:
            f.write(f"\nUnmatched Residents: {len(unmatched)}\n")
            for resident in sorted(unmatched, key=lambda r: r.id):
                f.write(f"  - {resident.first_name} {resident.last_name} ({resident.id})\n")


def main():
    print("Loading data...")
    residents = load_residents("residents4000.csv")
    programs = load_programs("programs4000.csv")

    print(f"Loaded {len(residents)} residents and {len(programs)} programs")

    print("\nRunning Gale-Shapley algorithm...")
    iterations = gale_shapley(residents, programs)
    print(f"Algorithm completed in {iterations} iterations")

    # Calculate statistics
    total_matched = sum(1 for r in residents.values() if r.is_matched())
    total_unmatched = len(residents) - total_matched
    total_capacity = sum(p.quota for p in programs.values())
    total_filled = sum(len(p.matched_residents) for p in programs.values())

    print(f"\nStatistics:")
    print(f"  Total residents: {len(residents)}")
    print(f"  Matched: {total_matched}")
    print(f"  Unmatched: {total_unmatched}")
    print(f"  Total program capacity: {total_capacity}")
    print(f"  Total positions filled: {total_filled}")

    # Save to file
    output_file = "python_output4000.txt"
    save_results(residents, programs, output_file)
    print(f"\nResults saved to {output_file}")

    # Print to screen as well
    print_results(residents, programs)


if __name__ == "__main__":
    main()
