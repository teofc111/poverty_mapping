import os
from qgis.core import QgsProject, QgsMapSettings, QgsMapRendererParallelJob, QgsMapLayerType
from PyQt5.QtCore import QSize
import time

# Define the output folder
output_folder = "/home/tfc/Desktop/2022/temp2"

# Create output folder if it does not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Load the vector layer defining extents
extent_layer = QgsProject.instance().mapLayersByName("phil_2022_extents_epsg4326")[0]

# Prepare the QGIS map settings
def setup_map_settings():
    map_settings = QgsMapSettings()
    layers = [layer for layer in QgsProject.instance().mapLayers().values() if layer.isValid()]
    map_settings.setLayers([layers[0]])
    map_settings.setOutputSize(QSize(240, 240))
    return map_settings

map_settings = setup_map_settings()

def export_feature(feature):
    try:
        geom = feature.geometry()
        extent = geom.boundingBox()
        map_settings.setExtent(extent)
        
        output_file = os.path.join(output_folder, f"map_{feature.id()}.tif")

        # Adjust output size based on extent
        map_settings.setOutputSize(QSize(240, 240))

        # Render the map
        render_job = QgsMapRendererParallelJob(map_settings)
        render_job.start()
        render_job.waitForFinished()

        image = render_job.renderedImage()
        image.save(output_file,"tif")

        print(f"Exported {output_file}")
    except Exception as e:
        print(f"Failed to export feature {feature.id()}: {e}")

# Process each feature sequentially
for i,feature in enumerate(extent_layer.getFeatures()):
    export_feature(feature)
    if i%100==0:
        print(f'At image {i} of len(extent_layer.getFeatures())')
        time.sleep(5)

print("Export completed.")