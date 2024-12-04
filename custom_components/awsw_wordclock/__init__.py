"""AWSW WordClock integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from aiohttp import ClientSession
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AWSW WordClock from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    if entry.entry_id not in hass.data[DOMAIN]:
        hass.data[DOMAIN][entry.entry_id] = {
            "config_entry": entry,
            "session": ClientSession(),
        }

    # Register options update listener
    entry.add_update_listener(update_options)

    await hass.config_entries.async_forward_entry_setups(entry, ["switch"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if entry.entry_id in hass.data[DOMAIN]:
        session = hass.data[DOMAIN][entry.entry_id].get("session")
        if session:
            await session.close()

        unload_ok = await hass.config_entries.async_unload_platforms(entry, ["switch"])
        if unload_ok:
            hass.data[DOMAIN].pop(entry.entry_id)
        return unload_ok
    return False

async def update_options(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options updates dynamically."""
    hass.data[DOMAIN][config_entry.entry_id]["config_entry"] = config_entry
    await hass.config_entries.async_reload(config_entry.entry_id)
