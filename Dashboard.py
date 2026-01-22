import streamlit as st
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.transform import xy
import streamlit.components.v1 as components
from scipy.ndimage import gaussian_filter

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="UT Campus Digital Twin",
    layout="wide"
)

st.title("UT Campus Digital Twin – Urban Development Scenario Tool")

#st.session_state["carbon_class"] = carbon_class
#st.session_state["carbon_transform"] = carbon_transform
#st.session_state["carbon_lookup"] = CARBON_CLASS_TO_MG


# ================= LOAD UT BOUNDARY =================
ut_boundary_path = "data/UT_Boundary.geojson"

ut_boundary = gpd.read_file(ut_boundary_path)
ut_boundary = ut_boundary.set_crs("EPSG:28992", allow_override=True)
ut_boundary = ut_boundary.to_crs("EPSG:4326")

ut_boundary_geojson = ut_boundary.to_json()

# ================= LOAD CHM RASTER =================
chm_path = "data/Forest_CHM.tif"

points = []

with rasterio.open(chm_path) as src:
    chm = src.read(1)
    transform = src.transform

rows, cols = chm.shape
step = 20  # increase for performance, decrease for density

for r in range(0, rows, step):
    for c in range(0, cols, step):
        height = chm[r, c]
        if height > 3:  # filter shrubs/noise
            x, y = xy(transform, r, c)
            points.append((x, y, float(height)))

chm_df = pd.DataFrame(points, columns=["x", "y", "height"])

chm_gdf = gpd.GeoDataFrame(
    chm_df,
    geometry=gpd.points_from_xy(chm_df.x, chm_df.y),
    crs="EPSG:28992"
).to_crs("EPSG:4326")

chm_geojson = chm_gdf.to_json()

# ================= LOAD CARBON STOCK =================
carbon_path = "data/UT_Carbon_Stock_10m_resolution.tif"

with rasterio.open(carbon_path) as src:
    carbon_class = src.read(1)
    carbon_transform = src.transform
    carbon_nodata = src.nodata

CARBON_CLASS_TO_MG = {
    1: 0.50,   # Mg C per pixel
    2: 1.10,
    3: 1.80
}


# ================= LOAD HTML =================
with open("Map.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("__MAPBOX_KEY__", st.secrets["MAPBOX_ACCESS_KEY"])
html = html.replace("__UT_BOUNDARY__", ut_boundary_geojson)
html = html.replace("__CHM_TREES__", chm_geojson)

components.html(html, height=650)
