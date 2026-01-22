import streamlit as st
import json
from carbon_processing import calculate_carbon_loss
from lst_processing import calculate_lst_stats
from heat_prediction import calculate_heat_prediction
from carbon_processing import calculate_carbon_loss
from lst_processing import calculate_lst_stats
from heat_prediction import calculate_heat_prediction


def run_environmental_analysis(feature_geojson: dict):
    """
    Runs carbon loss, LST statistics, and heat prediction
    for a user-defined polygon (GeoJSON Feature).
    """

    carbon_loss = calculate_carbon_loss(
        feature_geojson=feature_geojson,
        raster_path="data/UT_Carbon_Stock_10m_resolution.tif"
    )

    lst_stats = calculate_lst_stats(
        feature_geojson=feature_geojson,
        raster_path="data/LST_Sept2020_Sept2025_L8_L9.tif"
    )

    heat_prediction = calculate_heat_prediction(
        feature_geojson=feature_geojson,
        carbon_loss_MgC=carbon_loss,
        mean_lst=lst_stats["mean_lst"],
        max_lst=lst_stats["max_lst"]
    )

    return {
        "carbon_loss_MgC": carbon_loss,
        "mean_lst": lst_stats["mean_lst"],
        "max_lst": lst_stats["max_lst"],
        "delta_lst": heat_prediction["delta_lst"],
        "predicted_mean_lst": heat_prediction["predicted_mean_lst"],
        "predicted_max_lst": heat_prediction["predicted_max_lst"],
    }
