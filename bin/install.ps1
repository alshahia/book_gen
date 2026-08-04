# Backward-compat shim (v0.9.x). v0.10.0+ delegates everything to agents-manager.
[CmdletBinding()]
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$AllArgs)
& (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "agents-manager.ps1") install @AllArgs