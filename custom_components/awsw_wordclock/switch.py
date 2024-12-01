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
    language = entry.data.get("language", "German")
    device_id = f"wordclock_{ip_address.replace('.', '_')}"
    switches = []

    LOGGER.info("Setting up WordClock switches for IP: %s with language: %s", ip_address, language)

    words = LANGUAGE_WORDS.get(language, {})
    for word_id, word_name in words.items():
        switches.append(WordClockSwitch(ip_address, word_id, word_name, device_id))

    async_add_entities(switches)


class WordClockSwitch(SwitchEntity):
    """Representation of a WordClock extra word as a switch."""

    def __init__(self, ip_address, word_id, name, device_id):
        self._ip_address = ip_address
        self._word_id = word_id
        self._name = name
        self._is_on = False
        self._device_id = device_id

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
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=f"WordClock ({self._ip_address})",
            manufacturer="AWSW",
            model="WordClock",
            configuration_url=f"http://{self._ip_address}",
        )

    async def async_turn_on(self, **kwargs):
        LOGGER.debug("Turning on Word %s (ID: %d)", self._name, self._word_id)
        self._is_on = True
        await self._send_request("1")
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        LOGGER.debug("Turning off Word %s (ID: %d)", self._name, self._word_id)
        self._is_on = False
        await self._send_request("0")
        self.async_write_ha_state()

    async def async_update(self):
        """Fetch the current status of the switch."""
        url = f"http://{self._ip_address}:2023/ewstatus/?{self._word_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    self._is_on = (await response.text()).strip() == "1"
                else:
                    LOGGER.error("Failed to fetch status for Word %s (HTTP %d)", self._name, response.status)
        self.async_write_ha_state()

    async def _send_request(self, state):
        url = f"http://{self._ip_address}:2023/ew/?ew{self._word_id}={state}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    LOGGER.error("Request to %s failed with HTTP %d", url, response.status)
