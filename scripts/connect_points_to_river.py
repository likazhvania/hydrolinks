from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsProject,
    QgsWkbTypes,
    QgsSpatialIndex
)

# Load water and point layers
water_layer = QgsVectorLayer("path\\Augsburg.gpkg|layername=waterways_osm", "Water", "ogr")
points_layer = QgsVectorLayer("path\\Augsburg.gpkg|layername=buildings_osm_centroids", "Points", "ogr")


# Add layers to the QGIS project
QgsProject.instance().addMapLayer(water_layer)
QgsProject.instance().addMapLayer(points_layer)
# Create a spatial index for the water layer
water_spatial_index = QgsSpatialIndex(water_layer.getFeatures())

# Create an empty memory layer to store the lines
lines_layer = QgsVectorLayer("LineString?crs=" + points_layer.crs().toWkt(), "Lines", "memory")
lines_layer_data = lines_layer.dataProvider()
QgsProject.instance().addMapLayer(lines_layer)

# Iterate through points
for feature in points_layer.getFeatures():
    point_geom = feature.geometry()

    # Find the nearest water segment
    nearest_segment_ids = water_spatial_index.nearestNeighbor(point_geom.asPoint(), 1)
    nearest_segment_id = next(iter(nearest_segment_ids), None)
    if nearest_segment_id is not None:
        nearest_segment = water_layer.getFeature(nearest_segment_id)

        # Get the coordinates of the nearest point on the water segment
        nearest_point_coords = nearest_segment.geometry().nearestPoint(point_geom).asPoint()

        # Create a line geometry connecting the point and the nearest point on the water segment
        line_geometry = QgsGeometry.fromPolylineXY([point_geom.asPoint(), nearest_point_coords])

        # Add the line geometry to the lines layer
        lines_feature = QgsFeature()
        lines_feature.setGeometry(line_geometry)
        lines_layer_data.addFeature(lines_feature)

# Update the lines layer
lines_layer.updateExtents()
