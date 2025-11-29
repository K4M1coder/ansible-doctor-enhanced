# Run CLI from source (PowerShell)
# Usage: .\scripts\run_cli.ps1 -- --help
param([Parameter(ValueFromRemainingArguments=$true)][String[]] $Args)

# Use poetry if available, otherwise fallback to python -m
if (Get-Command poetry -ErrorAction SilentlyContinue) {
    # run with poetry in the project's virtualenv
    poetry run python -m ansibledoctor.cli $Args
} else {
    python -m ansibledoctor.cli $Args
}