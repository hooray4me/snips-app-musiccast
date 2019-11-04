#!/usr/bin/env python3.7

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import requests
import json

CONFIG_INI = "config.ini"

MQTT_IP_ADDR: str = "localhost"
MQTT_PORT: int = 1883
MQTT_ADDR: str = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

def apiAction(ipAddress,cmd):
    uri="http://" + str(ipAddress) + "/YamahaExtendedControl/v1/" + str(cmd)
    response = requests.get(uri) 

def apiResponse(ipAddress,cmd):
    uri="http://" + str(ipAddress) + "/YamahaExtendedControl/v1/" + str(cmd)
    response = requests.get(uri)
    return response

class MusicCast(object):

    def __init__(self):
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except Exception:
            self.config = None

        self.start_blocking()

    def execMusicCast_callback(self, hermes, intent_message):

        myaction = intent_message.slots.mcaction.first().value
        ipAddress = self.config.get("secret").get("ip-address")
        if myaction == "on":
            apiAction(ipAddress,"main/setPower?power=on")
            p = "it is turned on"
            hermes.publish_end_session(intent_message.session_id, p)
        elif myaction == "off":
            apiAction(ipAddress,"main/setPower?power=standby")
            p = "it is turned off"
            hermes.publish_end_session(intent_message.session_id, p)
        elif myaction == "play" or myaction == "stop":
            apiAction(ipAddress,"netusb/setPlayback?playback=" + myaction)
            p = "play action is set to " + myaction
            hermes.publish_end_session(intent_message.session_id, p)
        elif myaction == "tell":
            r = apiResponse(ipAddress,"netusb/getPlayInfo")
            p = "the current song is " + str(r.json().get("track")) + " by " + str(r.json().get("artist"))
            hermes.publish_end_session(intent_message.session_id, p)
        elif myaction == "guy show":
            p = "did you mean the nasty muppet show. thats what they should call it"
            hermes.publish_end_session(intent_message.session_id, p)
            r = apiResponse(ipAddress,"main/getStatus")
            if str(r.json().get("power")) == "standby":
                apiAction(ipAddress,"main/setPower?power=on")
            apiAction(ipAddress,"netusb/recallPreset?zone=main&num=2")
            p = "I have turned it on. Bears are fast"
            hermes.publish_end_session(intent_message.session_id, p)
        else:
            hermes.publish_end_session(intent_message.session_id, "bugger, somethings a muck")

    def master_intent_callback(self,hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        if coming_intent == 'hooray4me:musiccast':
            self.execMusicCast_callback(hermes, intent_message)


    # register callback function to its intent and start listen to MQTT bus
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    MusicCast()
