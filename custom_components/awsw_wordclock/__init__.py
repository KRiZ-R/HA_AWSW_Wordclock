"""AWSW WordClock integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from aiohttp import ClientSession
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AWSW WordClock from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Initialize the session if not already initialized
    if "session" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["session"] = ClientSession()

    # Store the entry data
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Register an update listener for options
    entry.add_update_listener(update_options)

    await hass.config_entries.async_forward_entry_setups(entry, ["switch"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["switch"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

        # Close the session if no entries are left
        if not hass.data[DOMAIN]:
            session = hass.data[DOMAIN].pop("session", None)
            if session:
                await session.close()

    return unload_ok

async def update_options(hass: HomeAssistant, config_entry: ConfigEntry):
    """Update options if changed."""
    hass.data[DOMAIN][config_entry.entry_id] = config_entry.data
