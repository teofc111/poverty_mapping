import os
from qgis.core import QgsProject, QgsMapSettings, QgsMapRendererParallelJob, QgsMapLayerType
from PyQt5.QtCore import QSize
import time

'''
Automates image export from QGIS for EOX cloudless Sentinel-2 map.
Note: Clip raster by mask layer does not work for WMS maps
'''

## INPUT
output_folder = "data/daysat/2023_grid/"          # Define output folder
shape_name = "grid_phil_2023_extents_epsg4326"    # Define shape name for clipping image tiles from map
map_name = "Sentinel-2 cloudless layer for 2023 by EOX - 4326"      # Define name of Sentinel-2 map layer loaded in QGIS

# Create output folder if it does not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Load the vector layer defining extents
extent_layer = QgsProject.instance().mapLayersByName(shape_name)[0]

# Load raster layer of EOX cloudless Sentinel-2 basemap via WMS
sentinel2_layer = QgsProject.instance().mapLayersByName(map_name)[0]


# Prepare the QGIS map settings
def setup_map_settings():
    map_settings = QgsMapSettings()
    map_settings.setLayers([sentinel2_layer])
    map_settings.setOutputSize(QSize(240, 240)) # Setting output at 240 by 240 pixels
    return map_settings

map_settings = setup_map_settings()

def export_feature(feature):
    try:
        geom = feature.geometry()
        extent = geom.boundingBox()
        map_settings.setExtent(extent)
        
        output_file = os.path.join(output_folder, f"map_{feature.id()}.tif")

        # Adjust output size based on extent
        map_settings.setOutputSize(QSize(240, 240)) # Setting output at 240 by 240 pixels

        # Render the map
        render_job = QgsMapRendererParallelJob(map_settings)
        render_job.start()
        render_job.waitForFinished()

        image = render_job.renderedImage()
        image.save(output_file,"tif")

#         print(f"Exported {output_file}")
    except Exception as e:
        print(f"Failed to export feature {feature.id()}: {e}")

# Process each feature sequentially
for i,feature in enumerate(extent_layer.getFeatures()):
    export_feature(feature)
    if i%100==0:
        print(f'At image {i} of len(extent_layer.getFeatures())')
        time.sleep(5)

print("Export completed.")
