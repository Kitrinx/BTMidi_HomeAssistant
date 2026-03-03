# Muro Box BLE MIDI Integration

This scaffold creates a Home Assistant custom integration in
`src/custom_components/murobox_midi`.

## Service format

The `murobox_midi.play_chime` service accepts either:

- Note tokens: `C5/120 E5/120 G5/240`
- Raw MIDI hex: `90 48 64 80 48 00`

Notes use the format `NOTE/OFF_MS@VELOCITY`:

- `C5` uses default duration and velocity
- `C5/120` overrides the duration in milliseconds
- `C5/120@96` overrides duration and velocity
- `R/100` inserts a 100 ms rest

## Example automation action

```yaml
- action: murobox_midi.play_chime
  target:
    device_id: 0123456789abcdef0123456789abcdef
  data:
    midi: "C5/120 E5/120 G5/240"
```

## Preset scripts

Ready-made Home Assistant scripts are provided in
`resources/home_assistant_scripts.yaml`.

Copy those script definitions into your Home Assistant `scripts.yaml` to create
triggerable actions such as:

- `script.murobox_chime1`
- `script.murobox_chime2`
- `script.murobox_chime3`
- `script.murobox_chime4`
- `script.murobox_chime5`
- `script.murobox_chime6`

Each script accepts an optional `entry_id` field. Leave it blank if you only
have one Muro Box configured; otherwise pass the integration's config entry ID.
