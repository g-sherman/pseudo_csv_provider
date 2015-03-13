import csv
import shutil
from tempfile import NamedTemporaryFile

from qgis.core import (QgsVectorLayer, QgsFeature, QgsGeometry, QgsPoint,
                       QgsMapLayerRegistry, QgsFeatureRequest, QgsMessageLog)

logger = lambda msg: QgsMessageLog.logMessage(msg, 'CSV Provider Example', 1)

class CsvLayer():
    """ Pretend we are a data provider """

    dirty = False
    doing_attr_update = False

    def __init__(self, csv_path):
        """ Initialize the layer by reading the CSV file, creating a memory
        layer, and adding records to it """
        # Save the path to the file soe we can update it in response to edits
        self.csv_path = csv_path
        self.csv_file = open(csv_path, 'rb')
        self.reader = csv.reader(self.csv_file)
        self.header = self.reader.next()
        logger(str(self.header))
        # Get sample
        sample = self.reader.next()
        self.field_sample = dict(zip(self.header, sample))
        logger("sample %s" % str(self.field_sample))
        field_name_types = {}
        # create dict of fieldname:type
        for key in self.field_sample.keys():
            if self.field_sample[key].isdigit():
                field_type = 'integer'
            else:
                try:
                    float(self.field_sample[key])
                    field_type = 'real'
                except ValueError:
                    field_type = 'string'
            field_name_types[key] = field_type
        logger(str(field_name_types))
        # Build up the URI needed to create memory layer
        self.uri = self.uri = "Point?crs=epsg:4326"
        for fld in self.header:
            self.uri += '&field={}:{}'.format(fld, field_name_types[fld])

        logger(self.uri)
        # Create the layer
        self.lyr = QgsVectorLayer(self.uri, 'cities.csv', 'memory')
        self.add_records()
        # done with the csv file
        self.csv_file.close()

        # Make connections
        self.lyr.editingStarted.connect(self.editing_started)
        self.lyr.editingStopped.connect(self.editing_stopped)
        self.lyr.committedAttributeValuesChanges.connect(self.attributes_changed)
        self.lyr.committedFeaturesAdded.connect(self.features_added)
        self.lyr.committedFeaturesRemoved.connect(self.features_removed)
        self.lyr.geometryChanged.connect(self.geometry_changed)

        # Add the layer the map
        QgsMapLayerRegistry.instance().addMapLayer(self.lyr)

    def add_records(self):
        """ Add records to the memory layer by reading the CSV file """
        # Return to beginning of csv file
        self.csv_file.seek(0)
        # Skip the header
        self.reader.next()
        self.lyr.startEditing()

        for row in self.reader:
            flds = dict(zip(self.header, row))
            # logger("This row: %s" % flds)
            feature = QgsFeature()
            geometry = QgsGeometry.fromPoint(
                QgsPoint(float(flds['X']), float(flds['Y'])))

            feature.setGeometry(geometry)
            # for key in flds:
            #    logger("setting attribute for |%s|" % key)
            #    feature.setAttribute(feature.fieldNameIndex(key), flds[key])
            feature.setAttributes(row)
            self.lyr.addFeature(feature, True)
        self.lyr.commitChanges()

    def editing_started(self):
        # Connect to the edit buffer so we can capture geometry and attribute
        # changes
        #self.lyr.editBuffer().committedGeometriesChanges.connect(self.geometries_changed)
        self.lyr.editBuffer().committedAttributeValuesChanges.connect(self.attributes_changed)

    def editing_stopped(self):
        # Update the CSV file if changes were committed
        logger("Updating the CSV")
        features = self.lyr.getFeatures()
        tempfile = NamedTemporaryFile(mode='w', delete=False)
        writer = csv.writer(tempfile, delimiter=',')
        # write the header
        writer.writerow(self.header)
        for feature in features:
            row = []
            for fld in self.header:
                # set x and y to current values
                #pt = feature.geometry().asPoint()
                #feature.setAttribute('X', pt.x())
                #feature.setAttribute('Y', pt.y())
                row.append(feature[feature.fieldNameIndex(fld)])
            writer.writerow(row)

        tempfile.close()
        shutil.move(tempfile.name, self.csv_path)

        self.dirty = False

    def attributes_changed(self, layer, changes):
        if not self.doing_attr_update:
            logger("attributes changed")
            self.dirty = True

    def features_added(self, layer, features):
        logger("features added")
        for feature in features:
            self.geometry_changed(feature.id(), feature.geometry())
        self.dirty = True

    def features_removed(self, layer, feature_ids):
        logger("features removed")
        self.dirty = True

    def geometry_changed(self, fid, geom):
            feature = self.lyr.getFeatures(QgsFeatureRequest(fid)).next()
            pt = geom.asPoint()
            logger("Updating feature {} ({}) X and Y attributes to: {}".format(
                fid, feature['NAME'], pt.toString()))
            self.lyr.changeAttributeValue(fid, feature.fieldNameIndex('X'),
                                          pt.x())
            self.lyr.changeAttributeValue(fid, feature.fieldNameIndex('Y'),
                                          pt.y())
