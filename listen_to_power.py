import java
import java.beans
import jmri

TRACK_POWER_STRING = "track_power"
TRACK_POWER_COMMAND_TOPIC = get_discovery_utility_switch_command_path(TRACK_POWER_STRING)

class TrackPowerListener(java.beans.PropertyChangeListener):
    def __init__(self, is_power_on):
        self.power_on = is_power_on
        self.publish_power()

    def propertyChange(self, event):
        print("Power changed: " + str(event.newValue))
        self.power_on = event.newValue == jmri.PowerManager.ON
        self.publish_power()

    def get_topic(self):
        return get_utility_state_path(TRACK_POWER_STRING)

    def publish_power(self):
        publish(self.get_topic(), self.get_payload(), 0, True)
        # Also let turnouts know about the power update
        programming_turnout.power_update(self.power_on)

    def get_payload(self):
        if self.power_on:
            return "ON"
        else:
            return "OFF"

def on_track_power_command_received(topic, payload):
    if payload == "ON":
        powermanager.setPower(jmri.PowerManager.ON)
    elif payload == "OFF":
        powermanager.setPower(jmri.PowerManager.OFF)
subscribe(TRACK_POWER_COMMAND_TOPIC, on_track_power_command_received)

power_listener = TrackPowerListener(powermanager.getPower() == jmri.PowerManager.ON)
powermanager.addPropertyChangeListener(power_listener)

# Publish discovery payload
power_discovery_string = get_discovery_utility_switch_path(TRACK_POWER_STRING)
power_discovery_entry = get_discovery_object("Track Power", get_utility_state_path(TRACK_POWER_STRING), get_model_railroad_device())
power_discovery_entry['command_topic'] = TRACK_POWER_COMMAND_TOPIC
power_discovery_entry['retain'] = False
publish_object(power_discovery_string, power_discovery_entry, 0, True)
