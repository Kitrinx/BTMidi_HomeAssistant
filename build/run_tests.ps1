param(
    [string]$Python = "python"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$testSupport = Join-Path $repoRoot "libraries\\test_support"
$testsPath = Join-Path $repoRoot "tests"
$configPath = Join-Path $PSScriptRoot "pytest.ini"

if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$testSupport;$env:PYTHONPATH"
}
else {
    $env:PYTHONPATH = $testSupport
}

& $Python -m pytest -c $configPath $testsPath
exit $LASTEXITCODE
