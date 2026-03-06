"""Config flow for the Muro Box BLE MIDI integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

from .const import (
    CONF_ADDRESS,
    CONF_DISCONNECT_MODE,
    CONF_IDLE_DISCONNECT_SECONDS,
    DEFAULT_DISCONNECT_MODE,
    DEFAULT_IDLE_DISCONNECT_SECONDS,
    DEFAULT_NAME,
    DISCONNECT_MODE_DELAYED,
    DISCONNECT_MODE_IMMEDIATE,
    DISCONNECT_MODE_NEVER,
    DOMAIN,
)


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

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return MuroBoxMidiOptionsFlow(config_entry)


class MuroBoxMidiOptionsFlow(config_entries.OptionsFlow):
    """Handle integration options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage post-setup options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_DISCONNECT_MODE: user_input[CONF_DISCONNECT_MODE],
                    CONF_IDLE_DISCONNECT_SECONDS: user_input[
                        CONF_IDLE_DISCONNECT_SECONDS
                    ],
                },
            )

        current_mode = self._config_entry.options.get(
            CONF_DISCONNECT_MODE,
            DEFAULT_DISCONNECT_MODE,
        )
        current_idle_seconds = int(
            self._config_entry.options.get(
                CONF_IDLE_DISCONNECT_SECONDS,
                DEFAULT_IDLE_DISCONNECT_SECONDS,
            )
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DISCONNECT_MODE,
                        default=current_mode,
                    ): vol.In(
                        {
                            DISCONNECT_MODE_IMMEDIATE: "Immediately after each chime",
                            DISCONNECT_MODE_DELAYED: "After an idle timeout",
                            DISCONNECT_MODE_NEVER: "Never (keep connected)",
                        }
                    ),
                    vol.Required(
                        CONF_IDLE_DISCONNECT_SECONDS,
                        default=current_idle_seconds,
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=3600)),
                }
            ),
        )


def _normalize_address(address: str) -> str:
    """Normalize Bluetooth addresses into a stable unique ID format."""
    return address.strip().upper()
