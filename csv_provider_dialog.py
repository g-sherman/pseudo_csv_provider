# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CSVProviderDialog
                                 A QGIS plugin
 Example of "faking" a data provider with PyQGIS
                             -------------------
        begin                : 2015-03-13
        git sha              : $Format:%H$
        copyright            : (C) 2015 by GeoApt LLC
        email                : gsherman@geoapt.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'csv_provider_dialog_base.ui'))


class CSVProviderDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(CSVProviderDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.toolButton.clicked.connect(self.select_file)

    def select_file(self):
        csv_file = QtGui.QFileDialog.getOpenFileName(None, "Select CSV File",
                os.environ['HOME'], 'CSV (*.csv *.txt)')
        if csv_file:
            self.lineEdit.setText(csv_file)

