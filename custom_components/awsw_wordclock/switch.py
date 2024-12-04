from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
import aiohttp
import logging

LOGGER = logging.getLogger(__name__)

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
    """Set up WordClock switches from a config entry."""
    ip_address = entry.data["ip_address"]
    # Load the language from entry.options or fallback to German
    language = entry.options.get("language", "German")
    device_id = f"wordclock_{ip_address.replace('.', '_')}"
    session = hass.data[DOMAIN][entry.entry_id]["session"]
    switches = []

    LOGGER.info("Setting up WordClock switches for IP: %s with language: %s", ip_address, language)

    # Fetch words for the selected language
    words = LANGUAGE_WORDS.get(language, {})
    if not words:
        LOGGER.error("Language '%s' not found. Using default (German).", language)
        words = LANGUAGE_WORDS["German"]

    for word_id, word_name in words.items():
        switches.append(WordClockExtraWordSwitch(ip_address, word_id, word_name, device_id, session))

    async_add_entities(switches)


class WordClockExtraWordSwitch(SwitchEntity):
    """Representation of an extra word switch."""

    def __init__(self, ip_address, word_id, name, device_id, session):
        self._ip_address = ip_address
        self._word_id = word_id
        self._name = name
        self._is_on = False
        self._device_id = device_id
        self._session = session

    @property
    def name(self):
        return f"Word {self._name}"

    @property
    def is_on(self):
        return self._is_on

    @property
    def unique_id(self):
        return f"{self._device_id}_word_{self._word_id}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": f"WordClock ({self._ip_address})",
            "manufacturer": "AWSW",
            "model": "WordClock",
        }

    async def async_turn_on(self, **kwargs):
        self._is_on = True
        await self._send_request("1")
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._is_on = False
        await self._send_request("0")
        self.async_write_ha_state()

    async def _send_request(self, state):
        url = f"http://{self._ip_address}:2023/ew/?ew{self._word_id}={state}"
        try:
            async with self._session.get(url) as response:
                if response.status != 200:
                    LOGGER.error("Failed to send request to %s, HTTP %d", url, response.status)
        except Exception as e:
            LOGGER.error("Error sending request to %s: %s", url, e)
