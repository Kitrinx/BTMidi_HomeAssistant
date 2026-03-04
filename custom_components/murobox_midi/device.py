"""BLE client wrapper for sending MIDI messages to a Muro Box device."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from dataclasses import dataclass
import time

from bleak import BleakClient
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .ble_midi import encode_ble_midi_packet
from .const import BLE_MIDI_CHARACTERISTIC_UUID, DOMAIN
from .midi_spec import TimedMidiMessage, parse_midi_spec


class MuroBoxClient:
    """Thin async BLE MIDI client for one Muro Box device."""

    def __init__(self, hass: HomeAssistant, address: str, name: str) -> None:
        self.hass = hass
        self.address = address
        self.name = name
        self._client: BleakClient | None = None
        self._connect_lock = asyncio.Lock()
        self._play_lock = asyncio.Lock()

    async def async_play_spec(self, spec: str) -> None:
        """Parse and send an automation-friendly MIDI string."""
        await self.async_play_messages(parse_midi_spec(spec))

    async def async_play_messages(self, messages: list[TimedMidiMessage]) -> None:
        """Send a sequence of timed MIDI messages."""
        async with self._play_lock:
            client = await self._async_ensure_connected()
            try:
                for timed_message in messages:
                    if timed_message.data:
                        try:
                            await self._async_write_message(client, timed_message.data)
                        except Exception as err:
                            raise HomeAssistantError(
                                f"Unable to send BLE MIDI data to {self.name}"
                            ) from err

                    if timed_message.delay_after_ms:
                        await asyncio.sleep(timed_message.delay_after_ms / 1000)
            except Exception:
                await self.async_disconnect()
                raise

            # Keep the BLE session open after playback so we can test whether
            # an explicit all-channel "all sound off" is enough to stop motion.
            with suppress(Exception):
                await self._async_send_cleanup(client)
                await self.async_disconnect()

    async def async_disconnect(self) -> None:
        """Tear down the BLE connection if one is open."""
        async with self._connect_lock:
            if self._client is None:
                return

            client, self._client = self._client, None
            with suppress(Exception):
                if client.is_connected:
                    await client.disconnect()

    async def _async_ensure_connected(self) -> BleakClient:
        """Connect to the Muro Box when required."""
        async with self._connect_lock:
            if self._client is not None and self._client.is_connected:
                return self._client

            ble_device = bluetooth.async_ble_device_from_address(
                self.hass,
                self.address,
                True,
            )
            if ble_device is None:
                raise HomeAssistantError(
                    f"{self.name} is not available from Home Assistant Bluetooth right now"
                )

            client = BleakClient(ble_device, timeout=15.0)
            try:
                await client.connect()
            except Exception as err:
                raise HomeAssistantError(
                    f"Unable to connect to {self.name} over Bluetooth"
                ) from err

            self._client = client
            return client

    async def _async_write_message(self, client: BleakClient, message: bytes) -> None:
        """Encode and send a single raw MIDI message."""
        packet = encode_ble_midi_packet(
            message,
            int(time.monotonic() * 1000),
        )
        await client.write_gatt_char(
            BLE_MIDI_CHARACTERISTIC_UUID,
            packet,
            response=False,
        )

    async def _async_send_cleanup(self, client: BleakClient) -> None:
        """Send a best-effort stop sequence after playback."""
        for cleanup_message in _cleanup_messages():
            await self._async_write_message(client, cleanup_message)


@dataclass(slots=True)
class MuroBoxRuntime:
    """Runtime objects stored per config entry."""

    entry_id: str
    address: str
    name: str
    client: MuroBoxClient

    @property
    def device_identifiers(self) -> set[tuple[str, str]]:
        """Return the Home Assistant device identifiers for this runtime."""
        return {(DOMAIN, self.entry_id)}


def _cleanup_messages() -> tuple[bytes, ...]:
    """Broadcast All Sound Off on every MIDI channel."""
    return tuple(
        bytes((0xB0 | channel, 0x78, 0x00))
        for channel in range(16)
    )
