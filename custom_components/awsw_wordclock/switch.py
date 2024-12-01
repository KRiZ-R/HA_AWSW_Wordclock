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
        1: "ALARM",
        2: "BIRTHDAY",
        3: "TAKE OUT TRASH",
        4: "CAR",
        5: "HOLIDAY",
        6: "FORMULA1",
        7: "YELLOW BAG",
        8: "VACATION",
        9: "WORKSHOP",
    },
    "Dutch": {
        1: "ALARM",
        2: "VERJAARDAG",
        3: "AFVAL BUITEN",
        4: "AUTO",
        5: "VAKANTIE",
        6: "FORMULE1",
        7: "GELE ZAK",
        8: "WERKPLAATS",
        9: "VRIJE TIJD",
    },
    "French": {
        1: "ALARME",
        2: "ANNIVERSAIRE",
        3: "SORTIR LES DÉCHETS",
        4: "VOITURE",
        5: "VACANCES",
        6: "FORMULE1",
        7: "SAC JAUNE",
        8: "ATELIER",
        9: "TEMPS LIBRE",
    },
    "Italian": {
        1: "ALLARME",
        2: "COMPLEANNO",
        3: "PORTARE FUORI LA SPAZZATURA",
        4: "AUTO",
        5: "VACANZA",
        6: "FORMULA1",
        7: "SACCO GIALLO",
        8: "OFFICINA",
        9: "TEMPO LIBERO",
    },
    "Swedish": {
        1: "LARM",
        2: "FÖDELSEDAG",
        3: "TA UT SOPOR",
        4: "BIL",
        5: "SEMESTER",
        6: "FORMEL1",
        7: "GUL PÅSE",
        8: "VERKSTAD",
        9: "FRITID",
    },
    "Spanish": {
        1: "ALARMA",
        2: "CUMPLEAÑOS",
        3: "SACAR LA BASURA",
        4: "COCHE",
        5: "VACACIONES",
        6: "FÓRMULA1",
        7: "BOLSA AMARILLA",
        8: "TALLER",
        9: "TIEMPO LIBRE",
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
