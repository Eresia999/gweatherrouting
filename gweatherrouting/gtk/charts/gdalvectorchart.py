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
from osgeo import ogr

from gweatherrouting.gtk.charts.cm93driver import CM93Driver
from gweatherrouting.gtk.charts.vectordrawer.osmchartdrawer import OSMChartDrawer

from .chartlayer import ChartLayer
from .vectordrawer import CM93ChartDrawer, S57ChartDrawer, SimpleChartDrawer


class GDALVectorChart(ChartLayer):
    def __init__(self, path, settingsManager, metadata=None, enabled=True):
        super().__init__(path, "vector", settingsManager, metadata, enabled)

        self.drawer = None

        drvName = None
        if path.find("geojson") != -1:
            drvName = "GeoJSON"
            self.drawer = SimpleChartDrawer(settingsManager)
        elif path.find("shp") != -1:
            drvName = "ESRI Shapefile"
            self.drawer = SimpleChartDrawer(settingsManager)
        elif path.find(".000") != -1:
            drvName = "S57"
            self.drawer = S57ChartDrawer(settingsManager)
        elif path.find("Cm93") != -1:
            drvName = "CM93"
            self.drawer = CM93ChartDrawer(settingsManager)
        elif path.find("osm") != -1 or path.find("pbf") != -1:
            drvName = "OSM"
            self.drawer = OSMChartDrawer(self.settingsManager)

        if drvName is None and self.drawer is None:
            raise Exception("Invalid format")

        if drvName == "CM93":
            drv = CM93Driver()
        else:
            drv = ogr.GetDriverByName(drvName)
        self.vectorFile = drv.Open(path)

        if self.vectorFile is None:
            raise Exception("Unable to open vector map %s" % path)

    def onRegister(self, onTickHandler=None):
        pass

    def do_draw(self, gpsmap, cr):
        boundingGeometry = self.getBoundingGeometry(gpsmap)
        self.drawer.draw(gpsmap, cr, self.vectorFile, boundingGeometry)

    def do_render(self, gpsmap):
        pass

    def do_busy(self):
        return False

    def do_button_press(self, gpsmap, gdkeventbutton):
        return False
