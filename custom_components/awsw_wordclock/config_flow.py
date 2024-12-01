from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

LANGUAGES = {
    "German": "Deutsch",
    "English": "English",
    "Dutch": "Nederlands",
    "French": "Français",
    "Italian": "Italiano",
    "Swedish": "Svenska",
    "Spanish": "Español",
}

class WordClockConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AWSW WordClock."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            ip_address = user_input.get("ip_address")
            if self._is_valid_ip(ip_address):
                self.ip_address = ip_address
                return await self.async_step_language()
            errors["base"] = "invalid_ip"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip_address"): str
            }),
            errors=errors
        )

    async def async_step_language(self, user_input=None):
        """Handle the step for selecting language."""
        errors = {}
        if user_input is not None:
            selected_language = user_input.get("language")
            return self.async_create_entry(
                title=f"WordClock ({self.ip_address})",
                data={
                    "ip_address": self.ip_address,
                    "language": selected_language,
                },
            )

        return self.async_show_form(
            step_id="language",
            data_schema=vol.Schema({
                vol.Required("language", default="German"): vol.In(LANGUAGES.keys())
            }),
            errors=errors
        )

    def _is_valid_ip(self, ip_address):
        """Validate the given IP address."""
        import ipaddress
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False
