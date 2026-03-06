"""Home Assistant integration for sending BLE MIDI chimes to a Muro Box N-20."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .const import (
    CONF_ADDRESS,
    CONF_DISCONNECT_MODE,
    CONF_ENTRY_ID,
    CONF_IDLE_DISCONNECT_SECONDS,
    CONF_MIDI,
    DEFAULT_DISCONNECT_MODE,
    DEFAULT_IDLE_DISCONNECT_SECONDS,
    DEFAULT_NAME,
    DEVICE_MANUFACTURER,
    DEVICE_MODEL,
    DOMAIN,
    SERVICE_PLAY_CHIME,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall

    from .device import MuroBoxClient


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the integration component."""
    hass.data.setdefault(DOMAIN, {})

    if not hass.services.has_service(DOMAIN, SERVICE_PLAY_CHIME):
        hass.services.async_register(
            DOMAIN,
            SERVICE_PLAY_CHIME,
            _build_play_service_handler(hass),
            schema=_service_schema(),
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    from homeassistant.const import CONF_NAME
    from homeassistant.helpers import device_registry as dr

    from .device import MuroBoxClient, MuroBoxRuntime

    address = entry.data[CONF_ADDRESS]
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    disconnect_mode = entry.options.get(CONF_DISCONNECT_MODE, DEFAULT_DISCONNECT_MODE)
    idle_disconnect_seconds = int(
        entry.options.get(
            CONF_IDLE_DISCONNECT_SECONDS,
            DEFAULT_IDLE_DISCONNECT_SECONDS,
        )
    )
    runtime = MuroBoxRuntime(
        entry_id=entry.entry_id,
        address=address,
        name=name,
        client=MuroBoxClient(
            hass,
            address,
            name,
            disconnect_mode=disconnect_mode,
            idle_disconnect_seconds=idle_disconnect_seconds,
        ),
    )
    hass.data[DOMAIN][entry.entry_id] = runtime
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers=runtime.device_identifiers,
        connections={("bluetooth", address.lower())},
        manufacturer=DEVICE_MANUFACTURER,
        model=DEVICE_MODEL,
        name=name,
    )

    await hass.config_entries.async_forward_entry_setups(entry, _platforms())
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, _platforms())
    if not unload_ok:
        return False

    runtime = hass.data[DOMAIN].pop(entry.entry_id)
    await runtime.client.async_disconnect()
    return True


def _build_play_service_handler(hass: HomeAssistant):
    """Create the play_chime service handler."""

    async def async_handle_play_chime(call: ServiceCall) -> None:
        clients = _resolve_target_clients(hass, call)
        for client in clients:
            await client.async_play_spec(call.data[CONF_MIDI])

    return async_handle_play_chime


def _resolve_target_clients(
    hass: HomeAssistant,
    call: ServiceCall,
) -> list[MuroBoxClient]:
    """Find the runtime clients targeted by a service call."""
    from homeassistant.const import ATTR_DEVICE_ID
    from homeassistant.exceptions import HomeAssistantError
    from homeassistant.helpers import device_registry as dr

    runtimes = hass.data.get(DOMAIN, {})
    if not runtimes:
        raise HomeAssistantError("No Muro Box devices are configured")

    entry_id = call.data.get(CONF_ENTRY_ID)
    if entry_id:
        runtime = runtimes.get(entry_id)
        if runtime is None:
            raise HomeAssistantError(f"Unknown config entry: {entry_id}")
        return [runtime.client]

    raw_device_ids = call.data.get(ATTR_DEVICE_ID)
    if raw_device_ids:
        if isinstance(raw_device_ids, str):
            device_ids = [raw_device_ids]
        else:
            device_ids = list(raw_device_ids)

        device_registry = dr.async_get(hass)
        clients: list[MuroBoxClient] = []
        seen_entry_ids: set[str] = set()

        for device_id in device_ids:
            device = device_registry.async_get(device_id)
            if device is None:
                continue

            for config_entry_id in device.config_entries:
                if config_entry_id in seen_entry_ids:
                    continue
                runtime = runtimes.get(config_entry_id)
                if runtime is None:
                    continue

                clients.append(runtime.client)
                seen_entry_ids.add(config_entry_id)
                break

        if clients:
            return clients
        raise HomeAssistantError("The selected device is not managed by this integration")

    if len(runtimes) == 1:
        return [next(iter(runtimes.values())).client]

    raise HomeAssistantError(
        "Specify entry_id or target a Muro Box device when more than one device is configured"
    )


def _platforms():
    """Return the platforms used by this integration."""
    from homeassistant.const import Platform

    return [Platform.BUTTON]


def _service_schema():
    """Build the play_chime service schema lazily."""
    import voluptuous as vol

    return vol.Schema(
        {
            vol.Optional(CONF_ENTRY_ID): str,
            vol.Required(CONF_MIDI): str,
        },
        extra=vol.ALLOW_EXTRA,
    )


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options are changed from the UI."""
    await hass.config_entries.async_reload(entry.entry_id)
