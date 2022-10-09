import jmri

# Define the shutdown task
class ShutdownMQTT(jmri.implementation.AbstractShutDownTask):
  def run(self):
    publish(AVAILABILITY_TOPIC_PATH, "offline", 0, True)
    powermanager.setPower(jmri.PowerManager.OFF)
    
shutdown.register(ShutdownMQTT("MQTT Shutdown"))
