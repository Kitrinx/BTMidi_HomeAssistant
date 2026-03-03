# Muro Box BLE MIDI for Home Assistant

Custom Home Assistant integration for sending Bluetooth Low Energy MIDI chimes
to a Muro Box N-20 music box.

This repository is structured for two use cases:

- `src/` contains the development source and tests.
- `custom_components/murobox_midi/` contains the HACS-ready distribution copy.

## Features

- Config flow with manual Bluetooth address entry and Bluetooth discovery.
- `murobox_midi.play_chime` service for automations.
- Note-string input such as `C5/120 E5/120 G5/240`.
- Raw MIDI hex input such as `90 48 64 80 48 00`.
- Diagnostic button entity to trigger a built-in test chime.

## Install with HACS

1. In Home Assistant, open HACS.
2. Add this repository as a custom repository.
3. Set the repository type to `Integration`.
4. Install `Muro Box BLE MIDI`.
5. Restart Home Assistant.
6. Add the integration from `Settings -> Devices & Services`.

## Usage

Example automation action:

```yaml
- action: murobox_midi.play_chime
  target:
    device_id: 0123456789abcdef0123456789abcdef
  data:
    midi: "C5/120 E5/120 G5/240"
```

Supported MIDI formats:

- Note tokens: `C5/120 E5/120 G5/240`
- Raw MIDI hex: `90 48 64 80 48 00`

Notes use `NOTE/DURATION_MS@VELOCITY`:

- `C5`
- `C5/120`
- `C5/120@96`
- `R/100` for a rest

Preset Home Assistant scripts for six longer notification chimes are included in
[resources/home_assistant_scripts.yaml](C:/Users/Kitrinx/workspace/kitrinx/btmidi_homeassistant/resources/home_assistant_scripts.yaml).
Copy those entries into your Home Assistant `scripts.yaml`, then call
`script.murobox_chime1` through `script.murobox_chime6` from automations.

## Development

Bootstrap the local test environment:

```powershell
.\build\bootstrap_tests.ps1
```

Run the tests:

```powershell
.\build\run_tests.ps1
```

If you change files under `src/custom_components/murobox_midi`, sync the HACS
copy before publishing:

```powershell
.\build\sync_hacs_package.ps1
```

## License

MIT. See [LICENSE](LICENSE).
