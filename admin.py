#!/usr/bin/python3
""" DIYHA admin
    Manage the IOT infrastructure from MQTT broker
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

import logging.config
import time
import paho.mqtt.client as mqtt
import requests
import smtplib

from pkg_classes.configmodel import ConfigModel
from pkg_classes.djangomodel import DjangoModel
from pkg_classes.fanhal import FanHAL
from pkg_classes.topicmodel import TopicModel
from pkg_classes.whoview import WhoView
from pkg_classes.timermodel import TimerModel

# Start logging and enable imported classes to log appropriately.

LOGGING_FILE = '/usr/local/admin/logging.ini'
logging.config.fileConfig( fname=LOGGING_FILE, disable_existing_loggers=False )
LOGGER = logging.getLogger(__name__)
LOGGER.info('Application started')

# get the command line arguements

CONFIG = ConfigModel(LOGGING_FILE)

# setup web server updates

DJANGO = DjangoModel(LOGGING_FILE)
DJANGO.set_django_urls(CONFIG.get_django_api_url())

# Location is used to create the switch topics

TOPIC = TopicModel()  # Location MQTT topic
TOPIC.set(CONFIG.get_location())

# Set up who message handler from MQTT broker and wait for client.

WHO = WhoView(LOGGING_FILE, DJANGO)

# initialize status monitoring

FAN = FanHAL(LOGGING_FILE, 12)
FAN.run()

def send_alert_email(title, message):
    """ send email to Dave and Joann """
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login("parttimehacker@gmail.com", "qcbgbnhaybzcehpu")
        mailtext = "Subject: "+title+"\n"+message
        server.sendmail(
            "parttimehacker@gmail.com",
            "parttimemaker@gmail.com",
            mailtext)
        server.sendmail(
            "parttimehacker@gmail.com",
            "jgperrett@cywren.com",
            mailtext)
    except smtplib.SMTPException as exception:
        LOGGER.info('send_alert_mail exception: ' +str(exception))
    server.quit()
    
def email_critical_system_status(msg): 
    """ process alert and fire system messages
    """
    #pylint: disable=unused-argument
        
    payload =  str( msg.payload, 'utf-8' )
    #LOGGER.info(msg.topic, payload)
    
    # only process two critical messages - ignoring the rest
    
    if msg.topic == 'diy/system/fire':
        subject = "FIRE ALERT DOWNGRADE"
        message = "DIYHAS: Fire alert terminated by Alexa or the console."
        if msg.payload == b'ON':
            subject = "FIRE ALERT"
            message = "DIYHAS: Fire alert initiated by Alexa or the console."
        send_alert_email(subject,message)
        
    elif msg.topic == 'diy/system/panic':
        subject = "PANIC ALERT DOWNGRADE"
        message = "DIYHAS: Panic alert terminated by Alexa or the console."
        if msg.payload == b'ON':
            subject = "PANIC ALERT"
            message = "DIYHAS: Panic alert initiated by Alexa or the console."
        send_alert_email(subject,message)
        

# The callback for when a PUBLISH message is received from the server
def on_message(client, user_data, msg):
    """ dispatch to the appropriate MQTT topic handler 
    """
    #pylint: disable=unused-argument
    if msg.topic == 'diy/system/demo':
        if msg.payload == b'ON':
            FAN.silent_mode(False)
            FAN.flash()
        else:
            FAN.silent_mode(True)
    elif msg.topic == 'diy/system/silent':
        if msg.payload == b'ON':
            FAN.silent_mode(True)
        else:
            FAN.silent_mode(False)  
            FAN.flash()  
    elif msg.topic == 'diy/system/fire':
        email_critical_system_status(msg)
        if msg.payload == b'ON':
            FAN.control(True)
        else:
            FAN.control(False)  
    elif msg.topic == 'diy/system/panic':
        email_critical_system_status(msg)
        if msg.payload == b'ON':
            FAN.control(True)
        else:
            FAN.control(False)     
    elif msg.topic == 'diy/system/who':
        email_critical_system_status(msg)
        if msg.payload == b'ON':
            FAN.control(True)
        else:
            FAN.control(False) 
    else:
        FAN.flash()


def on_connect(client, userdata, flags, rc_msg):
    """ Subscribing in on_connect() means that if we lose the connection and
        reconnect then subscriptions will be renewed.
    """
    # pylint: disable=unused-argument
    client.subscribe("diy/system/demo", 1)
    client.subscribe("diy/system/fire", 1)
    client.subscribe("diy/system/panic", 1)
    client.subscribe("diy/system/silent", 1)
    client.subscribe("diy/system/who", 1)
    client.subscribe("diy/+/os", 1)
    client.subscribe("diy/+/pi", 1)
    client.subscribe("diy/+/ip", 1)
    client.subscribe("diy/+/cpu", 1)
    client.subscribe("diy/+/cpucelsius", 1)
    client.subscribe("diy/+/disk", 1)


def on_disconnect(client, userdata, rc_msg):
    """ Subscribing on_disconnect() tilt """
    # pylint: disable=unused-argument
    client.connected_flag = False
    client.disconnect_flag = True
    
    
def initialize_system_topics(client,):
    """ dispatch system messages to subscribers """
    client.publish("diy/system/calibrate", "OFF", 0, True)
    client.publish("diy/system/demo", "ON", 0, True)
    client.publish("diy/system/fire", "OFF", 0, True)
    client.publish("diy/system/panic", "OFF", 0, True)
    client.publish("diy/system/security", "OFF", 0, True)
    client.publish("diy/system/silent", "OFF", 0, True)
    client.publish("diy/system/who", "OFF", 0, True)
    client.publish("diy/system/test", "OFF", 0, True)
    LOGGER.info("Publish / initalize eight (8) system topics")
    
def initialize_sensor_topics(client,):
    """ dispatch locations to sensor servers """
    client.publish("diy/choke/setup", "diy/main/living", 0, True)
    client.publish("diy/cloud/setup", "diy/main/garage", 0, True)
    client.publish("diy/cran/setup", "diy/upper/study", 0, True)
    LOGGER.info("Publish locations to three (3) sensor servers")

def initialize_clock_topics(client,):
    """ dispatch locations to clock servers """
    client.publish("diy/tay/setup", "diy/main/living", 0, True)
    client.publish("diy/bar/setup", "diy/upper/study", 0, True)
    client.publish("diy/bil/setup", "diy/upper/guest", 0, True)
    LOGGER.info("Publish locations to three (3) clock servers")

def initialize_light_topics(client,):
    """ dispatch locations to light servers """
    client.publish("diy/bear/setup", "diy/main/garage", 0, True)
    LOGGER.info("Publish locations to one (1) light servers")

def initialize_alarm_topics(client,):
    """ dispatch locations to alarm servers """
    client.publish("diy/pink/setup", "diy/main/garage", 0, True)
    client.publish("diy/humpy/setup", "diy/upper/study", 0, True)
    LOGGER.info("Publish locations to three (3) alarm servers")


if __name__ == '__main__':

    # Setup MQTT handlers then wait for timed events or messages

    CLIENT = mqtt.Client()
    CLIENT.on_connect = on_connect
    CLIENT.on_disconnect = on_disconnect
    CLIENT.on_message = on_message

    # command line argument for the switch mode - motion activated is the default

    CLIENT.connect(CONFIG.get_broker(), 1883, 60)
    CLIENT.loop_start()

    time.sleep(2) # let MQTT stuff initialize
    
    TIMER = TimerModel(LOGGER, CLIENT)
    
    # set the state of overall system at all diyha devices
    
    initialize_system_topics(CLIENT)
    initialize_clock_topics(CLIENT)
    initialize_sensor_topics(CLIENT)
    initialize_clock_topics(CLIENT)
    initialize_alarm_topics(CLIENT)

    # Loop forever waiting for motion

    while True:
        time.sleep(1.0)
        TIMER.check_for_timed_events()

