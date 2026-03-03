# Libraries

Runtime packages such as `bluetooth`, `bleak`, and `voluptuous` are expected to
come from the Home Assistant environment that loads the custom integration.

When you run `build/bootstrap_tests.ps1`, it installs a temporary local pytest
toolchain into `libraries/test_support` without modifying the system Python
environment.

Use `build/requirements-dev.txt` to refresh that test-only environment. If you
later need additional vendored helpers or protocol tooling, place them here.
