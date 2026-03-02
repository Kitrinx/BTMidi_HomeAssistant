"""Unit tests for BLE MIDI packet encoding."""

from __future__ import annotations

import pytest

from murobox_midi_core.ble_midi import encode_ble_midi_packet


def test_encode_ble_midi_packet_adds_timestamp_prefix() -> None:
    packet = encode_ble_midi_packet(b"\x90\x3C\x64", 0x123)

    assert packet[:2] == bytes((0x82, 0xA3))
    assert packet[2:] == b"\x90\x3C\x64"


def test_encode_ble_midi_packet_wraps_timestamp_to_13_bits() -> None:
    wrapped = encode_ble_midi_packet(b"\x80\x3C\x00", 0x2001)
    base = encode_ble_midi_packet(b"\x80\x3C\x00", 0x0001)

    assert wrapped[:2] == base[:2]


def test_encode_ble_midi_packet_rejects_empty_messages() -> None:
    with pytest.raises(ValueError, match="at least one MIDI byte"):
        encode_ble_midi_packet(b"", 0)
