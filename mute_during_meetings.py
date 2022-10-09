import java
import java.beans

import jmri
import jmri.jmrit.automat
import jmri.jmrit.roster

class ThrottleMuter(jmri.jmrit.automat.AbstractAutomaton):
    def init(self):
        sensor_manager = jmri.InstanceManager.getDefault(jmri.SensorManager)
        self.microphone_sensor = sensor_manager.getBySystemName("MSmicrophone")
        self.set_muted(self.microphone_sensor.getRawState() == jmri.Sensor.ACTIVE)

    def handle(self):
        current_state = self.microphone_sensor.getRawState()
        # Block until the sensor is ready
        self.waitSensorChange(current_state, self.microphone_sensor)
        self.set_muted(self.microphone_sensor.getRawState() == jmri.Sensor.ACTIVE)
        return True

    def set_muted(self, is_muted):
        print("Setting mute state to " + str(is_muted))
        roster_list = jmri.jmrit.roster.Roster.getDefault().matchingList(None, None, None, None, None, None, None)
        
        for entry in roster_list.toArray():
            throttle = self.getThrottle(entry)
            if throttle is None:
                continue
            throttle.setF8(is_muted)
            throttle.release(None)

muter = ThrottleMuter()
muter.start()
