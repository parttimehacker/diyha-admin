#!/usr/bin/python3
""" DIYHA Application Configuration Initializer """

# The MIT License (MIT)
#
# Copyright (c) 2019 parttimehacker@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import logging
import logging.config

class TimerModel:
    """ Command line arguement model which expects an MQTT broker hostname or IP address,
        the location topic for the device and an option mode for the switch.
    """

    def __init__(self, logging_file, client, day = 6, night = 21):
        """ Initialize day, night, and LED devices. """
        logging.config.fileConfig(fname=logging_file, disable_existing_loggers=False)
        # Get the logger specified in the file
        self.logger = logging.getLogger(__name__)
        self.client = client
        self.day = day
        self.night = night # 24 hour clock
        # Turn on lights to bright
        self.lights_are_on = False
        self.control_lights("Turn On")

    def control_lights(self, switch):
        """ Dim lights at night or turn up during the day. """
        if switch == "Turn On":
            client.publish("diy/system/silent", "OFF", 0, True)
            client.publish("diy/system/demo", "ON", 0, True)
            self.lights_are_on = True
        else:
            client.publish("diy/system/demo", "OFF", 0, True)
            client.publish("diy/system/silent", "ON", 0, True)
            self.lights_are_on = False

    def check_for_timed_events(self,):
        """ Dim the LED devices at night. """
        now = datetime.datetime.now().time()
        if now.hour <= self.day:
            if self.lights_are_on:
                self.control_lights("Turn Off")
                msg = "Day: Turn On: "+str(now.hour)
                LOGGER.info(msg)
        elif now.hour >= self.night:
            if self.lights_are_on:
                self.control_lights("Turn Off")
                msg = "Night: Turn Off: "+str(now.hour)
                LOGGER.info(msg)
        else:
            if not self.lights_are_on:
                self.control_lights("Turn On")
                msg = "Normal: Turn ON: "+str(now.hour)
                LOGGER.info(msg)
