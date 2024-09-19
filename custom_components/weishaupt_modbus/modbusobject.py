from pymodbus.client import ModbusTcpClient as ModbusClient
from .const import FORMATS, TYPES

# import logging
# logging.basicConfig()
# log = logging.getLogger()
# log.setLevel(logging.DEBUG)

# A Modbus object that contains a Modbus item and communicates with the Modbus
# it contains a ModbusClient for setting and getting Modbus register values
class ModbusObject():
    _ModbusItem = None
    _DataFormat = None
 
    _ip = None
    _port = None
    _ModbusClient = None

    def __init__(self, hp_ip, hp_port, modbus_item):
        self._ModbusItem = modbus_item
        #self._HeatPump = heatpump
        
        self._ip = hp_ip
        self._port = hp_port
        self._ModbusClient = None
        
    def connect(self):
        try:
            self._ModbusClient = ModbusClient(host=self._ip, port=self._port)
            return self._ModbusClient.connected  # noqa: TRY300
        except:  # noqa: E722
            return None

    @property
    def value(self):
        try:
            self.connect()
            match self._ModbusItem.type:
                case TYPES.SENSOR:
                    # Sensor entities are read-only
                    return self._ModbusClient.read_input_registers(self._ModbusItem.address, slave=1).registers[0]
                case TYPES.SELECT | TYPES.NUMBER:
                    return self._ModbusClient.read_holding_registers(self._ModbusItem.address, slave=1).registers[0]
        except:  # noqa: E722
            return None

    @value.setter
    def value(self,value) -> None:
        if self._ModbusItem.type == TYPES.SENSOR:
            # Sensor entities are read-only
            return

        self.connect()
        self._ModbusClient.write_register(self._ModbusItem.address, value, slave=1)
