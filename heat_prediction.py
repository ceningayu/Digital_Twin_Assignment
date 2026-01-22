import math
from shapely.geometry import shape
from typing import Dict, Any

def calculate_heat_prediction(feature_geojson: Dict[str, Any], carbon_loss_MgC: float, mean_lst: float, max_lst: float) -> Dict[str, float]:
    # Parameters from literature for urban heat increase related to vegetation loss
    a = 0.5  # °C max increase for complete vegetation loss
    b = 1.5  # °C fixed impervious surface effect

    geom = shape(feature_geojson["geometry"])
    area_degrees = geom.area

    # Approximate polygon area in m² for EPSG:4326 lon-lat
    mean_lat = geom.centroid.y
    lat_factor = 111000  # meters per degree latitude
    lon_factor = 111000 * abs(math.cos(math.radians(mean_lat)))

    approx_area_m2 = area_degrees * lat_factor * lon_factor
    area_ha = approx_area_m2 / 10000  # convert to hectares

    if area_ha == 0:
        area_ha = 0.01  # avoid division by zero

    carbon_loss_density = carbon_loss_MgC / area_ha  # MgC per ha

    max_carbon_stock = 180.0  # Adjust this based on your study area's max carbon stock (MgC/ha)

    # Vegetation loss percentage capped at 1.0
    veg_loss_percent = min(carbon_loss_density / max_carbon_stock, 1.0)

    # Calculate delta LST: proportion of veg loss scaled by max increase + fixed impervious effect
    delta_lst = (veg_loss_percent * a) + b

    predicted_mean_lst = mean_lst + delta_lst
    predicted_max_lst = max_lst + delta_lst * 1.2

    return {
        "delta_lst": delta_lst,
        "predicted_mean_lst": predicted_mean_lst,
        "predicted_max_lst": predicted_max_lst,
    }
