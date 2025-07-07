import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import os

st.title("QLD LotPlan Cadastral Map Viewer + KMZ Downloader")

# Input LotPlans
lotplan_input = st.text_area("Enter LotPlan values (comma-separated):", "6RP702264, 51CP844255")
lotplans = [lp.strip() for lp in lotplan_input.split(",") if lp.strip()]

# Setup map
map_center = [-27.5, 153]
m = folium.Map(location=map_center, zoom_start=6)

# Folder for downloads
download_dir = "downloads"
os.makedirs(download_dir, exist_ok=True)

for lotplan in lotplans:
    st.write(f"🔍 Searching for: {lotplan}")
    base_url = "https://spatial-gis.information.qld.gov.au/arcgis/rest/services/PlanningCadastre/LandParcelPropertyFramework/MapServer/1/query"

    # 1. Display Geometry
    geojson_params = {
        "where": f"lotplan='{lotplan}'",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson"
    }
    r_geojson = requests.get(base_url, params=geojson_params)
    gj = r_geojson.json()
    if gj.get("features"):
        folium.GeoJson(gj, tooltip=lotplan).add_to(m)
    else:
        st.warning(f"No geometry found for {lotplan}")

    # 2. KMZ download
    kmz_params = {
        "where": f"lotplan='{lotplan}'",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "kmz"
    }
    kmz_response = requests.get(base_url, params=kmz_params)
    if kmz_response.status_code == 200 and len(kmz_response.content) > 1000:
        file_path = os.path.join(download_dir, f"{lotplan}.kmz")
        with open(file_path, "wb") as f:
            f.write(kmz_response.content)

        with open(file_path, "rb") as f:
            st.download_button(label=f"⬇️ Download {lotplan}.kmz", data=f, file_name=f"{lotplan}.kmz", mime="application/vnd.google-earth.kmz")
    else:
        st.error(f"Failed to download KMZ for {lotplan}")

# Show the map
st_folium(m, width=700, height=500)
