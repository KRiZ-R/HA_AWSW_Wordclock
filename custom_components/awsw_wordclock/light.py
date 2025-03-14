"""Light platform for AWSW WordClock."""
import logging
from typing import Any, Dict, List, Optional, Tuple
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up WordClock lights based on config entry."""
    ip_address = entry.data["ip_address"]
    device_id = f"wordclock_{ip_address.replace('.', '_')}"
    session = hass.data[DOMAIN][entry.entry_id]["session"]
    
    LOGGER.debug("Setting up WordClock lights for IP: %s", ip_address)
    
    lights = [
        WordClockTimeLight(ip_address, device_id, session),
        WordClockBackgroundLight(ip_address, device_id, session),
    ]
    
    async_add_entities(lights)
    
    # Store entities in hass.data for service access
    if "entities" not in hass.data[DOMAIN][entry.entry_id]:
        hass.data[DOMAIN][entry.entry_id]["entities"] = {}
    
    hass.data[DOMAIN][entry.entry_id]["entities"]["light"] = lights
    LOGGER.debug("Added %d light entities for WordClock", len(lights))


class WordClockBaseLight(LightEntity):
    """Base class for WordClock lights."""

    def __init__(self, ip_address, device_id, session):
        """Initialize the light."""
        self._ip_address = ip_address
        self._device_id = device_id
        self._session = session
        self._state = True  # Start on by default
        self._brightness = 255
        self._rgb_color = (255, 255, 255)
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_color_mode = ColorMode.RGB
        
    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": f"WordClock ({self._ip_address})",
            "manufacturer": "AWSW",
            "model": "WordClock",
        }
        
    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._state
        
    @property
    def brightness(self) -> int:
        """Return the brightness of this light."""
        return self._brightness
        
    @property
    def rgb_color(self) -> Tuple[int, int, int]:
        """Return the rgb color value [int, int, int]."""
        return self._rgb_color
        
    async def _send_request(self, url):
        """Send request to the WordClock."""
        try:
            LOGGER.debug("Sending request to: %s", url)
            async with self._session.get(url) as response:
                if response.status != 200:
                    LOGGER.error("Failed to send request to %s, HTTP %d", url, response.status)
                    return False
                return True
        except Exception as e:
            LOGGER.error("Error sending request to %s: %s", url, e)
            return False

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