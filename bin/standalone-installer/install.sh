#!/usr/bin/env bash
# agents-manager standalone installer shim (Unix)
exec python3 "$(dirname "${BASH_SOURCE[0]}")/install.py" "$@"
