from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from carbon_processing import calculate_carbon_loss
from lst_processing import calculate_lst_stats
from heat_prediction import calculate_heat_prediction
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GeoJSONFeature(BaseModel):
    type: str
    geometry: Dict[str, Any]
    properties: Dict[str, Any] | None = None

@app.post("/polygon")
async def receive_polygon(feature: GeoJSONFeature):
    feature_dict = feature.dict()

    carbon_loss = calculate_carbon_loss(
        feature_geojson=feature_dict,
        raster_path="data/UT_Carbon_Stock_10m_resolution.tif"
    )

    lst_stats = calculate_lst_stats(
        feature_geojson=feature_dict,
        raster_path="data/LST_Sept2020_Sept2025_L8_L9.tif"
    )

    heat_prediction = calculate_heat_prediction(
        feature_geojson=feature_dict,
        carbon_loss_MgC=carbon_loss,
        mean_lst=lst_stats["mean_lst"],
        max_lst=lst_stats["max_lst"]
    )

    return {
        "type": "Feature",
        "geometry": feature.geometry,
        "properties": {
            "carbon_loss_MgC": carbon_loss,
            "mean_lst": lst_stats["mean_lst"],
            "max_lst": lst_stats["max_lst"],
            "delta_lst": heat_prediction["delta_lst"],
            "predicted_mean_lst": heat_prediction["predicted_mean_lst"],
            "predicted_max_lst": heat_prediction["predicted_max_lst"],
        }
    }

if __name__ == "__main__":
    uvicorn.run("fast_api:app", host="0.0.0.0", port=8001, reload=True)
