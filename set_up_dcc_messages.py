import jmri
import java

whichDCCppConnection = 0; #which DCCpp connection to use if multiples (0 is 1st connection, 1 is 2nd, etc.)

# create a minimal listener class needed to call sendDCCppMessage()
class PeerListener (jmri.jmrix.dccpp.DCCppListener):
    def message(self, msg):
        return

# function to send a string message to the DCCpp connection
def dccSend(strMessage):
    print("Sending DCC message: " + str(strMessage))
    m = jmri.jmrix.dccpp.DCCppMessage.makeMessage(strMessage)
    tc.sendDCCppMessage(m, dl)

# get the DCCpp connection stuff once
dc = jmri.InstanceManager.getList(jmri.jmrix.dccpp.DCCppSystemConnectionMemo).get(whichDCCppConnection);
tc = dc.getDCCppTrafficController()
dl = tc.addDCCppListener(0xFF,PeerListener())
