"""Setting uop my sensor entities."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .configentry import MyConfigEntry
from .const import TYPES
from .coordinator import MyCoordinator, MyWebIfCoordinator
from .entities import MyWebifSensorEntity, build_entity_list
from .hpconst import DEVICELISTS, WEBIF_INFO_HEIZKREIS1

logging.basicConfig()
log: logging.Logger = logging.getLogger(name=__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    _modbus_api = config_entry.runtime_data.modbus_api

    entries = []

    for device in DEVICELISTS:
        coordinator = MyCoordinator(
            hass=hass,
            my_api=_modbus_api,
            api_items=device,
            p_config_entry=config_entry,
        )
        await coordinator.async_config_entry_first_refresh()

        entries = await build_entity_list(
            entries=entries,
            config_entry=config_entry,
            api_items=device,
            item_type=TYPES.NUMBER_RO,
            coordinator=coordinator,
        )
        entries = await build_entity_list(
            entries=entries,
            config_entry=config_entry,
            api_items=device,
            item_type=TYPES.SENSOR_CALC,
            coordinator=coordinator,
        )

        log.debug(msg="Adding sensor entries to entity list ..")

        # Webif Sensors here
        entries = await build_entity_list(
            entries=entries,
            config_entry=config_entry,
            api_items=device,
            item_type=TYPES.SENSOR,
            coordinator=coordinator,
        )

    webifcoordinator = MyWebIfCoordinator(hass=hass, config_entry=config_entry)

    webifentries = []

    for webifitem in WEBIF_INFO_HEIZKREIS1:
        webifentries.append(  # noqa: PERF401
            MyWebifSensorEntity(
                config_entry=config_entry,
                api_item=webifitem,
                coordinator=webifcoordinator,
                idx=1,
            )
        )

    entries = entries + webifentries
    async_add_entities(
        entries,
        update_before_add=True,
    )
