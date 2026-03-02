# Libraries

Runtime packages such as `bluetooth`, `bleak`, and `voluptuous` are expected to
come from the Home Assistant environment that loads the custom integration.

`libraries/test_support` contains the locally installed pytest toolchain used to
run the unit tests without modifying the system Python environment.

Use `build/requirements-dev.txt` to refresh that test-only environment. If you
later need additional vendored helpers or protocol tooling, place them here.
