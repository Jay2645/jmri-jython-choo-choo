import java
import java.beans

import jmri
import jmri.jmrit.automat
import jmri.jmrit.roster

throttle_manager = jmri.InstanceManager.getDefault(jmri.ThrottleManager)
roster_list = jmri.jmrit.roster.Roster.getDefault().matchingList(None, None, None, None, None, None, None)

roster_command_topics = {}
roster_names = []

class LocoSpeedChanger(jmri.jmrit.automat.AbstractAutomaton):
    def __init__(self, in_roster_entry, in_speed):
        self.roster_entry = in_roster_entry
        self.speed_percent = abs(in_speed) / 100.0
        self.is_forward = in_speed >= 0

    def handle(self):
        throttle = self.getThrottle(self.roster_entry)
        if throttle is None:
            return False
        throttle.setIsForward(self.is_forward)
        throttle.setSpeedSetting(self.speed_percent)
        throttle.release(None)
        return False

class LocoFunctionButton(jmri.jmrit.automat.AbstractAutomaton):
    def __init__(self, in_roster_entry, in_function, in_value):
        self.roster_entry = in_roster_entry
        self.function = in_function
        self.value = in_value

    def handle(self):
        throttle = self.getThrottle(self.roster_entry)
        if throttle is None:
            return False
        throttle.setFunction(self.function, self.value)
        throttle.release(None)
        return False

class LocoListener(java.beans.PropertyChangeListener):
    def __init__(self, in_roster_entry):
        self.roster_entry = in_roster_entry

        # Add basic attributes
        self.static_attributes = {}
        self.static_attributes['id'] = self.roster_entry.getId()
        self.static_attributes['display_name'] = self.roster_entry.getDisplayName()
        self.static_attributes['comment'] = self.roster_entry.getComment()
        self.static_attributes['decoder_comment'] = self.roster_entry.getDecoderComment()
        self.static_attributes['decoder_family'] = self.roster_entry.getDecoderFamily()
        self.static_attributes['decoder_model'] = self.roster_entry.getDecoderModel()
        self.static_attributes['date_modified'] = self.roster_entry.getDateUpdated()
        self.static_attributes['dcc_address'] = self.roster_entry.getDccAddress()
        self.static_attributes['road_name'] = self.roster_entry.getRoadName()
        self.static_attributes['road_number'] = self.roster_entry.getRoadNumber()
        self.static_attributes['filename'] = self.roster_entry.getFileName()
        self.static_attributes['icon_path'] = self.roster_entry.getIconPath()
        self.static_attributes['image_path'] = self.roster_entry.getImagePath()
        self.static_attributes['max_function_num'] = self.roster_entry.getMAXFNNUM()
        self.static_attributes['max_speed_percent'] = self.roster_entry.getMaxSpeedPCT()
        self.static_attributes['manufacturer'] = self.roster_entry.getMfg()
        self.static_attributes['model'] = self.roster_entry.getModel()
        self.static_attributes['owner'] = self.roster_entry.getOwner()
        self.static_attributes['path_name'] = self.roster_entry.getPathName()
        self.static_attributes['protocol'] = self.roster_entry.getProtocolAsString()
        self.static_attributes['shunting_function'] = self.roster_entry.getShuntingFunction()
        self.static_attributes['url'] = self.roster_entry.getURL()
        self.static_attributes['is_long_address'] = self.roster_entry.isLongAddress()
        self.static_attributes['is_open'] = self.roster_entry.isOpen()

        self.attributes = {}
        self.attributes['SpeedSetting'] = 0.0
        self.attributes['IsForward'] = False
        self.attributes['speed'] = 0.0
        # Add functions 0-28
        for i in range(0, 29):
            function_name = "F" + str(i)
            self.attributes[function_name] = "OFF"

    def propertyChange(self, event):
        if event.propertyName in self.attributes:
            if event.propertyName == "IsForward" or event.propertyName == "SpeedSetting":
                self.attributes[event.propertyName] = event.newValue
                if self.attributes['IsForward']:
                    self.attributes['speed'] = int(self.attributes['SpeedSetting'] * 100)
                else:
                    self.attributes['speed'] = int(-1.0 * self.attributes['SpeedSetting'] * 100)
                publish(get_roster_path(self.static_attributes['id']) + "/speed", self.attributes['speed'], 0, True)
            else:
                if event.newValue:
                    self.attributes[event.propertyName] = "ON"
                else:
                    self.attributes[event.propertyName] = "OFF"
                publish(get_roster_path(self.static_attributes['id']) + "/" + event.propertyName, self.attributes[event.propertyName], 0, True)

    def get_attributes_topic(self):
        return get_roster_attributes_path(self.roster_entry.getId())

    def publish_full_state(self):
        for entry in self.attributes:
            if entry == "IsForward" or entry == "SpeedSetting":
                continue
            publish(get_roster_path(self.static_attributes['id']) + "/" + entry, self.attributes[entry], 0, True)

    def publish_attributes(self):
        publish_object(self.get_attributes_topic(), self.static_attributes, 0, True)

