#!/usr/bin/python3
""" DIYHA Application Configuration Initializer """

# The MIT License (MIT)
#
# Copyright (c) 2021 parttimehacker@gmail.com
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

import logging
import logging.config
import socket
import json
import requests

# GLOBALS

HEADERS = {'Content-type': 'application/json'} # put parameters are json

# General methods

def put(url, info, logger):
    """ REST put json server info to the Django server """
    try:
        response = requests.put(url, data=json.dumps(info), headers=HEADERS)
        response.raise_for_status()
        # Code here will only run if the request is successful
    except requests.exceptions.HTTPError as errh:
        logger.debug(errh)
    except requests.exceptions.ConnectionError as errc:
        logger.debug(errc)
    except requests.exceptions.Timeout as errt:
        logger.debug(errt)
    except requests.exceptions.RequestException as err:
        logger.debug(err)

# Django Model Class

class DjangoModel:
    """ The DjangoModel class is used to encapsulate several RESTful API calls to a
        Django web server. This class is used in my do it yourself home automation system.
    """

    def __init__(self, logging_file):
        """ Prepare for logging, urls and serve ids for REST put """
        logging.config.fileConfig(fname=logging_file, disable_existing_loggers=False)
        # Get the logger specified in the file
        self.logger = logging.getLogger(__name__)
        self.urls = {"status": "/server/status", "assets": "/server/assets", \
            "environment": "/environment", "motion": "/motion"}
        self.ids = {"status": 0, "assets": 0, "environment": 0, "motion": 0}

    def set_django_urls(self, webserver):
        """ Create API strings based on hostname or IP address."""
        for key in self.ids:
            self.urls[key] = webserver + self.urls[key]
            self.get_id(key)

    def get_id(self, key):
        """ Find the server id from the Django database (PIR sensors)."""
        try:
            response = requests.get(self.urls[key])
            info_array = response.json()
            host = socket.gethostname()
            for info in info_array:
                if host == info["name"]:
                    self.ids[key] = info["id"]
                    break
            # Code here will only run if the request is successful
        except requests.exceptions.HTTPError as errh:
            self.logger.debug(errh)
        except requests.exceptions.ConnectionError as errc:
            self.logger.debug(errc)
        except requests.exceptions.Timeout as errt:
            self.logger.debug(errt)
        except requests.exceptions.RequestException as err:
            self.logger.debug(err)

    def put_server_status(self, info):
        """ REST put json cpu status to the Django server """
        info["id"] = self.ids["status"]
        url = self.urls["status"] + "/" + str(self.ids["status"])
        put(url, info, self.logger)

    def put_server_asset(self, info):
        """ REST put json server asset info to the Django server """
        info["id"] = self.ids["assets"]
        url = self.urls["assets"]  + "/" + str(self.ids["assets"])
        put(url, info, self.logger)

    def put_environment(self, info):
        """ REST put json server asset info to the Django server """
        info["id"] = self.ids["environment"]
        url = self.urls["environment"]  + "/" + str(self.ids["environment"])
        put(url, info, self.logger)

    def put_motion(self, info):
        """ REST put json server asset info to the Django server """
        info["id"] = self.ids["motion"]
        url = self.urls["motion"]  + "/" + str(self.ids["motion"])
        put(url, info, self.logger)
