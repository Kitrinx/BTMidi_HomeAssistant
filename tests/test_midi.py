"""Unit tests for the MIDI string parser."""

from __future__ import annotations

import pytest

from murobox_midi_core.midi import TimedMidiMessage, parse_midi_spec


def test_parse_note_sequence_creates_note_on_and_off_pairs() -> None:
    messages = parse_midi_spec("C4/100@90 E4/150")

    assert messages == [
        TimedMidiMessage(bytes((0x90, 60, 90)), 100),
        TimedMidiMessage(bytes((0x80, 60, 0)), 0),
        TimedMidiMessage(bytes((0x90, 64, 100)), 150),
        TimedMidiMessage(bytes((0x80, 64, 0)), 0),
    ]


def test_parse_rest_token_inserts_a_delay() -> None:
    messages = parse_midi_spec("R/75 G4/80")

    assert messages[0] == TimedMidiMessage(b"", 75)
    assert messages[1] == TimedMidiMessage(bytes((0x90, 67, 100)), 80)
    assert messages[2] == TimedMidiMessage(bytes((0x80, 67, 0)), 0)


def test_parse_hex_string_returns_single_raw_message() -> None:
    messages = parse_midi_spec("90 3C 64 80 3C 00")

    assert messages == [TimedMidiMessage(bytes.fromhex("90 3C 64 80 3C 00"), 0)]


def test_parse_flat_note_maps_to_expected_midi_number() -> None:
    messages = parse_midi_spec("Bb3/60")

    assert messages[0] == TimedMidiMessage(bytes((0x90, 58, 100)), 60)


def test_parse_invalid_token_raises() -> None:
    with pytest.raises(ValueError, match="Unsupported MIDI token"):
        parse_midi_spec("not_a_note")
