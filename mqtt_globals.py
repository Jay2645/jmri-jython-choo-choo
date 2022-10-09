import json
import re

ROSTER_PATH = "trains/roster"
UTILITY_PATH = "trains/utilities"
TURNOUT_PATH = "trains/track/turnout"

DISCOVERY_SENSOR_PATH = "homeassistant/sensor/train"
DISCOVERY_BINARY_SENSOR_PATH = "homeassistant/binary_sensor/train"
DISCOVERY_SWITCH_PATH = "homeassistant/switch/train"
DISCOVERY_LIGHT_PATH = "homeassistant/light/train"
DISCOVERY_NUMBER_PATH = "homeassistant/number/train"
DISCOVERY_SELECT_PATH = "homeassistant/select/train"

AVAILABILITY_TOPIC_PATH = "trains/status"

MODEL_RAILROAD_DEVICE_ID = "ModelRailroad"
MODEL_RAILROAD_AREA = "Model Railroad"

manager = JMRIMQTTManager()

def get_discovery_object(id_string, state_string, device):
    discovery_entry = {}

    discovery_entry['name'] = id_string
    discovery_entry['availability_topic'] = AVAILABILITY_TOPIC_PATH
    discovery_entry['unique_id'] = "choo_choo_" + sanitize_id(id_string)
    discovery_entry['state_topic'] = state_string
    discovery_entry['device'] = device
    return discovery_entry

def get_model_railroad_device():
    device = {}
    device['name'] = "Model Railroad"
    device['suggested_area'] = MODEL_RAILROAD_AREA
    device['identifiers'] = MODEL_RAILROAD_DEVICE_ID
    device['connections'] = [["mac", "dc:a6:32:7b:7a:9e"]]
    device['manufacturer'] = "Jay Stevens"
    return device

def publish_object(topic, payload_object, qos=0, retain=False):
    json_output = json.dumps(payload_object)
    publish(topic, str(json_output), qos, retain)

def publish(topic, payload, qos=0, retain=False):
    manager.publish(topic, payload, qos, retain)

def subscribe(topic, delegate):
    manager.add_subscription(topic, delegate)

def sanitize_id(id):
    id_string = str(id)
    return re.sub('\W+','_', id_string).lower()

def get_roster_attributes_path(id):
    return get_roster_path(id) + "/attributes"

def get_roster_path(id):
    clean_id = sanitize_id(id)
    return ROSTER_PATH + "/" + clean_id

def get_utility_state_path(id):
    clean_id = sanitize_id(id)
    return UTILITY_PATH + "/" + clean_id + "/state"

def get_turnout_state_path(id):
    clean_id = sanitize_id(id)
    return TURNOUT_PATH + "/" + clean_id

def get_discovery_roster_sensor_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_SENSOR_PATH + "_roster/" + clean_id + "/config"

def get_discovery_roster_binary_sensor_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_BINARY_SENSOR_PATH + "_roster/" + clean_id + "/config"

def get_discovery_roster_select_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_SELECT_PATH + "_roster/" + clean_id + "/config"

def get_discovery_roster_select_command_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_SELECT_PATH + "_roster/" + clean_id + "/command"

def get_discovery_roster_switch_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_SWITCH_PATH + "_roster/" + clean_id + "/config"

def get_discovery_roster_switch_command_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_SWITCH_PATH + "_roster/" + clean_id + "/command"

def get_discovery_roster_light_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_LIGHT_PATH + "_roster/" + clean_id + "/config"

def get_discovery_roster_light_command_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_LIGHT_PATH + "_roster/" + clean_id + "/command"

def get_discovery_roster_number_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_NUMBER_PATH + "_roster/" + clean_id + "/config"

def get_discovery_roster_number_command_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_NUMBER_PATH + "_roster/" + clean_id + "/command"

def get_discovery_utility_sensor_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_SENSOR_PATH + "_utilities/" + clean_id + "/config"

def get_discovery_utility_binary_sensor_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_BINARY_SENSOR_PATH + "_utilities/" + clean_id + "/config"

def get_discovery_utility_switch_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_SWITCH_PATH + "_utilities/" + clean_id + "/config"

def get_discovery_utility_switch_command_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_SWITCH_PATH + "_utilities/" + clean_id + "/command"

def get_discovery_utility_number_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_NUMBER_PATH + "_utilities/" + clean_id + "/config"

def get_discovery_utility_number_command_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_NUMBER_PATH + "_utilities/" + clean_id + "/command"

def get_discovery_turnout_switch_path(id):
    clean_id = sanitize_id(id)
    return DISCOVERY_SWITCH_PATH + "_turnout/" + clean_id + "/config"

# Set availability payload
publish(AVAILABILITY_TOPIC_PATH, "online", 0, True)

status_discovery_entry = {}
status_discovery_entry['name'] = "JMRI Status"
status_discovery_entry['unique_id'] = "choo_choo_jmri_status"
status_discovery_entry['state_topic'] = AVAILABILITY_TOPIC_PATH
status_discovery_entry['command_topic'] = get_discovery_utility_switch_command_path("jmri_status")
status_discovery_entry['payload_on'] = "online"
status_discovery_entry['payload_off'] = "offline"
status_discovery_entry['device'] = get_discovery_device()
status_discovery_entry['retain'] = False
status_json_output = json.dumps(status_discovery_entry)
publish(get_discovery_utility_switch_path("jmri_status"), str(status_json_output), 0, True)

def on_shutdown_command_received(topic, payload):
    if payload == "offline":
        publish(AVAILABILITY_TOPIC_PATH, "offline", 0, True)
        publish(get_utility_state_path("track_power"), "OFF", 0, True)
        powermanager.setPower(jmri.PowerManager.OFF)
subscribe(status_discovery_entry['command_topic'], on_shutdown_command_received)
