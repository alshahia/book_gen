#!/usr/bin/env bash
# agents-manager installer shim (Unix) — defers to Python
exec python3 "$(dirname "${BASH_SOURCE[0]}")/install.py" "$@"
