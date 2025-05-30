# -*- coding: utf-8 -*-
# Copyright (C) 2017-2025 Davide Gessa
"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

For detail about GNU see <http://www.gnu.org/licenses/>.
"""

import logging
import time
from threading import Event, Thread
from typing import Dict

from gweatherrouting.core import DataSource, NetworkDataSource, SerialDataSource
from gweatherrouting.core.utils import EventDispatcher, Storage

logger = logging.getLogger("gweatherrouting")


# Every connection can be of type:
# - serial: data port, baudrate, protocol
# - connection: tcpudp, host, data port, protocol


class ConnectionManagerStorage(Storage):
    def __init__(self):
        Storage.__init__(self, "conn-manager")
        self.connections = []
        self.load_or_save_default()


# { type: 'serial|network', protocol: 'nmea0183', direction: 'in|out|both' }
# Serial: { data-port: '/dev/ttyACM0', baudrate: 9600 }
# Network: { network: 'tcp|udp', host: 'localhost', port: '1234' }


class ConnectionManager(EventDispatcher):
    def __init__(self):
        self.storage = ConnectionManagerStorage()
        self.stop_event = Event()
        self.sources: Dict[str, DataSource] = {}
        self.thread = None

    def __del__(self):
        self.stop_event.set()

    def stop_polling(self):
        logger.info("Polling stopped")
        self.stop_event.set()
        if self.thread:
            self.thread.join()
            self.thread = None

    @property
    def connections(self):
        return self.storage.connections

    def plug_all(self):
        logger.info("Plugging all connections")
        self.sources = {}
        for x in self.storage.connections:
            if x["type"] == "serial":
                self.sources[x["data-port"]] = SerialDataSource(
                    x["protocol"], x["direction"], x["data-port"], x["baudrate"]
                )
                if self.sources[x["data-port"]].connect():
                    logger.info("Data source %s connected", x["data-port"])

            elif x["type"] == "network":
                self.sources[x["host"] + ":" + str(x["port"])] = NetworkDataSource(
                    x["protocol"], x["direction"], x["host"], x["port"], x["network"]
                )
                if self.sources[x["host"] + ":" + str(x["port"])].connect():
                    logger.info("Data source %s:%d connected", x["host"], x["port"])

    def add_connection(self, d):
        if d["type"] == "serial":
            if not list(
                filter(
                    lambda x: x["type"] == "serial"
                    and x["data-port"] == d["data-port"],
                    self.connections,
                )
            ):
                self.storage.connections.append(d)
        elif d["type"] == "network":
            if not list(
                filter(
                    lambda x: x["type"] == "network"
                    and x["host"] == d["host"]
                    and x["port"] == d["port"],
                    self.connections,
                )
            ):
                self.storage.connections.append(d)

        self.storage.save()
        self.plug_all()

    def remove_connection(self, d):
        self.storage.connections.remove(d)
        self.storage.save()
        self.plug_all()

    def poll(self):
        dd = []
        rf = 0

        for _, ds in self.sources.items():
            if not ds.connected:
                continue

            rf += 1
            try:
                d = ds.read()
                if len(d):
                    dd += d
            except Exception as e:
                print(e)
                logger.error("Error reading data from source")

        if len(dd) > 0:
            self.dispatch("data", dd)

        if rf < len(self.sources):
            self.stop_event.wait(timeout=30)
            self.plug_all()

        return len(dd)

    def poll_loop(self, b):
        while not self.stop_event.is_set():
            try:
                n = self.poll()
            except Exception as e:
                print(e)
                logger.error("Error polling data")
                n = 0
            if n > 0:
                time.sleep(0.05)
            else:
                time.sleep(0.5)

    def start_polling(self):
        logger.info("Polling started")
        self.stop_event.clear()
        self.thread = Thread(target=self.poll_loop, args=(True,))
        self.thread.start()
