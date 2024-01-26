# -*- coding: utf-8 -*-
# Copyright (C) 2017-2024 Davide Gessa
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
# flake8: noqa: E402
import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from .settingswindow_charts import SettingsWindowCharts
from .settingswindow_connections import SettingsWindowConnections


class SettingsWindow(SettingsWindowConnections, SettingsWindowCharts):
    def __init__(self, parent, settingsManager, core):
        self.parent = parent
        self.core = core
        self.settingsManager = settingsManager

        self.builder = Gtk.Builder()
        self.builder.add_from_file(
            os.path.abspath(os.path.dirname(__file__)) + "/settingswindow.glade"
        )
        self.builder.connect_signals(self)

        self.window = self.builder.get_object("settings-window")
        self.window.set_default_size(650, 400)

        # self.dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        # self.dialog.add_button("Save", Gtk.ResponseType.OK)

        # self.dialog.show_all ()

        self.builder.get_object("grib-arrow-onground").set_active(
            self.settingsManager.gribArrowOnGround
        )
        self.builder.get_object("grib-arrow-opacity-adjustment").set_value(
            self.settingsManager.gribArrowOpacity
        )

        SettingsWindowConnections.__init__(self, self.parent, settingsManager, core)
        SettingsWindowCharts.__init__(self, self.parent, settingsManager, core)

    def show(self):
        self.window.show_all()
        self.builder.get_object("ais-tab").hide()
        self.builder.get_object("general-tab").hide()

    def close(self):
        self.window.hide()

    def onGribArrowOnGroundChange(self, widget, v):
        self.settingsManager.gribArrowOnGround = widget.get_active()

    def onGribArrowOpacityChange(self, v):
        self.settingsManager.gribArrowOpacity = v.get_value()
