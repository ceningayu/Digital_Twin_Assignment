import rasterio
from rasterio.mask import mask
import numpy as np
from shapely.geometry import shape, mapping


def calculate_lst_stats(feature_geojson, raster_path):
    """
    Calculate mean and max LST inside a polygon.

    Parameters
    ----------
    feature_geojson : dict
        GeoJSON feature (Polygon) from Mapbox Draw
    raster_path : str
        Path to LST GeoTIFF

    Returns
    -------
    dict
        {
          "mean_lst": float,
          "max_lst": float
        }
    """

    # Convert GeoJSON geometry to Shapely
    geom = shape(feature_geojson["geometry"])
    geoms = [mapping(geom)]

    with rasterio.open(raster_path) as src:
        out_image, out_transform = mask(
            src,
            geoms,
            crop=True,
            nodata=src.nodata,
            filled=True
        )

        lst = out_image[0].astype(float)

        # Handle NoData and zeros
        nodata = src.nodata
        if nodata is not None:
            lst[lst == nodata] = np.nan

        lst[lst == 0] = np.nan

        if np.isnan(lst).all():
            return {
                "mean_lst": None,
                "max_lst": None
            }

        return {
            "mean_lst": float(np.nanmean(lst)),
            "max_lst": float(np.nanmax(lst))
        }
