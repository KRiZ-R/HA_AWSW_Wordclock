"""AWSW WordClock integration."""
import logging
import asyncio
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from aiohttp import ClientSession
from .const import DOMAIN

LOGGER = logging.getLogger(__name__)
PLATFORMS = ["switch", "light"]

async def update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the integration when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_setup(hass: HomeAssistant, config) -> bool:
    """Set up the AWSW WordClock component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AWSW WordClock from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    session = ClientSession()
    
    hass.data[DOMAIN][entry.entry_id] = {
        "session": session,
        "config_entry": entry,
    }

    # Register options update listener
    entry.add_update_listener(update_options)

    # Forward the setup to each platform
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )
        
    # Set up service to control word colors
    async def set_word_color(call):
        """Handle the service call to set word color."""
        entity_id = call.data.get("entity_id")
        rgb_color = call.data.get("rgb_color")
        
        if not entity_id or not rgb_color:
            LOGGER.error("Missing required service parameters")
            return
            
        # Find the entity and set its color
        for component_entities in hass.data.get(DOMAIN, {}).values():
            for platform in component_entities.get("entities", {}).values():
                for entity in platform:
                    if entity.entity_id == entity_id and hasattr(entity, "async_turn_on"):
                        LOGGER.debug("Setting color for %s to %s", entity_id, rgb_color)
                        await entity.async_turn_on(rgb_color=rgb_color)
                        return
        
        LOGGER.error("Entity %s not found or doesn't support color", entity_id)
    
    hass.services.async_register(
        DOMAIN, 
        "set_word_color", 
        set_word_color, 
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Required("rgb_color"): vol.All(
                vol.ExactSequence((cv.byte, cv.byte, cv.byte)),
                vol.Coerce(tuple),
            ),
        })
    )
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload entities for this entry for each platform
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    
    # Remove the session
    if unloaded:
        if session := hass.data[DOMAIN][entry.entry_id].get("session"):
            await session.close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded
