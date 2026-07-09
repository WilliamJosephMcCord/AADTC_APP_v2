import pandas as pd
import geopandas as gpd
import folium
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2
from pyproj import Transformer
from pathlib import Path
import json

# BASE DIRECTORY
BASE_DIR = Path(__file__).resolve().parent

# FILE PATHS
EXCEL_FILE = BASE_DIR / "States From Excel" / "AADTC_annualized_statistics.xlsx"
OUTPUT_MAP = "traffic_map.html"

# STATE CONFIGS

STATE_CONFIGS = {
    "FL": {"type": "shapefile", "shapefile": BASE_DIR / "Florida" / "Florida.shp"},
    "AR": {"type": "shapefile", "shapefile": BASE_DIR / "Arkansas" / "Arkansas.shp"},#send this to its own excel sheet
    "CT": {"type": "shapefile", "shapefile": BASE_DIR / "Connecticut" / "Connecticut.shp"},
    "CO": {"type": "shapefile", "shapefile": BASE_DIR / "Colorado" / "Colorado.shp"},
    "DE": {"type": "shapefile", "shapefile": BASE_DIR / "Delaware" / "Delaware.shp"},
    "ID": {"type": "shapefile", "shapefile": BASE_DIR / "Idaho" / "Idaho.shp"},
    "IL": {"type": "shapefile", "shapefile": BASE_DIR / "Illinois" / "Illinois.shp"},
    "IN": {"type": "shapefile", "shapefile": BASE_DIR / "Indiana" / "Indiana.shp"},
    "KY": {"type": "shapefile", "shapefile": BASE_DIR / "Kentucky" / "Kentucky.shp"},
    "LA": {"type": "shapefile", "shapefile": BASE_DIR / "Louisiana" / "Louisiana.shp"},
    "ME": {"type": "shapefile", "shapefile": BASE_DIR / "Maine" / "Maine.shp"},
    "MD": {"type": "shapefile", "shapefile": BASE_DIR / "Maryland" / "Maryland.shp"},
    "MI": {"type": "shapefile", "shapefile": BASE_DIR / "Michigan" / "Michigan.shp"},
    "MA": {"type": "shapefile", "shapefile": BASE_DIR / "Massachusetts" / "Massachusetts.shp"},
    "MN": {"type": "shapefile", "shapefile": BASE_DIR / "Minnesota" / "Minnesota.shp"},
    "NH": {"type": "shapefile", "shapefile": BASE_DIR / "New Hampshire" / "New Hampshire.shp"},
    "NJ": {"type": "shapefile", "shapefile": BASE_DIR / "New Jersey" / "New Jersey.shp"},
    "OH": {"type": "shapefile", "shapefile": BASE_DIR / "Ohio" / "Ohio.shp"},
    "OK": {"type": "shapefile", "shapefile": BASE_DIR / "Oklahoma" / "Oklahoma.shp"},
    "OR": {"type": "shapefile", "shapefile": BASE_DIR / "Oregon" / "Oregon.shp"},
    "PA": {"type": "shapefile", "shapefile": BASE_DIR / "Pennsylvania" / "Pennsylvania.shp"},
    "RI": {"type": "shapefile", "shapefile": BASE_DIR / "Rhode Island" / "Rhode Island.shp"},
    "VT": {"type": "shapefile", "shapefile": BASE_DIR / "Vermont" / "Vermont.shp"},
    "VA": {"type": "shapefile", "shapefile": BASE_DIR / "Virginia" / "Virginia.shp"},

    "SD": {"type": "excel", "sheet": "South Dakota", "epsg": "EPSG:6572", "projected": True},
    "CA": {"type": "excel", "sheet": "California", "epsg": "EPSG:2875", "projected": True},
    "WA": {"type": "excel", "sheet": "Washington", "epsg": "EPSG:3857", "projected": True},
    "WI": {"type": "excel", "sheet": "Wisconsin", "epsg": "EPSG:3071", "projected": True},

    "AK": {"type": "excel", "sheet": "Alaska", "projected": False},
    "AZ": {"type": "excel", "sheet": "Arizona", "projected": False},
    "GA": {"type": "excel", "sheet": "Georgia", "projected": False},
    "NV": {"type": "excel", "sheet": "Nevada", "projected": False},
    "NC": {"type": "excel", "sheet": "North Carolina", "projected": False},
    "NY": {"type": "excel", "sheet": "New York", "projected": False},
    "SC": {"type": "excel", "sheet": "South Carolina", "projected": False},
    "TN": {"type": "excel", "sheet": "Tennessee", "projected": False},
    "TX": {"type": "excel", "sheet": "Texas", "projected": False},
    "WV": {"type": "excel", "sheet": "West Virginia", "projected": False}
}

# CLEANING FUNCTION 
def clean_for_geojson(gdf):
    gdf = gdf.copy()

    for col in gdf.columns:
        if str(gdf[col].dtype).startswith("datetime"):
            gdf[col] = gdf[col].astype(str)

        if gdf[col].dtype == "object":
            gdf[col] = gdf[col].apply(
                lambda x: x.isoformat() if hasattr(x, "isoformat") else x
            )

    return gdf


# FIELD FINDER
def find_aadt_field(gdf):
    candidates = ["AADT", "AATD", "ATD6", "AADT_TO_11", "AADTYR","AADT_AADT_","CUR_AADT","ADT","faadt","Current_AA"]
    col_map = {col.upper(): col for col in gdf.columns}

    for c in candidates:
        if c.upper() in col_map:
            return col_map[c.upper()]

    return None


# DISTANCE
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# GEOCODER
def geocode_address(address):
    geolocator = Nominatim(user_agent="traffic_app", timeout=10)
    return geolocator.geocode(address)


# MAIN FUNCTION
def create_map(address, state, num_points):

    config = STATE_CONFIGS[state]

    location = geocode_address(address)

    if location is None:
        raise ValueError("Address could not be geocoded.")

    search_lat = location.latitude
    search_lon = location.longitude

    m = folium.Map(location=[search_lat, search_lon], zoom_start=15)

    folium.Marker(
        [search_lat, search_lon],
        popup=address,
        tooltip="Search Address"
    ).add_to(m)

    # SHAPEFILE BRANCH
    if config["type"] == "shapefile":

        gdf = gpd.read_file(str(config["shapefile"]))
        gdf = gdf.to_crs("EPSG:4326")

        field = find_aadt_field(gdf)

        centroids = gdf.geometry.centroid
        gdf["Lat"] = centroids.y
        gdf["Lon"] = centroids.x

        gdf["Distance_Miles"] = gdf.apply(
            lambda row: haversine(search_lat, search_lon, row["Lat"], row["Lon"]),
            axis=1
        )

        nearest = gdf.sort_values("Distance_Miles").head(num_points)

        # CLEAN BEFORE SERIALIZATION
        nearest = clean_for_geojson(nearest)

        folium.GeoJson(
            json.loads(nearest.to_json()),
            tooltip=folium.GeoJsonTooltip(fields=[field] if field else [])
        ).add_to(m)

    # EXCEL BRANCH
    
    else:

        sheet_name = config["sheet"]
        use_projected = config["projected"]

        transformer = None
        if use_projected:
            transformer = Transformer.from_crs(
                config["epsg"],
                "EPSG:4326",
                always_xy=True
            )

        def get_lat_lon(row):
            if use_projected:
                lon, lat = transformer.transform(row["X"], row["Y"])
                return lat, lon
            else:
                return row["Latitude"], row["Longitude"]

        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)

        df["Lat"], df["Lon"] = zip(*df.apply(get_lat_lon, axis=1))

        df["Distance_Miles"] = df.apply(
            lambda row: haversine(search_lat, search_lon, row["Lat"], row["Lon"]),
            axis=1
        )

        nearest = df.sort_values("Distance_Miles").head(num_points)

        aadt_field = "AADT" if "AADT" in df.columns else None

        for _, row in nearest.iterrows():
            popup_text = f"""
            AADT: {row[aadt_field] if aadt_field else 'N/A'}<br>
            Distance: {row['Distance_Miles']:.2f} miles
            """

            folium.CircleMarker(
                location=[row["Lat"], row["Lon"]],
                radius=8,
                popup=popup_text,
                fill=True
            ).add_to(m)

    m.save(OUTPUT_MAP)
    return OUTPUT_MAP