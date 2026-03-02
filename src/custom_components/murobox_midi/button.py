"""Diagnostic button entities for the Muro Box BLE MIDI integration."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_TEST_CHIME, DEVICE_MANUFACTURER, DEVICE_MODEL, DOMAIN
from .device import MuroBoxRuntime


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the integration's entities for a config entry."""
    runtime: MuroBoxRuntime = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MuroBoxTestChimeButton(runtime)])


class MuroBoxTestChimeButton(ButtonEntity):
    """Button that plays a built-in chime for quick validation."""

    _attr_has_entity_name = True
    _attr_name = "Test chime"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, runtime: MuroBoxRuntime) -> None:
        self._runtime = runtime
        self._attr_unique_id = f"{runtime.entry_id}_test_chime"

    @property
    def device_info(self) -> DeviceInfo:
        """Expose the parent device information."""
        return DeviceInfo(
            identifiers=self._runtime.device_identifiers,
            name=self._runtime.name,
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
        )

    async def async_press(self) -> None:
        """Play a known-good chime for validation."""
        await self._runtime.client.async_play_spec(DEFAULT_TEST_CHIME)
