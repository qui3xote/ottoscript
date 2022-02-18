from homeassistant import core


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
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
    return True
