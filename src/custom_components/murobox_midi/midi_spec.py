"""Parsing helpers for converting automation-friendly strings into MIDI data."""

from __future__ import annotations

from dataclasses import dataclass
import re

TOKEN_SPLIT_RE = re.compile(r"[\s,]+")
HEX_TOKEN_RE = re.compile(r"^(?:0x)?[0-9a-fA-F]{2}$")
NOTE_TOKEN_RE = re.compile(
    r"^(?:(?P<rest>R|REST)(?:/(?P<rest_duration>\d+))?|"
    r"(?P<note>[A-Ga-g])(?P<accidental>[#b]?)(?P<octave>-?\d+)"
    r"(?:/(?P<duration>\d+))?(?:@(?P<velocity>\d{1,3}))?)$"
)

NOTE_OFFSETS = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}


@dataclass(frozen=True, slots=True)
class TimedMidiMessage:
    """A MIDI message plus the delay to wait after transmitting it."""

    data: bytes
    delay_after_ms: int = 0


def parse_midi_spec(
    spec: str,
    *,
    channel: int = 0,
    default_duration_ms: int = 250,
    default_velocity: int = 100,
) -> list[TimedMidiMessage]:
    """Parse either raw hex bytes or a note sequence into MIDI messages.

    Supported note syntax:
    - `C4`
    - `C4/180`
    - `C4/180@96`
    - `R/120` or `REST/120` for a silent delay

    Tokens can be separated by spaces or commas.
    """
    tokens = [token for token in TOKEN_SPLIT_RE.split(spec.strip()) if token]
    if not tokens:
        raise ValueError("The MIDI string is empty")

    if not 0 <= channel <= 15:
        raise ValueError("MIDI channel must be between 0 and 15")
    if default_duration_ms < 0:
        raise ValueError("Default duration must be zero or greater")
    if not 0 <= default_velocity <= 127:
        raise ValueError("Default velocity must be between 0 and 127")

    if all(HEX_TOKEN_RE.fullmatch(token) for token in tokens):
        return [TimedMidiMessage(bytes(_parse_hex_token(token) for token in tokens))]

    messages: list[TimedMidiMessage] = []
    status_note_on = 0x90 | channel
    status_note_off = 0x80 | channel

    for token in tokens:
        match = NOTE_TOKEN_RE.fullmatch(token)
        if match is None:
            raise ValueError(f"Unsupported MIDI token: {token}")

        if match.group("rest"):
            rest_duration = int(match.group("rest_duration") or default_duration_ms)
            if rest_duration < 0:
                raise ValueError("Rest durations must be zero or greater")
            messages.append(TimedMidiMessage(b"", rest_duration))
            continue

        note_number = _note_to_midi(
            match.group("note"),
            match.group("accidental"),
            int(match.group("octave")),
        )
        velocity = int(match.group("velocity") or default_velocity)
        duration_ms = int(match.group("duration") or default_duration_ms)

        if not 0 <= velocity <= 127:
            raise ValueError("Note velocity must be between 0 and 127")
        if duration_ms < 0:
            raise ValueError("Note duration must be zero or greater")

        messages.append(
            TimedMidiMessage(bytes((status_note_on, note_number, velocity)), duration_ms)
        )
        messages.append(TimedMidiMessage(bytes((status_note_off, note_number, 0))))

    return messages


def _parse_hex_token(token: str) -> int:
    """Convert a hex token into a byte value."""
    if token.lower().startswith("0x"):
        token = token[2:]
    return int(token, 16)


def _note_to_midi(note: str, accidental: str, octave: int) -> int:
    """Translate a note name into a MIDI note number."""
    offset = NOTE_OFFSETS[note.upper()]
    if accidental == "#":
        offset += 1
    elif accidental == "b":
        offset -= 1

    midi_note = ((octave + 1) * 12) + offset
    if not 0 <= midi_note <= 127:
        raise ValueError(f"Note {note}{accidental}{octave} is outside the MIDI range")
    return midi_note
