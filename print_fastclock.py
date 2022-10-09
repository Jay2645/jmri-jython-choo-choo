import java
import java.beans
import jmri

timebase = jmri.InstanceManager.getDefault(jmri.Timebase)

fast_clock_path = get_utility_state_path("fast_clock")
publish(fast_clock_path, str(timebase.getTime()), 0, True)

class TimeListener(java.beans.PropertyChangeListener):
    def propertyChange(self, event):
        publish(fast_clock_path, str(timebase.getTime()), 0, True)

timebase.addMinuteChangeListener(TimeListener())

time_discovery_string = get_discovery_utility_sensor_path("fast_clock")

time_discovery_entry = get_discovery_object("Fast Clock", fast_clock_path, get_model_railroad_device())
time_discovery_entry['device_class'] = "timestamp"

publish_object(time_discovery_string, time_discovery_entry, 0, True)