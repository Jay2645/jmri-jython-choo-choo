import java
import java.beans
import jmri

section_manager = jmri.InstanceManager.getDefault(jmri.SectionManager)

class SectionListener(java.beans.PropertyChangeListener):
    def __init__(self):
        self.is_occupied = False
        self.section = None

    def propertyChange(self, event):
        print(event.newValue)
        
    def get_topic(self):
        return get_roster_state_path(self.roster_entry.getId())

    def publish_loco(self):
        publish(self.get_topic(), self.get_payload(), 0, True)

    def get_payload(self):
        return self.is_occupied

for section in section_manager.getNamedBeanSet():
    listener = SectionListener()
    listener.section = section
    
    section.addPropertyChangeListener(listener)
