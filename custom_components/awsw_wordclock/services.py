"""Services for AWSW WordClock integration."""
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.components.light import ATTR_RGB_COLOR

from .const import DOMAIN

LOGGER = logging.getLogger(__name__)

SERVICE_SET_WORD_COLOR = "set_word_color"

SERVICE_SET_WORD_COLOR_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Required(ATTR_RGB_COLOR): vol.All(
        vol.ExactSequence((cv.byte, cv.byte, cv.byte)),
        vol.Coerce(tuple),
    ),
})

async def async_setup_services(hass: HomeAssistant):
    """Set up services for AWSW WordClock integration."""
    
    async def async_handle_word_color(call: ServiceCall):
        """Handle the service call to set word color."""
        entity_id = call.data["entity_id"]
        rgb_color = call.data[ATTR_RGB_COLOR]
        
        entity = hass.states.get(entity_id)
        if not entity:
            LOGGER.error("Entity %s not found", entity_id)
            return
            
        # Find entity in registry and call its turn_on method with the color
        for component in hass.data.get(DOMAIN, {}).values():
            if "light" in component:
                for entity_obj in component["light"]:
                    if entity_obj.entity_id == entity_id:
                        await entity_obj.async_turn_on(**{ATTR_RGB_COLOR: rgb_color})
                        return
                            
        LOGGER.error("Could not find entity object for %s", entity_id)
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_WORD_COLOR,
        async_handle_word_color,
        schema=SERVICE_SET_WORD_COLOR_SCHEMA,
    )
    
    return True
    
async def async_unload_services(hass: HomeAssistant):
    """Unload services for AWSW WordClock integration."""
    if hass.services.has_service(DOMAIN, SERVICE_SET_WORD_COLOR):
        hass.services.async_remove(DOMAIN, SERVICE_SET_WORD_COLOR)