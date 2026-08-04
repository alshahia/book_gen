#!/usr/bin/env bash
# agents-manager CLI shim (Unix) — defers to Python
exec python3 "$(dirname "${BASH_SOURCE[0]}")/agents-manager.py" "$@"