def on_headlight_command_received(topic, payload):
    entry = roster_command_topics[topic]
    headlight_function = LocoFunctionButton(entry, 0, payload == "ON")
    headlight_function.start()

def on_bell_command_received(topic, payload):
    entry = roster_command_topics[topic]
    bell_function = LocoFunctionButton(entry, 1, payload == "ON")
    bell_function.start()

def on_horn_command_received(topic, payload):
    entry = roster_command_topics[topic]
    horn_function = LocoFunctionButton(entry, 2, payload == "ON")
    horn_function.start()

def on_mute_command_received(topic, payload):
    entry = roster_command_topics[topic]
    mute_function = LocoFunctionButton(entry, 8, payload == "ON")
    mute_function.start()

def on_throttle_command_received(topic, payload):
    entry = roster_command_topics[topic]
    speed_changer = LocoSpeedChanger(entry, int(payload))
    speed_changer.start()

for entry in roster_list.toArray():
    in_consist_group = False

    for group in entry.getGroups().toArray():
        if group.getName() == "Consists":
            in_consist_group = True
            break

    if in_consist_group == False:
        continue

    dcc_address = entry.getDccLocoAddress()
    id_string = str(entry.getDisplayName())
    
    print("Attached to " + id_string)

    roster_names.append(id_string)
    
    listener = LocoListener(entry)
    throttle_manager.attachListener(dcc_address, listener)
    listener.publish_full_state()
    listener.publish_attributes()

    attributes_string = get_roster_attributes_path(id_string)

    # Turn on the headlight
    headlight_function = LocoFunctionButton(entry, 0, True)
    headlight_function.start()

    # Set loco to forward
    speed_changer = LocoSpeedChanger(entry, 0)
    speed_changer.start()

    device = {}
    device['name'] = entry.getDisplayName()
    device['identifiers'] = entry.getId()
    device['manufacturer'] = entry.getMfg()
    device['model'] = entry.getModel()
    device['suggested_area'] = MODEL_RAILROAD_AREA
    device['configuration_url'] = MODEL_RAILROAD_URL
    device['via_device'] = MODEL_RAILROAD_DEVICE_ID

    # Publish/subscribe to speed changes
    speed_state_string = get_roster_path(id_string) + "/speed"
    speed_discovery_string = get_discovery_roster_number_path(id_string)
    speed_discovery_entry = get_discovery_object(id_string, speed_state_string, device)
    speed_discovery_entry['json_attributes_topic'] = attributes_string
    speed_discovery_entry['min'] = -100
    speed_discovery_entry['max'] = 100
    speed_discovery_entry['icon'] = "mdi:train-variant"
    speed_discovery_entry['command_topic'] = get_discovery_roster_number_command_path(id_string)

    roster_command_topics[speed_discovery_entry['command_topic']] = entry
    subscribe(speed_discovery_entry['command_topic'], on_throttle_command_received)

    publish_object(speed_discovery_string, speed_discovery_entry, 0, True)

    # Publish/subscribe to light changes
    light_state_string = get_roster_path(id_string) + "/F0"
    light_discovery_string = get_discovery_roster_light_path(id_string + "_light")
    light_discovery_entry = get_discovery_object(id_string + " Light", light_state_string, device)
    light_discovery_entry['schema'] = "template"
    light_discovery_entry['command_on_template'] = "ON"
    light_discovery_entry['command_off_template'] = "OFF"
    light_discovery_entry['state_template'] = "{{ value|lower }}"
    light_discovery_entry['json_attributes_topic'] = attributes_string
    light_discovery_entry['icon'] = "mdi:car-light-high"
    light_discovery_entry['command_topic'] = get_discovery_roster_light_command_path(id_string + "_light")

    roster_command_topics[light_discovery_entry['command_topic']] = entry
    subscribe(light_discovery_entry['command_topic'], on_headlight_command_received)

    publish_object(light_discovery_string, light_discovery_entry, 0, True)

    # Publish/subscribe to the bell
    bell_state_string = get_roster_path(id_string) + "/F1"
    bell_discovery_string = get_discovery_roster_switch_path(id_string + "_bell")
    bell_discovery_entry = get_discovery_object(id_string + " Bell", bell_state_string, device)
    bell_discovery_entry['json_attributes_topic'] = attributes_string
    bell_discovery_entry['icon'] = "mdi:bell"
    bell_discovery_entry['command_topic'] = get_discovery_roster_switch_command_path(id_string + "_bell")

    roster_command_topics[bell_discovery_entry['command_topic']] = entry
    subscribe(bell_discovery_entry['command_topic'], on_bell_command_received)

    publish_object(bell_discovery_string, bell_discovery_entry, 0, True)

    # Publish/subscribe to the horn
    horn_state_string = get_roster_path(id_string) + "/F2"
    horn_discovery_string = get_discovery_roster_switch_path(id_string + "_horn")
    horn_discovery_entry = get_discovery_object(id_string + " Horn", horn_state_string, device)
    horn_discovery_entry['json_attributes_topic'] = attributes_string
    horn_discovery_entry['icon'] = "mdi:bugle"
    horn_discovery_entry['command_topic'] = get_discovery_roster_switch_command_path(id_string + "_horn")

    roster_command_topics[horn_discovery_entry['command_topic']] = entry
    subscribe(horn_discovery_entry['command_topic'], on_horn_command_received)

    publish_object(horn_discovery_string, horn_discovery_entry, 0, True)

    # Publish/subscribe to mute
    mute_state_string = get_roster_path(id_string) + "/F8"
    mute_discovery_string = get_discovery_roster_switch_path(id_string + "_mute")
    mute_discovery_entry = get_discovery_object(id_string + " Mute", mute_state_string, device)
    mute_discovery_entry['json_attributes_topic'] = attributes_string
    mute_discovery_entry['icon'] = "mdi:volume-off"
    mute_discovery_entry['command_topic'] = get_discovery_roster_switch_command_path(id_string + "_mute")

    roster_command_topics[mute_discovery_entry['command_topic']] = entry
    subscribe(mute_discovery_entry['command_topic'], on_mute_command_received)

    publish_object(mute_discovery_string, mute_discovery_entry, 0, True)

roster_discovery_string = get_discovery_roster_select_path("roster")
roster_discovery_entry = get_discovery_object("Roster", roster_discovery_string, get_model_railroad_device())
roster_discovery_entry['command_topic'] = get_discovery_roster_select_command_path("roster")
roster_discovery_entry['state_topic'] = roster_discovery_entry['command_topic']
roster_discovery_entry['options'] = roster_names
roster_discovery_entry['retain'] = True
publish_object(roster_discovery_string, roster_discovery_entry, 0, True)
