"""Config flow for AWSW WordClock integration."""
from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

# Language mapping for configuration forms
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
    """Handle a config flow for AWSW WordClock.

    This class manages the initial setup and configuration of a WordClock device.
    """

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step for configuring a new device.

        Validates user input and creates configuration entry if valid.
        """
        errors = {}
        if user_input is not None:
            ip_address = user_input.get("ip_address")
            name = user_input.get("name", f"WordClock ({ip_address})")
            language = user_input.get("language")
            polling_time = user_input.get("polling_time", 5)

            # Validate IP address and check for duplicates
            if not self._is_valid_ip(ip_address):
                errors["base"] = "invalid_ip"
            elif await self._is_ip_already_configured(ip_address):
                errors["base"] = "ip_exists"
            else:
                # Create configuration entry with validated data
                return self.async_create_entry(
                    title=name,
                    data={"ip_address": ip_address, "name": name},
                    options={"language": language, "polling_time": polling_time},
                )

        # Show configuration form with validation schema
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip_address"): str,
                vol.Optional("name", default="WordClock"): str,
                vol.Required("language", default="German"): vol.In(LANGUAGES),
                vol.Required("polling_time", default=5): vol.All(vol.Coerce(int), vol.Range(min=1)),
            }),
            errors=errors,
        )

    def _is_valid_ip(self, ip_address):
        """Validate the given IP address.

        Args:
            ip_address: String containing the IP address to validate

        Returns:
            bool: True if valid IP address, False otherwise
        """
        import ipaddress
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    async def _is_ip_already_configured(self, ip_address):
        """Check if the IP address is already configured.

        Args:
            ip_address: String containing the IP address to check

        Returns:
            bool: True if IP is already configured, False otherwise
        """
        for entry in self._async_current_entries():
            if entry.data.get("ip_address") == ip_address:
                return True
        return False

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow for this handler.

        Creates an instance of WordClockOptionsFlow for handling configuration updates.
        """
        return WordClockOptionsFlow(config_entry)


class WordClockOptionsFlow(config_entries.OptionsFlow):
    """Handle options for AWSW WordClock.

    This class manages updates to existing WordClock configurations.
    """

    def __init__(self, config_entry):
        """Initialize the options flow.

        Args:
            config_entry: The current configuration entry being modified
        """
        self.entry_id = config_entry.entry_id
        self.current_language = config_entry.options.get(
            "language", config_entry.data.get("language", "German")
        )
        self.current_polling_time = config_entry.options.get("polling_time", 5)

    async def async_step_init(self, user_input=None):
        """Handle the initial step of the options flow.

        Presents and processes the options update form.
        """
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("language", default=self.current_language): vol.In(LANGUAGES),
                vol.Required("polling_time", default=self.current_polling_time): vol.All(vol.Coerce(int), vol.Range(min=1)),
            })
        )