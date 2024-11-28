"""init."""

# https://github.com/mvdwetering/yamaha_ynca/blob/d3fa53a07bf3b04903aced4ff90d7ec2e07b8a83/custom_components/yamaha_ynca/migrations.py#L142
# def migrate_v2_to_v3(hass: HomeAssistant, config_entry: ConfigEntry):
#    # Scene entities are replaced by Button entities
#    # (scenes limited to a single devics seem a bit weird)
#    # cleanup the scene entities so the user does not have to
#    registry = entity_registry.async_get(hass)
#    entities = entity_registry.async_entries_for_config_entry(
#        registry, config_entry.entry_id
#    )
#    for entity in entities:
#        if entity.domain == Platform.SCENE:
#            registry.async_remove(entity.entity_id)
#
#    config_entry.version = 3
#    hass.config_entries.async_update_entry(config_entry, data=config_entry.data)


# https://community.home-assistant.io/t/config-flow-how-to-update-an-existing-entity/522442/4


# async def async_setup_entry(
#    hass: HomeAssistant, config_entry: AcmedaConfigEntry
# ) -> bool:
#    """Set up Rollease Acmeda Automate hub from a config entry."""
#    await _migrate_unique_ids(hass, config_entry)

# async def _migrate_unique_ids(hass: HomeAssistant, entry: AcmedaConfigEntry) -> None:
#    """Migrate pre-config flow unique ids."""
#    entity_registry = er.async_get(hass)
#    registry_entries = er.async_entries_for_config_entry(
#        entity_registry, entry.entry_id
#    )
#    for reg_entry in registry_entries:
#        if isinstance(reg_entry.unique_id, int):  # type: ignore[unreachable]
#            entity_registry.async_update_entity(  # type: ignore[unreachable]
#                reg_entry.entity_id, new_unique_id=str(reg_entry.unique_id)
#            )

#    # Fix non-string unique_id for device trackers
#    # Can be removed in 2025.1
#    entity_registry = er.async_get(hass)
#    for device_key in tado.data["mobile_device"]:
#        if entity_id := entity_registry.async_get_entity_id(
#            DEVICE_TRACKER_DOMAIN, DOMAIN, device_key
#        ):
#            entity_registry.async_update_entity(
#                entity_id, new_unique_id=str(device_key)
#            )


# https://github.com/home-assistant/core/blob/f41bc98fe2dad97e3008a6f5d955808900800d90/homeassistant/components/tibber/sensor.py#L314
# async def async_setup_entry(
#        # migrate
#        old_id = home.info["viewer"]["home"]["meteringPointData"]["consumptionEan"]
#        if old_id is None:
#            continue
#        # migrate to new device ids
#        old_entity_id = entity_registry.async_get_entity_id(
#            "sensor", TIBBER_DOMAIN, old_id
#        )
#        if old_entity_id is not None:
#            entity_registry.async_update_entity(
#                old_entity_id, new_unique_id=home.home_id
#            )
#        # migrate to new device ids
#        device_entry = device_registry.async_get_device(
#            identifiers={(TIBBER_DOMAIN, old_id)}
#        )
#        if device_entry and entry.entry_id in device_entry.config_entries:
#            device_registry.async_update_device(
#                device_entry.id, new_identifiers={(TIBBER_DOMAIN, home.home_id)}
#            )

import json
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PREFIX
from homeassistant.core import HomeAssistant

from .const import (
    CONF_DEVICE_POSTFIX,
    CONF_HK2,
    CONF_HK3,
    CONF_HK4,
    CONF_HK5,
    CONF_KENNFELD_FILE,
    CONF_NAME_DEVICE_PREFIX,
    CONF_NAME_TOPIC_PREFIX,
    CONST,
    FORMATS,
    TYPES,
)
from .hpconst import (
    DEVICELISTS,
    MODBUS_HZ_ITEMS,
    MODBUS_SYS_ITEMS,
    MODBUS_ST_ITEMS,
    MODBUS_WP_ITEMS,
    MODBUS_WW_ITEMS,
    MODBUS_W2_ITEMS,
    MODBUS_IO_ITEMS,
    MODBUS_HZ2_ITEMS,
    MODBUS_HZ3_ITEMS,
    MODBUS_HZ4_ITEMS,
    MODBUS_HZ5_ITEMS,
)
from .items import ModbusItem, StatusItem
from .modbusobject import ModbusAPI
from .configentry import MyConfigEntry, MyData
from .migrate_helpers import migrate_entities

logging.basicConfig()
log = logging.getLogger(__name__)

PLATFORMS: list[str] = [
    "number",
    "select",
    "sensor",
    #    "switch",
]


