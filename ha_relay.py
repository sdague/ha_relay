#!/usr/bin/env python
#
# Copyright 2016 Sean Dague
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import daemon
import logging
import sys

import requests
from evdev import InputDevice, categorize, ecodes

# for keeping track of modifiers
SHIFT = False
CTRL = False


def parse_args():
    parser = argparse.ArgumentParser('ha_evdev')
    parser.add_argument('-f', '--foreground',
                        help="run in foreground (don't daemonize)",
                        action='store_true', default=False)
    parser.add_argument('-d', '--dev',
                        help="Input device path",
                        default='/dev/input/event0')
    return parser.parse_args()


def setup_logger(logfile=None):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: "
                                  "%(message)s")
    if logfile is not None:
        fh = logging.FileHandler(logfile)
    else:
        fh = logging.StreamHandler(sys.stdout)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return fh, logger


def call_ha(domain, name, payload=None):
    log = logging.getLogger()
    log.info("Calling HA with %s/%s" % (domain, name))
    url = "http://10.42.0.3:8123/api/services/%s/%s" % (domain, name)
    resp = requests.post(url, json=payload)
    if not resp:
        log.warn("Failed: %s" % resp)


def dispatch(key):
    global SHIFT
    global CTRL
    log = logging.getLogger()
    log.info("Key: %s" % key)
    # Using numbers for internet radio settings
    if key == ecodes.KEY[ecodes.KEY_1]:
        call_ha('script', 'wamc_lr')
    if key == ecodes.KEY[ecodes.KEY_2]:
        call_ha('script', 'rp_lr')
    if key == ecodes.KEY[ecodes.KEY_B] and SHIFT and CTRL:
        log.debug("Blue!")
    # Using letters for light setting


def set_modifiers(event):
    global SHIFT
    global CTRL
    key = categorize(event)
    if key.keycode == ecodes.KEY[ecodes.KEY_LEFTSHIFT]:
        if event.value == 1:
            SHIFT = True
        elif event.value == 0:
            SHIFT = False
    if key.keycode == ecodes.KEY[ecodes.KEY_RIGHTCTRL]:
        if event.value == 1:
            CTRL = True
        elif event.value == 0:
            CTRL = False


def event_loop(dev):
    for event in dev.read_loop():
        try:
            if event.type == ecodes.EV_KEY:
                # sets the modifiers as we go
                set_modifiers(event)
                log = logging.getLogger()
                key = categorize(event)
                log.debug("Raw key: %s" % key)
                # only work on key down events
                if event.value == 1:
                    dispatch(key.keycode)
        except Exception:
            log.exception()


def main():
    args = parse_args()

    if not args.foreground:
        fh, logger = setup_logger('ha_relay.log')
        try:
            with daemon.DaemonContext(files_preserve=[fh.stream, sys.stdout]):
                logger.debug("Starting ha_evdev in daemon mode")
                dev = InputDevice(args.dev)
                event_loop(dev)
        except Exception:
            logger.exception("Something went wrong!")
    else:
        fh, logger = setup_logger()
        logger.debug("Starting ha_evdev in foreground")
        dev = InputDevice(args.dev)
        event_loop(dev)


if __name__ == "__main__":
    main()
