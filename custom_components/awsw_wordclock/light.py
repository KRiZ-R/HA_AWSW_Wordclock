"""Platform for WordClock lights."""
import logging
from typing import Any, Tuple
from datetime import timedelta

LOGGER = logging.getLogger(__name__)

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers import device_registry as dr, entity_registry as er
import aiohttp
import re

from .const import DOMAIN

LOGGER = logging.getLogger(__name__)

# Mapping of extra word light texts per language.
LANGUAGE_WORDS = {
    "German": {
        1: "ALARM",
        2: "GEBURTSTAG",
        3: "MÜLL RAUS BRINGEN",
        4: "AUTO",
        5: "FEIERTAG",
        6: "FORMEL1",
        7: "GELBER SACK",
        8: "URLAUB",
        9: "WERKSTATT",
        10: "ZEIT ZUM ZOCKEN",
        11: "FRISEUR",
        12: "TERMIN",
    },
    "English": {
        1: "COME HERE",
        2: "LUNCH TIME",
        3: "ALARM",
        4: "GARBAGE",
        5: "HOLIDAY",
        6: "TEMPERATURE",
        7: "DATE",
        8: "BIRTHDAY",
        9: "DOORBELL",
    },
    "Dutch": {
        1: "KOM HIER",
        2: "LUNCH TIJD",
        3: "ALARM",
        4: "AFVAL",
        5: "VAKANTIE",
        6: "TEMPERATUUR",
        7: "DATUM",
        8: "VERJAARDAG",
        9: "DEURBEL",
    },
    "French": {
        1: "ALARME",
        2: "ANNIVERSAIRE",
        3: "POUBELLE",
        4: "A TABLE",
        5: "VACANCES",
        6: "VIENS ICI",
        7: "SONNETTE",
        8: "TEMPERATURE",
        9: "DATE",
    },
    "Italian": {
        1: "VIENI QUI",
        2: "ORA DI PRANZO",
        3: "ALLARME",
        4: "VACANZA",
        5: "TEMPERATURA",
        6: "DATA",
        7: "COMPLEANNO",
        8: "CAMPANELLO",
    },
    "Swedish": {
        1: "FÖDELSEDAG",
        2: "LARM",
        3: "HÖGTID",
        4: "SEMESTER",
        5: "LADDA NER",
        6: "LUNCHTID",
        7: "KOM HIT",
        8: "DÖRRKLOCKA",
        9: "TEMPERATUR",
    },
    "Spanish": {
        1: "CUMPLEAÑOS",
        2: "ALARMA",
        3: "VACACIONES",
        4: "DÍA DE BASURA",
        5: "FECHA",
        6: "HORA DE ALMUERZO",
        7: "VEN AQUÍ",
        8: "TIMBRE",
        9: "TEMPERATURA",
    },
}

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up WordClock lights from a config entry."""
    ip_address = entry.data["ip_address"]
    language = entry.options.get("language", entry.data.get("language", "German"))
    device_id = f"wordclock_{ip_address.replace('.', '_')}"

    device_name = entry.data.get("name", f"WordClock ({ip_address})")
    object_id_prefix = device_name.lower().replace(' ', '_')

    session = hass.data[DOMAIN][entry.entry_id]["session"]
    polling_time = hass.data[DOMAIN][entry.entry_id]["polling_time"]
    lights = []

    hass.data[DOMAIN][entry.entry_id]["entry"] = entry

    LOGGER.info("Setting up WordClock lights for IP: %s with language: %s", ip_address, language)

    # Add the main WordClock lights (time text and background)
    main_lights = [
        WordClockTimeLight(ip_address, device_id, object_id_prefix, device_name, session),
        WordClockBackgroundLight(ip_address, device_id, object_id_prefix, device_name, session),
    ]
    lights.extend(main_lights)

    # Remove old word entities if language has changed
    entity_registry = er.async_get(hass)
    try:
        existing_entities = er.async_entries_for_device(
            entity_registry,
            device_id,
            include_disabled_entities=True
        )

        for entity in existing_entities:
            if entity.entity_id.startswith(f"light.{object_id_prefix}_word_"):
                try:
                    entity_registry.async_remove(entity.entity_id)
                except Exception as e:
                    LOGGER.error("Error removing entity %s: %s", entity.entity_id, str(e))
    except Exception as e:
        LOGGER.error("Error accessing entity registry: %s", str(e))

    # Fetch words for the selected language
    words = LANGUAGE_WORDS.get(language, {})
    if not words:
        LOGGER.error("Language '%s' not found. Using default (German).", language)
        words = LANGUAGE_WORDS["German"]

    # Add extra word lights
# Add extra word lights (pass device_name as well)
    for word_id, word_name in words.items():
        lights.append(WordClockExtraWordLight(ip_address, word_id, word_name, device_id, object_id_prefix, device_name, session))
        
    async_add_entities(lights)

    # Store entities in hass.data for service access
    if "entities" not in hass.data[DOMAIN][entry.entry_id]:
        hass.data[DOMAIN][entry.entry_id]["entities"] = {}

    hass.data[DOMAIN][entry.entry_id]["entities"]["light"] = lights
    LOGGER.debug("Added %d light entities for WordClock", len(lights))


class WordClockBaseLight(LightEntity):
    """Base class for WordClock lights, providing common functionality."""


    def __init__(self, ip_address, device_id, object_id_prefix, device_name, session):
        """Initialize the light."""
        self._ip_address = ip_address
        self._device_id = device_id
        self._session = session
        self._device_name = device_name
        self._state = True  # Start on by default
        self._attr_brightness = 255
        self._attr_rgb_color = (255, 255, 255)
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_color_mode = ColorMode.RGB

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "AWSW",
            "model": "WordClock",
            "configuration_url": f"http://{self._ip_address}",
        }
    
    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._state
    
    @property
    def brightness(self) -> int:
        """Return the brightness of this light."""
        return self._attr_brightness

    @property
    def rgb_color(self) -> Tuple[int, int, int]:
        """Return the RGB color value [int, int, int]."""
        return self._attr_rgb_color
    
    async def _send_request(self, url):
        """Send an HTTP GET request to the device; log any errors."""
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

    async def async_update(self) -> None:
        """Fetch and update state data for this light from /status."""
        if not hasattr(self, "_color_key_prefix"):
            return
        url = f"http://{self._ip_address}:2023/status"
        try:
            async with self._session.get(url) as response:
                if response.status != 200:
                    LOGGER.error("Failed to fetch status, HTTP %d", response.status)
                    return
                text = await response.text()
            # Expected status: "R-Time=... G-Time=... B-Time=... R-Back=... G-Back=... B-Back=... INTENSITY=50 ..."
            status_data = {}
            for token in text.split():
                if "=" in token:
                    key, value = token.split("=", 1)
                    status_data[key] = value
            prefix = self._color_key_prefix  # "Time" or "Back"
            r = int(status_data.get(f"R-{prefix}", "0"))
            g = int(status_data.get(f"G-{prefix}", "0"))
            b = int(status_data.get(f"B-{prefix}", "0"))
            self._attr_rgb_color = (r, g, b)
            # Consider the light off if color is all zeros
            self._state = not (r == 0 and g == 0 and b == 0)
            # Update brightness based on INTENSITY (0-50 mapped to 0–255)
            intensity = int(status_data.get("INTENSITY", "0"))
            self._attr_brightness = round(intensity / 50 * 255)
        except Exception as e:
            LOGGER.error("Error updating WordClock status: %s", e)


class WordClockTimeLight(WordClockBaseLight):
    """Light entity for displaying the 'time' (text) on the WordClock."""

    def __init__(self, ip_address: str, device_id, object_id_prefix, device_name, session) -> None:
        """Initialize the light."""
        super().__init__(ip_address, device_id, object_id_prefix, device_name, session)
        self._attr_unique_id = f"{self._device_id}_time"
        self._attr_name = "WordClock Time"
        self.entity_id = f"light.{object_id_prefix}_time"
        self._color_key_prefix = "Time"
        self._default_rgb_color = (255, 0, 0)  # Default red

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        if ATTR_RGB_COLOR in kwargs:
            self._attr_rgb_color = kwargs[ATTR_RGB_COLOR]
        elif self._attr_rgb_color == (0, 0, 0):
            self._attr_rgb_color = self._default_rgb_color
        if ATTR_BRIGHTNESS in kwargs:
            self._attr_brightness = kwargs[ATTR_BRIGHTNESS]

        r, g, b = self._attr_rgb_color
        url = f"http://{self._ip_address}:2023/config?R-Time={r}&G-Time={g}&B-Time={b}"
        # If brightness is provided, update master intensity (0–50)
        if ATTR_BRIGHTNESS in kwargs:
            intensity_value = int(self._attr_brightness / 255 * 50)
            url += f"&INTENSITY={intensity_value}&INTENSITYviaWEB=1"
        await self._send_request(url)
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        url = f"http://{self._ip_address}:2023/config?R-Time=0&G-Time=0&B-Time=0"
        await self._send_request(url)
        self._state = False
        self.async_write_ha_state()


class WordClockBackgroundLight(WordClockBaseLight):
    """Light entity for controlling the background color of the WordClock."""

    def __init__(self, ip_address, device_id, object_id_prefix, device_name, session) -> None:
        """Initialize the background light."""
        super().__init__(ip_address, device_id, object_id_prefix, device_name, session)
        self._attr_unique_id = f"{self._device_id}_background"
        self._attr_name = "WordClock Background"
        self.entity_id = f"light.{object_id_prefix}_background"
        self._color_key_prefix = "Back"
        self._default_rgb_color = (110, 140, 255)  # Default light blue

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        if ATTR_RGB_COLOR in kwargs:
            self._attr_rgb_color = kwargs[ATTR_RGB_COLOR]
        elif self._attr_rgb_color == (0, 0, 0):
            self._attr_rgb_color = self._default_rgb_color
        if ATTR_BRIGHTNESS in kwargs:
            self._attr_brightness = kwargs[ATTR_BRIGHTNESS]

        r, g, b = self._attr_rgb_color
        url = f"http://{self._ip_address}:2023/config?R-Back={r}&G-Back={g}&B-Back={b}"
        # If brightness is provided, update master intensity (0–50)
        if ATTR_BRIGHTNESS in kwargs:
            intensity_value = int(self._attr_brightness / 255 * 50)
            url += f"&INTENSITY={intensity_value}&INTENSITYviaWEB=1"
        await self._send_request(url)
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        url = f"http://{self._ip_address}:2023/config?R-Back=0&G-Back=0&B-Back=0"
        await self._send_request(url)
        self._state = False
        self.async_write_ha_state()


class WordClockExtraWordLight(LightEntity):
    """Light entity for each extra 'word' LED on the WordClock."""


    def __init__(self, ip_address, word_id, name, device_id, object_id_prefix, device_name, session):
        """Initialize the light."""
        self._ip_address = ip_address
        self._word_id = word_id
        self._name = name
        self._state = False  # Using _state instead of _is_on for consistency
        self._device_id = device_id
        self._device_name = device_name
        self._session = session
        self._rgb_color = (255, 255, 255)  # Default to white
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_color_mode = ColorMode.RGB
        self._attr_unique_id = f"{self._device_id}_word_{self._word_id}"
        self._attr_name = f"WordClock Word {self._name}"
        self.entity_id = f"light.{object_id_prefix}_word_{name.lower().replace(' ', '_')}"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "AWSW",
            "model": "WordClock",
            "configuration_url": f"http://{self._ip_address}",
        }

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._state  # Return _state instead of _is_on

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the rgb color value [int, int, int]."""
        return self._rgb_color

    @property
    def should_poll(self) -> bool:
        """Return True to ensure Home Assistant polls this entity regularly."""
        return True

    async def async_update(self):
        """Fetch and update the current state of the light."""

        url = f"http://{self._ip_address}:2023/ewstatus/?{self._word_id}"
        try:
            async with self._session.get(url) as response:
                if response.status == 200:
                    data = await response.text()
                    # Use regex to extract the first occurrence of 0 or 1 from the reply
                    match = re.search(r"\b([01])\b", data)
                    if match:
                        old_state = self._state
                        new_state = match.group(1) == "1"
                        if old_state != new_state:
                            self._state = new_state
                            LOGGER.debug("Updated extra word %s state from %s to %s (raw: %s)",
                                self._word_id, old_state, self._state, data.strip())
                    else:
                        LOGGER.error("Unexpected response format for extra word %s: %s",
                            self._word_id, data.strip())
                else:
                    LOGGER.error("Failed to fetch status for extra word %s, HTTP %d",
                        self._word_id, response.status)
        except Exception as e:
            LOGGER.error("Error fetching status for extra word %s: %s", self._word_id, e)
    
    async def async_turn_on(self, **kwargs):
        """Turn on the light, updating color and brightness if provided."""

        # Base URL for turning on the word
        url = f"http://{self._ip_address}:2023/ew/?ew{self._word_id}=1"

        # Only add color parameters if color is explicitly provided
        if ATTR_RGB_COLOR in kwargs:
            self._rgb_color = kwargs[ATTR_RGB_COLOR]
            r, g, b = self._rgb_color
            url += f"&R={r}&G={g}&B={b}"

        await self._send_request(url)
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off the light."""

        url = f"http://{self._ip_address}:2023/ew/?ew{self._word_id}=0"
        await self._send_request(url)
        self._state = False
        self.async_write_ha_state()

    async def _send_request(self, url):
        """Send request to device."""
        try:
            async with self._session.get(url) as response:
                if response.status != 200:
                    LOGGER.error("Failed to send request to %s, HTTP %d", url, response.status)
        except Exception as e:
            LOGGER.error("Error sending request to %s: %s", url, e)