# Return boolean to indicate that initialization was successful.
# return True
async def async_setup_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Set up entry."""
    # Store an instance of the "connecting" class that does the work of speaking
    # with your actual devices.
    # hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hub.Hub(hass, entry.data["host"])
    mbapi = ModbusAPI(entry)
    await mbapi.connect()
    entry.runtime_data = MyData(mbapi, hass.config.config_dir, hass)

    migrate_entities(entry, MODBUS_SYS_ITEMS)
    migrate_entities(entry, MODBUS_HZ_ITEMS)
    migrate_entities(entry, MODBUS_HZ2_ITEMS)
    migrate_entities(entry, MODBUS_HZ3_ITEMS)
    migrate_entities(entry, MODBUS_HZ4_ITEMS)
    migrate_entities(entry, MODBUS_HZ5_ITEMS)
    migrate_entities(entry, MODBUS_WP_ITEMS)
    migrate_entities(entry, MODBUS_WW_ITEMS)
    migrate_entities(entry, MODBUS_W2_ITEMS)
    migrate_entities(entry, MODBUS_IO_ITEMS)
    migrate_entities(entry, MODBUS_ST_ITEMS)

    # see https://community.home-assistant.io/t/config-flow-how-to-update-an-existing-entity/522442/8
    entry.async_on_unload(entry.add_update_listener(update_listener))

    # This is used to generate a strings.json file from hpconst.py
    # create_string_json()

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    log.info("Init done")

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(
        entry.entry_id
    )  # list of entry_ids created for file


async def async_migrate_entry(hass: HomeAssistant, config_entry: MyConfigEntry):
    """Migrate old entry."""

    new_data = {**config_entry.data}

    if config_entry.version > 4:
        # This means the user has downgraded from a future version
        return False

    # to ensure all update paths we have to check every version to not overwrite existing entries
    if config_entry.version < 4:
        log.warning("Old Version detected")

    if config_entry.version < 2:
        log.warning("Version <2 detected")
        new_data[CONF_PREFIX] = CONST.DEF_PREFIX
        new_data[CONF_DEVICE_POSTFIX] = ""
        new_data[CONF_KENNFELD_FILE] = CONST.DEF_KENNFELDFILE
    if config_entry.version < 3:
        log.warning("Version <3 detected")
        new_data[CONF_HK2] = False
        new_data[CONF_HK3] = False
        new_data[CONF_HK4] = False
        new_data[CONF_HK5] = False
    if config_entry.version < 4:
        log.warning("Version <4 detected")
        new_data[CONF_NAME_DEVICE_PREFIX] = False
        new_data[CONF_NAME_TOPIC_PREFIX] = False

        hass.config_entries.async_update_entry(
            config_entry, data=new_data, minor_version=1, version=4
        )
        log.warning("Config entries updated to version 4")
    if config_entry.version < 5:
        log.warning("Version <5 detected")
    #   new_data[CONF_NAME_OLD_NAMESTYLE] = True

    if config_entry.version < 6:
        log.warning("Version <6 detected")
    #     new_data[CONF_CONVERT_NAMES] = False

    hass.config_entries.async_update_entry(
        config_entry, data=new_data, minor_version=1, version=6
    )
    log.warning(
        "Config entries updated to version 6 - using old namestyle, reinitialize integration, if new namestyle should be used"
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    entry.runtime_data.modbus_api.close()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        try:
            hass.data[entry.data[CONF_PREFIX]].pop(entry.entry_id)
        except KeyError:
            log.warning("KeyError: " + str(entry.data[CONF_PREFIX]))

    return unload_ok


def create_string_json() -> None:
    """Create strings.json from hpconst.py."""
    item: ModbusItem = None
    myStatusItem: StatusItem = None
    myEntity = {}
    myJson = {}
    mySensors = {}
    myNumbers = {}
    mySelects = {}

    # generate list of all mbitems
    DEVICELIST = []
    for devicelist in DEVICELISTS:
        DEVICELIST = DEVICELIST + devicelist

    for item in DEVICELIST:
        match item.type:
            case TYPES.SENSOR | TYPES.NUMBER_RO | TYPES.SENSOR_CALC:
                mySensor = {}
                mySensor["name"] = "{prefix}" + item.name
                if item.resultlist is not None:
                    if item.format is FORMATS.STATUS:
                        myValues = {}
                        for myStatusItem in item.resultlist:
                            myValues[myStatusItem.translation_key] = myStatusItem.text
                        mySensor["state"] = myValues.copy()
                mySensors[item.translation_key] = mySensor.copy()
            case TYPES.NUMBER:
                myNumber = {}
                myNumber["name"] = "{prefix}" + item.name
                if item.resultlist is not None:
                    if item.format is FORMATS.STATUS:
                        myValues = {}
                        for myStatusItem in item.resultlist:
                            myValues[myStatusItem.translation_key] = myStatusItem.text
                        myNumber["value"] = myValues.copy()
                myNumbers[item.translation_key] = myNumber.copy()
            case TYPES.SELECT:
                mySelect = {}
                mySelect["name"] = "{prefix}" + item.name
                if item.resultlist is not None:
                    if item.format is FORMATS.STATUS:
                        myValues = {}
                        for myStatusItem in item.resultlist:
                            myValues[myStatusItem.translation_key] = myStatusItem.text
                        mySelect["state"] = myValues.copy()
                mySelects[item.translation_key] = mySelect.copy()
    myEntity["sensor"] = mySensors
    myEntity["number"] = myNumbers
    myEntity["select"] = mySelects
    myJson["entity"] = myEntity

    # iterate over all devices in order to create a translation. TODO
    # for key, value in asdict(DEVICES).items():
    #    ...

    # load strings.json into string
    with open(
        file="config/custom_components/weishaupt_modbus/strings.json",
        encoding="utf-8",
    ) as file:
        data = file.read()
    # create dict from json
    data_dict = json.loads(data)
    # overwrite entiy dict
    data_dict["entity"] = myEntity
    # write whole json to file again
    with open(
        file="config/custom_components/weishaupt_modbus/strings.json",
        mode="w",
        encoding="utf-8",
    ) as file:
        file.write(json.dumps(data_dict, indent=4, sort_keys=True, ensure_ascii=False))
