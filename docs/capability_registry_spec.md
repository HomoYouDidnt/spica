# Capability Registry Specification

## Purpose
Defines the semantic and structural expectations for SPICA capability entries.

## Required Fields
- `name`: Unique string identifier
- `tags`: List of domains (e.g., "transform", "rank", "qa")
- `path`: Import path to callable
- `schema`: I/O specification for validation
- `budgets`: { "tokens": int, "sec": float }
- `tests`: Reference to pytest or fixture verifying callable correctness
