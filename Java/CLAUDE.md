# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a CSI 2120/CSI 2520 course project implementing the Gale-Shapley stable matching algorithm for resident-program 
matching (similar to the hospital residency matching problem).

## Build and Run

Compile all Java files:
```bash
javac *.java
```

Run the stable matching algorithm:
```bash
java StableMatching <residents.csv> <programs.csv>
```

## Architecture

The codebase implements a classic two-sided matching problem using the Gale-Shapley algorithm:

- **StableMatching.java**: Main entry point that orchestrates the matching process and displays results
- **GaleShapley.java**: Core algorithm engine that reads CSV files and executes the matching loop
- **Resident.java**: Represents applicants with ranked order lists (ROL) of preferred programs
- **Program.java**: Represents programs with quotas and ranked order lists of preferred residents

### Matching Flow

1. Residents are loaded with their preference lists (ROL) of program IDs
2. Programs are loaded with quotas and preference lists of resident IDs
3. The algorithm iterates until stable:
   - Unmatched residents propose to their next choice program
   - Programs accept if they have space OR if the new resident is preferred over their current worst match
   - Rejected residents remain unmatched and try their next choice in the next iteration

### Key Implementation Details

- Residents track their `nextChoice` index to iterate through their ROL
- Programs use `leastPreferred()` to identify which current match to potentially replace
- Programs only accept residents who appear in their ROL via `member()` check
- The algorithm terminates when no resident changes their match status in a full iteration (see GaleShapley.java:18-37)

## File Format

CSV files must have:
- Header row (skipped during parsing)
- For residents: `ID,FirstName,LastName,[programID1,programID2,...]`
- For programs: `ProgramID,Name,Quota,[residentID1,residentID2,...]`
