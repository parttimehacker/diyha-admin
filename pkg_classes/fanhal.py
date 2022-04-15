#!/usr/bin/python3
""" DIYHA Motion Controller:
    Detect PIR motion and create a queue to manage them.
"""

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

import queue
import sys
import time
from threading import Thread
import logging
import logging.config

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!")
    
STATES = [       1,   0,   1,   0,   1,   0,   1,   0,   1,   0,   1,   0, \
      1,   0,   1,   0,   1,   0 ]
    
SLEEP_TIME = [ 0.2, 0.2, 0.2, 0.2, 0.2, 1.0, 1.0, 0.2, 1.0, 0.2, 1.0, 0.2, \
    0.2, 0.2, 0.2, 0.2, 0.2, 3.0  ]

class FanHAL:
    """ Fan light device driver """

    def __init__(self, logging_file, pin):
        """ Initialize device and class defaults """
        logging.config.fileConfig(fname=logging_file, disable_existing_loggers=False)
        # Get the logger specified in the file
        self.logger = logging.getLogger(__name__)
        self.queue = queue.Queue()
        """ Setup interrupts on the GPIO pin and the motion queue. """
        self.channel = pin
        try:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.channel, GPIO.OUT)
        except RuntimeError:
            print("HAL Fan setup error RPi.GPIO!")
        self.sm=0
        self.on = False
        self.silent = False
        self.reset()

    def reset(self,):
        """ Enable interrupts and prepare the callback. """
        try:
            GPIO.output(self.channel,0)
        except RuntimeError:
            print("Error reset output RPi.GPIO!")
        self.on = False
        self.silent = False

    def control(self, turn_on=True):
        """ Turn fan light on or off """
        self.on = turn_on
        self.sm = 0
        
    def silent_mode(self, turn_on=True):
        """ Turn fan light on or off """
        self.silent = turn_on
        self.sm = 0

    def flash(self,):
        """ trigger fan light one time """
        if self.on:
            return
        if self.silent:
            return
        try:
            GPIO.output(self.channel,1)
        except RuntimeError:
            print("Error fan light output 1 RPi.GPIO!")
        time.sleep(0.2)
        try:
            GPIO.output(self.channel,0)
        except RuntimeError:
            print("Error fan light output 0 RPi.GPIO!")
            
    def fan_thread(self,):
        while True:
            if self.on:
                try:
                    GPIO.output(self.channel, STATES[self.sm])
                except RuntimeError:
                    print("HAL Fan output error RPi.GPIO!")
                time.sleep(SLEEP_TIME[self.sm])
                self.sm = self.sm + 1
                if self.sm >= len(STATES):
                    self.sm = 0
            else:
                try:
                    GPIO.output(self.channel, 0)
                except RuntimeError:
                    print("HAL Fan output error RPi.GPIO!")
                time.sleep(1.0)
        
    def run(self):
        """ start the fan light thread and make it a daemon """
        fan = Thread(target=self.fan_thread)
        fan.daemon = True
        fan.start()
