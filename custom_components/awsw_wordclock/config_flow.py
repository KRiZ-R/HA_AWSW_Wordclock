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
        """Handle the initial step for configuring a new device."""
        errors = {}
        if user_input is not None:
            ip_address = user_input.get("ip_address")
            language = user_input.get("language")
            
            # Check if IP is valid
            if not self._is_valid_ip(ip_address):
                errors["base"] = "invalid_ip"
            elif await self._is_ip_already_configured(ip_address):
                errors["base"] = "ip_exists"
            else:
                return self.async_create_entry(
                    title=f"WordClock ({ip_address})",
                    data={"ip_address": ip_address, "language": language},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip_address"): str,
                vol.Required("language", default="German"): vol.In(LANGUAGES),
            }),
            errors=errors,
        )

    def _is_valid_ip(self, ip_address):
        """Validate the given IP address."""
        import ipaddress
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    async def _is_ip_already_configured(self, ip_address):
        """Check if the IP address is already configured."""
        for entry in self._async_current_entries():
            if entry.data.get("ip_address") == ip_address:
                return True
        return False

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow for this handler."""
        return WordClockOptionsFlow(config_entry)


class WordClockOptionsFlow(config_entries.OptionsFlow):
    """Handle options for AWSW WordClock."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle the initial step of the options flow."""
        if user_input is not None:
            # Update the options and reload the entry
            self.hass.config_entries.async_update_entry(self.config_entry, options=user_input)
            return self.async_create_entry(title="", data={})

        # Show form for updating the language
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("language", default=self.config_entry.options.get("language", self.config_entry.data.get("language", "German"))): vol.In(LANGUAGES),
            })
        )
