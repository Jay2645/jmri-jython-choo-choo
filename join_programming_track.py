import java
import java.beans
import jmri

class ProgrammingTurnoutListener(java.beans.PropertyChangeListener):
    def __init__(self):
        self.turnout = turnouts.provideTurnout("MTprogramming")
        self.turnout.addPropertyChangeListener(self)
        
    def power_update(self, is_power_on):
        if is_power_on:
            self.update_value(self.turnout.getKnownState())     

    def propertyChange(self, event):
        self.update_value(event.newValue)

    def update_value(self, value):
        if value == jmri.Turnout.CLOSED:
            dccSend("1 JOIN")
        elif value == jmri.Turnout.THROWN:
            dccSend("1 PROG")

programming_turnout = ProgrammingTurnoutListener()
