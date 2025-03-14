"""Platform for light integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import aiohttp

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the WordClock Light platform."""
    ip_address = config_entry.data["ip"]

    async_add_entities([
        WordClockTimeLight(ip_address),
        WordClockBackgroundLight(ip_address)
    ])

class WordClockBaseLight(LightEntity):
    """Base class for WordClock lights."""

    def __init__(self, ip_address: str) -> None:
        """Initialize the light."""
        self._ip_address = ip_address
        self._attr_is_on = True
        self._attr_brightness = 255
        self._attr_rgb_color = (255, 255, 255)
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_color_mode = ColorMode.RGB

    async def _send_request(self, url: str) -> None:
        """Send request to WordClock."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            "Error communicating with WordClock: %s", response.status
                        )
        except aiohttp.ClientError as err:
            _LOGGER.error("Error communicating with WordClock: %s", err)

class WordClockTimeLight(WordClockBaseLight):
    """Representation of WordClock Time Light."""

    def __init__(self, ip_address: str) -> None:
        """Initialize the light."""
        super().__init__(ip_address)
        self._attr_unique_id = f"wordclock_{ip_address}_time"
        self._attr_name = "WordClock Time"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        if ATTR_RGB_COLOR in kwargs:
            self._attr_rgb_color = kwargs[ATTR_RGB_COLOR]
        if ATTR_BRIGHTNESS in kwargs:
            self._attr_brightness = kwargs[ATTR_BRIGHTNESS]

        r, g, b = self._attr_rgb_color
        brightness_pct = int(self._attr_brightness / 255 * 100)

        url = f"http://{self._ip_address}:2023/config?R-Time={r}&G-Time={g}&B-Time={b}&Bright={brightness_pct}"
        await self._send_request(url)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        url = f"http://{self._ip_address}:2023/config?R-Time=0&G-Time=0&B-Time=0"
        await self._send_request(url)
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for this light."""
        # In a future update, implement status fetching logic here
        pass

class WordClockBackgroundLight(WordClockBaseLight):
    """Representation of WordClock Background Light."""

    def __init__(self, ip_address: str) -> None:
        """Initialize the light."""
        super().__init__(ip_address)
        self._attr_unique_id = f"wordclock_{ip_address}_background"
        self._attr_name = "WordClock Background"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        if ATTR_RGB_COLOR in kwargs:
            self._attr_rgb_color = kwargs[ATTR_RGB_COLOR]
        if ATTR_BRIGHTNESS in kwargs:
            self._attr_brightness = kwargs[ATTR_BRIGHTNESS]

        r, g, b = self._attr_rgb_color
        brightness_pct = int(self._attr_brightness / 255 * 100)

        url = f"http://{self._ip_address}:2023/config?R-Back={r}&G-Back={g}&B-Back={b}&Bright={brightness_pct}"
        await self._send_request(url)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        url = f"http://{self._ip_address}:2023/config?R-Back=0&G-Back=0&B-Back=0"
        await self._send_request(url)
        self.async_write_ha_state()

    async def async_update(self):
        """Fetch new state data for this light."""
        # In a future update, implement status fetching logic here
        pass