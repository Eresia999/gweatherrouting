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


class ProjectPropertiesWindow:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(
            os.path.abspath(os.path.dirname(__file__))
            + "/projectpropertieswindow.glade"
        )
        self.builder.connect_signals(self)

        self.window = self.builder.get_object("project-properties-window")
        self.window.set_default_size(550, 300)

        # self.dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        # self.dialog.add_button("Save", Gtk.ResponseType.OK)

    def show(self):
        self.window.show_all()

    def close(self):
        self.window.hide()
