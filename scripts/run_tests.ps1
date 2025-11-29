# Run test suite quickly (PowerShell)
# Usage: .\scripts\run_tests.ps1 [--integration|--unit|--all]
param([string]$scope = "unit")

switch ($scope.ToLower()) {
    "unit" { $tests = "tests/unit" }
    "integration" { $tests = "tests/integration" }
    "all" { $tests = "tests" }
    default { $tests = "tests/unit" }
}

if (Get-Command poetry -ErrorAction SilentlyContinue) {
    poetry run pytest $tests -q --maxfail=1
} else {
    pytest $tests -q --maxfail=1
}