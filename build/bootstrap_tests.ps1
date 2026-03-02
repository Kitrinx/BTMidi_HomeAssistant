param(
    [string]$Python = "python"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$target = Join-Path $repoRoot "libraries\\test_support"
$requirements = Join-Path $PSScriptRoot "requirements-dev.txt"

& $Python -m pip install --disable-pip-version-check --target $target -r $requirements
exit $LASTEXITCODE
