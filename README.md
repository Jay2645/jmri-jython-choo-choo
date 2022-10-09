Note that this is intended to be a backup for my personal JMRI Jython setup.

I use Home Assistant on LAN 192.168.86.223 running an MQTT server with MQTT discovery turned on. This publishes the roster to that MQTT server and allows for basic control of locomotives from within Home Assistant (and anything else that can use MQTT).

Feel free to use this for inspiration for your own projects, but as this is intended just for my personal setup I will not be providing support. You'll also have to excuse the lack of comments, as this wasn't intended to be public-facing.

I have JMRI set to execute the following scripts in order on startup:
1. set_up_environment.py (prepares the JMRI side of the MQTT enviroment)
2. mqtt_helper.py (definition of MQTT object)
3. mqtt_globals.py (creates MQTT object, basic MQTT alias functions for publish/subscribe, Home Assistant-MQTT glue)
4. shutdown_mqtt.py (tells Home Assistant that the layout controls are unavailable when JMRI closes)
5. print_roster.py (now an empty file I should probably remove... used to print every registered roster entry to the JMRI log)
6. listen_to_throttles.py (publishes all roster entries to MQTT, binds to their throttles to publish changes to MQTT when I change them in JMRI and to tell JMRI about changes I make via MQTT)
7. print_fastclock.py (sends Fast Clock time to MQTT so Home Assistant can manage layout lighting based on time of day)
