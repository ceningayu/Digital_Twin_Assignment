from rasterio.mask import mask
from shapely.geometry import shape
import geopandas as gpd
import rasterio
import numpy as np

CARBON_CLASS_TO_MG_PER_HA = {
    1: 50,
    2: 110,
    3: 180
}

PIXEL_AREA_HA = 0.01  # 10m x 10m pixel

def calculate_carbon_loss(feature_geojson, raster_path):
    geom = shape(feature_geojson["geometry"])

    gdf = gpd.GeoDataFrame(
        [{"geometry": geom}],
        crs="EPSG:4326"
    ).to_crs("EPSG:28992")

    try:
        with rasterio.open(raster_path) as src:
            masked, _ = mask(
                src,
                gdf.geometry,
                crop=True,
                nodata=src.nodata
            )
    except ValueError:
        return 0.0

    data = masked[0]

    if data.size == 0:
        return 0.0

    total_carbon = 0.0

    for val in data.flatten():
        if val == src.nodata or np.isnan(val):
            continue

        cls = int(round(val))
        if cls in CARBON_CLASS_TO_MG_PER_HA:
            total_carbon += (
                CARBON_CLASS_TO_MG_PER_HA[cls] * PIXEL_AREA_HA
            )

    return round(total_carbon, 2)
