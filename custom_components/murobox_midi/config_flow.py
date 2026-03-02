"""Config flow for the Muro Box BLE MIDI integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME

from .const import CONF_ADDRESS, DEFAULT_NAME, DOMAIN


class MuroBoxMidiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Support manual setup and Bluetooth discovery."""

    VERSION = 1

    _discovered_address: str | None = None
    _discovered_name: str | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the manual setup flow."""
        if user_input is not None:
            address = _normalize_address(user_input[CONF_ADDRESS])
            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()

            name = user_input.get(CONF_NAME) or DEFAULT_NAME
            return self.async_create_entry(
                title=name,
                data={
                    CONF_ADDRESS: address,
                    CONF_NAME: name,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): str,
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                }
            ),
        )

    async def async_step_bluetooth(self, discovery_info):
        """Handle setup triggered from Bluetooth discovery."""
        address = _normalize_address(discovery_info.address)
        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()

        self._discovered_address = address
        self._discovered_name = discovery_info.name or DEFAULT_NAME
        self.context["title_placeholders"] = {
            "name": self._discovered_name,
            "address": address,
        }
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Confirm a Bluetooth-discovered device."""
        if self._discovered_address is None:
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            return self.async_create_entry(
                title=self._discovered_name or DEFAULT_NAME,
                data={
                    CONF_ADDRESS: self._discovered_address,
                    CONF_NAME: self._discovered_name or DEFAULT_NAME,
                },
            )

        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={
                "name": self._discovered_name or DEFAULT_NAME,
                "address": self._discovered_address,
            },
        )


def _normalize_address(address: str) -> str:
    """Normalize Bluetooth addresses into a stable unique ID format."""
    return address.strip().upper()
