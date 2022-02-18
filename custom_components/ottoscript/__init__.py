import os
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

import voluptuous as vol
from voluptuous.error import MultipleInvalid
from voluptuous.schema_builder import PREVENT_EXTRA

from .const import (
    DOMAIN,
    DOMAIN_DATA,
    CONFIG_SCRIPT_DIR,
    PYSCRIPT_FOLDER,
    PYSCRIPT_APP_FOLDER
)

_LOGGER = logging.getLogger(__name__)

config_schema = vol.Schema(
    {
        vol.Optional(CONFIG_SCRIPT_DIR, default='/config/ottoscripts/'): str
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the OttoScript component."""
    # @TODO: Add setup code.
    # Check for pyscript install - stop if not installed
    # Read in configuration - script directory.
    # Check if app is installed - if not, copy files.
    # ^will need to check version installed. Or just reinstall
    # every time.
    # if pyscript running - reload.
    # If pyscript not running... wait? Or just stop?
    # Add script dir to watchdog. (borrow code form pyscript)
    # if any otto files change, trigger pyscript reload.

    # Check for pyscript folder
    pyscript_folder = hass.config.path(PYSCRIPT_FOLDER)
    if not await hass.async_add_executor_job(os.path.isdir, pyscript_folder):
        _LOGGER.error(
            "Pyscript Folder %s not found. Install pyscript.", pyscript_folder)
        return False

    app_folder = hass.config.pyscript_folder(PYSCRIPT_APP_FOLDER)
    if not await hass.async_add_executor_job(os.path.isdir, app_folder):
        _LOGGER.debug(
            "Pyscript App Folder %s not found. Creating it.", app_folder)
            await hass.async_add_executor_job(os.makedirs, app_folder)

        return True


async def async_setup_entry(hass, config_entry, async_add_devices):
    return


async def async_unload_entry(hass, entry):
    return
