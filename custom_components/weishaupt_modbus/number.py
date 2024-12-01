"""Number."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .configentry import MyConfigEntry
from .const import TYPES
from .coordinator import MyCoordinator
from .entity_helpers import build_entity_list
from .hpconst import DEVICELISTS


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    _modbus_api = config_entry.runtime_data.modbus_api

    # start with an empty list of entries
    entries = []

    coordinator = config_entry.runtime_data.coordinator

    for device in DEVICELISTS:
        # we create one communicator per device and entry platform. This allows better scheduling than one
        # coordinator = MyCoordinator(
        #    hass=hass,
        #    my_api=_modbus_api,
        #    api_items=device,
        #    p_config_entry=config_entry,
        # )
        # await coordinator.async_config_entry_first_refresh()

        entries = await build_entity_list(
            entries=entries,
            config_entry=config_entry,
            api_items=device,
            item_type=TYPES.NUMBER,
            coordinator=coordinator,
        )

    async_add_entities(
        entries,
        update_before_add=True,
    )
