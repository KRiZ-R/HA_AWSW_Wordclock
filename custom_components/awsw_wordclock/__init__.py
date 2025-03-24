"""AWSW WordClock integration."""

import logging
import asyncio
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

LOGGER = logging.getLogger(__name__)
PLATFORMS = ["light"]

####
# Options Update
####
async def update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """
    Update integration options without a full reload when possible.

    If the language option changes, cancel any polling tasks, update the stored language,
    and trigger a full reload of the integration. If only the polling time changes,
    cancel the current polling task and reschedule it with the new interval.
    """
    # Get current and new polling intervals
    current_polling_time = hass.data[DOMAIN][entry.entry_id].get("polling_time", 5)
    new_polling_time = entry.options.get("polling_time", 5)

    # Get current and new language settings
    current_language = hass.data[DOMAIN][entry.entry_id].get("language")
    new_language = entry.options.get("language")

    # If language has changed, perform a full reload
    if current_language is not None and new_language != current_language:
        LOGGER.debug("Language changed from %s to %s, performing full reload", current_language, new_language)
        hass.data[DOMAIN][entry.entry_id]["language"] = new_language
        # Cancel existing polling task (if any)
        if "polling_canceller" in hass.data[DOMAIN][entry.entry_id]:
            LOGGER.debug("Cancelling existing polling task due to language change")
            hass.data[DOMAIN][entry.entry_id]["polling_canceller"]()
            hass.data[DOMAIN][entry.entry_id].pop("polling_canceller", None)
        await hass.config_entries.async_reload(entry.entry_id)
        return

    # If polling time remains unchanged, no update is needed.
    if current_polling_time == new_polling_time:
        LOGGER.debug("Polling time unchanged (%s seconds); no update needed", new_polling_time)
        return

    # Update the stored polling time.
    LOGGER.debug("Updating polling_time from %s to %s", current_polling_time, new_polling_time)
    hass.data[DOMAIN][entry.entry_id]["polling_time"] = new_polling_time

    # Cancel the current polling task if one exists before rescheduling.
    if "polling_canceller" in hass.data[DOMAIN][entry.entry_id]:
        LOGGER.debug("Cancelling existing polling task")
        hass.data[DOMAIN][entry.entry_id]["polling_canceller"]()
        hass.data[DOMAIN][entry.entry_id].pop("polling_canceller", None)

    # If light entities are available, reschedule polling with the new interval.
    if ("entities" in hass.data[DOMAIN][entry.entry_id] and
            "light" in hass.data[DOMAIN][entry.entry_id]["entities"]):
        lights = hass.data[DOMAIN][entry.entry_id]["entities"]["light"]

        async def update_light(light):
            try:
                await light.async_update()
                light.async_write_ha_state()
            except Exception as e:
                LOGGER.error("Error updating light %s: %s", light.entity_id, e)

        async def update_all(now):
            # Always grab the latest interval value
            current_poll = hass.data[DOMAIN][entry.entry_id].get("polling_time", 5)
            LOGGER.debug("Polling WordClock (all lights) using interval: %s seconds", current_poll)
            # Update all lights concurrently
            await asyncio.gather(*(update_light(light) for light in lights))

        LOGGER.info("Setting up new polling with interval of %s seconds", new_polling_time)
        canceller = async_track_time_interval(hass, update_all, timedelta(seconds=new_polling_time))
        hass.data[DOMAIN][entry.entry_id]["polling_canceller"] = canceller

        # Optionally, trigger an immediate update after rescheduling.
        await update_all(None)

####
# Standard Setup and Entry Functions
####
async def async_setup(hass: HomeAssistant, config) -> bool:
    """Set up the AWSW WordClock component."""
    # Initialize the integration data storage
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AWSW WordClock from a configuration entry."""
    session = async_get_clientsession(hass)
    # Retrieve polling time and language from the entry options (or use defaults)
    polling_time = entry.options.get("polling_time", 5)
    language = entry.options.get("language", entry.data.get("language", "German"))

    # Create and store integration state data
    hass.data[DOMAIN][entry.entry_id] = {
        "session": session,
        "polling_time": polling_time,
        "language": language,
        "entities": {}  # This will later be populated by platforms (e.g., light)
    }

    # Register a listener to update integration options on the fly.
    entry.add_update_listener(update_options)

    # Forward setup to each supported platform (here: light)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Allow a brief pause so that platforms can register their entities.
    await asyncio.sleep(0.1)
    entities = hass.data[DOMAIN][entry.entry_id].get("entities", {})
    lights = entities.get("light", [])
    if lights:
        async def update_light(light):
            try:
                await light.async_update()
                light.async_write_ha_state()
            except Exception as e:
                LOGGER.error("Error updating light %s: %s", light.entity_id, e)

        async def update_all(now):
            current_poll = hass.data[DOMAIN][entry.entry_id].get("polling_time", 5)
            LOGGER.debug("Polling WordClock (all lights) using interval: %s seconds", current_poll)
            await asyncio.gather(*(update_light(light) for light in lights))

        LOGGER.info("Setting up polling for WordClock with interval of %s seconds", polling_time)
        # Only schedule polling if not already scheduled
        if "polling_canceller" not in hass.data[DOMAIN][entry.entry_id]:
            canceller = async_track_time_interval(hass, update_all, timedelta(seconds=polling_time))
            hass.data[DOMAIN][entry.entry_id]["polling_canceller"] = canceller

    ####
    # Service Registration (optional)
    ####
    async def set_word_color(call):
        """
        Handle the service call to set the word color (and optionally brightness).

        It searches through the stored entities (by iterating over the integration's data)
        for a matching entity_id, then calls async_turn_on with the proper parameters.
        """
        entity_id = call.data.get("entity_id")
        rgb_color = call.data.get("rgb_color")
        brightness = call.data.get("brightness")  # Optional parameter

        if not entity_id or not rgb_color:
            LOGGER.error("Missing required service parameters: entity_id or rgb_color")
            return

        # Iterate through the components to find the matching entity.
        for component in hass.data.get(DOMAIN, {}).values():
            if isinstance(component, dict) and "entities" in component:
                for entity_list in component["entities"].values():
                    for entity in entity_list:
                        if entity.entity_id == entity_id and hasattr(entity, "async_turn_on"):
                            LOGGER.debug("Setting color for %s to %s with brightness %s", entity_id, rgb_color, brightness)
                            kwargs = {"rgb_color": rgb_color}
                            if brightness is not None:
                                kwargs["brightness"] = brightness
                            await entity.async_turn_on(**kwargs)
                            return

        LOGGER.error("Entity %s not found or doesn't support color/brightness", entity_id)

    # Register the service under the integration's domain.
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
            vol.Optional("brightness"): vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
        })
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a configuration entry."""
    # Unload all platforms that were forwarded.
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        # If a polling task is active, cancel it during unload.
        entry_data = hass.data[DOMAIN].pop(entry.entry_id, {})
        if "polling_canceller" in entry_data:
            LOGGER.debug("Cancelling polling task during unload")
            entry_data["polling_canceller"]()
    return unloaded