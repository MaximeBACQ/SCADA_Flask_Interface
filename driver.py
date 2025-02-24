from pyModbusTCP.client import ModbusClient
from time import sleep
from DriverHasControlException import DriverHasControlException

#constants
SLAVE_ADDRESS = '127.0.0.1'
SLAVE_PORT = 502
ARR_COUNT = {"b": 0, "g": 0, "m": 0}
ARR_SLEEP = {"b": 2, "g": 3, "m": 6}

#modbus addresses
SENSOR = 0
ENTRY_CONVOYER = 0
STOP_BLADE = 1
EXIT_CONVOYER = 2
ARR_BELT = {"b": 4, "g": 6, "m": 8}
ARR_TURN = {"b": 3, "g": 5, "m": 7}
EMITTER = 9
ARR_COUNTER = {"b": 0, "g": 1, "m": 2}

def check_driver_has_control(shared_state, control_type: str):
    if not shared_state.driverHasControl[control_type]:
        raise DriverHasControlException("")

def factory_run(client, status):
    client.write_single_coil(ENTRY_CONVOYER, status)
    client.write_single_coil(EMITTER, status)
    sleep(0.2)
    client.write_single_coil(STOP_BLADE, (status+1)%2)

def color_found(client, shared_state, color):
    try:
        check_driver_has_control(shared_state, color)
        sleep(1)

        check_driver_has_control(shared_state, "entry")
        factory_run(client, 0)

        check_driver_has_control(shared_state, color)
        ARR_COUNT[color] += 1
        client.write_single_register(ARR_COUNTER[color], ARR_COUNT[color])

        check_driver_has_control(shared_state, color)
        client.write_single_coil(ARR_TURN[color], 1)
        client.write_single_coil(ARR_BELT[color], 1)
        sleep(ARR_SLEEP[color])
        client.write_single_coil(ARR_TURN[color], 0)
        client.write_single_coil(ARR_BELT[color], 0)

        check_driver_has_control(shared_state, "entry")
        factory_run(client, 1)

    except DriverHasControlException:
        return
    
    finally:
        if shared_state.driverHasControl["exit"]:
            client.write_single_coil(EXIT_CONVOYER, 1)

def driver_loop(shared_state, stop_event):
    client = ModbusClient(SLAVE_ADDRESS, port=SLAVE_PORT, unit_id=1)
    client.open()
    
    if client.is_open:
        print("[Driver] Connexion Modbus OK")
    else:
        print("[Driver] Connexion Modbus KO")
        return

    if shared_state.driverHasControl["exit"]:
        client.write_single_coil(EXIT_CONVOYER, 1)
    if shared_state.driverHasControl["entry"]:
        factory_run(client, 1)
            
    while not stop_event.is_set():
        #print(shared_state.driverHasControl)
        sensor_value = client.read_input_registers(SENSOR, 1)
        if sensor_value:
            val = sensor_value[0]

            #if shared_state.driverHasControl["entry"] and shared_state.driverHasControl["exit"]:
            if val in range(1, 4):
                color_found(client, shared_state, "b")
            elif val in range(4, 7):
                color_found(client, shared_state, "g")
            elif val in range(7, 10):
                color_found(client, shared_state, "m")

        sleep(0.5)

    client.close()