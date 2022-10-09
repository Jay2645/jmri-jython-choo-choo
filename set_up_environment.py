import datetime
import os
import sys

import jmri
import java

from org.python.core.util import StringUtil

sys.path.append(os.path.join(os.environ['JYTHONPATH'], 'dist-packages'))

mqttAdapter = jmri.InstanceManager.getDefault( jmri.jmrix.mqtt.MqttSystemConnectionMemo ).getMqttAdapter()
topic = "utilities/boot_time/state"
payload = str(datetime.datetime.now())

mqttAdapter.publish(topic, payload)
