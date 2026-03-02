"""Helpers for wrapping raw MIDI messages in BLE MIDI packets."""

from __future__ import annotations

BLE_MIDI_TIMESTAMP_MASK = 0x1FFF


def encode_ble_midi_packet(message: bytes, timestamp_ms: int) -> bytes:
    """Wrap a MIDI message in the BLE MIDI timestamp envelope."""
    if not message:
        raise ValueError("BLE MIDI packets require at least one MIDI byte")

    timestamp = timestamp_ms & BLE_MIDI_TIMESTAMP_MASK
    timestamp_high = 0x80 | ((timestamp >> 7) & 0x3F)
    timestamp_low = 0x80 | (timestamp & 0x7F)
    return bytes((timestamp_high, timestamp_low)) + message
