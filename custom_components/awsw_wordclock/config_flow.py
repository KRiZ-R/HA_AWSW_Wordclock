
from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class WordClockConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AWSW WordClock."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            ip_address = user_input.get("ip_address")
            if self._is_valid_ip(ip_address):
                return self.async_create_entry(
                    title=f"WordClock ({ip_address})", data={"ip_address": ip_address}
                )
            errors["base"] = "invalid_ip"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip_address"): str
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
