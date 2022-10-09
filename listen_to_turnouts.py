import java
import java.beans
import jmri

class TurnoutListener(java.beans.PropertyChangeListener):
    def __init__(self, to):
        self.turnout = to
        self.name = to.getUserName()
        self.id = to.getSystemName()[2:]

        device = {}
        device['name'] = self.name
        device['identifiers'] = self.id
        device['suggested_area'] = MODEL_RAILROAD_AREA
        device['configuration_url'] = MODEL_RAILROAD_URL
        device['via_device'] = MODEL_RAILROAD_DEVICE_ID

        # Publish discovery payload
        self.discovery_string = get_discovery_turnout_switch_path(self.name)
        self.discovery_entry = get_discovery_object(self.name, get_turnout_state_path(self.id), device)
        self.discovery_entry['command_topic'] = get_turnout_state_path(self.id)
        self.discovery_entry['retain'] = False
        self.discovery_entry['payload_off'] = "CLOSED"
        self.discovery_entry['payload_on'] = "THROWN"

        self.publish_turnout()

    def propertyChange(self, event):
        self.publish_turnout()

    def publish_turnout(self):
        current_state = self.turnout.getKnownState()
        if current_state == jmri.Turnout.CLOSED:
            self.discovery_entry['icon'] = "mdi:electric-switch-closed"
        elif current_state == jmri.Turnout.THROWN:
            self.discovery_entry['icon'] = "mdi:electric-switch"
        publish_object(self.discovery_string, self.discovery_entry, 0, True)

for to in turnouts.getNamedBeanSet():
    listener = TurnoutListener(to)
    to.addPropertyChangeListener(listener)