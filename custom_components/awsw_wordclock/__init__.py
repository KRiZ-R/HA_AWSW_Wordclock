"""AWSW WordClock integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from aiohttp import ClientSession
from .const import DOMAIN
from .services import async_setup_services, async_unload_services

async def async_setup(hass: HomeAssistant, config) -> bool:
    """Set up the AWSW WordClock component."""
    hass.data.setdefault(DOMAIN, {})

    # Set up services
    await async_setup_services(hass)

    return True

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

    # Set up both switch and light platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["switch", "light"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if entry.entry_id in hass.data[DOMAIN]:
        session = hass.data[DOMAIN][entry.entry_id].get("session")
        if session:
            await session.close()

        # Unload both switch and light platforms
        unload_ok = await hass.config_entries.async_unload_platforms(entry, ["switch", "light"])
        if unload_ok:
            hass.data[DOMAIN].pop(entry.entry_id)
        return unload_ok
    return False

async def async_unload(hass: HomeAssistant):
    """Unload the AWSW WordClock component."""
    await async_unload_services(hass)

async def update_options(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options updates dynamically."""
    hass.data[DOMAIN][config_entry.entry_id]["config_entry"] = config_entry
    await hass.config_entries.async_reload(config_entry.entry_id)
