import html
import json
import os
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path

import geopandas as gpd
import pandas as pd
from dotenv import load_dotenv
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import GoogleV3
from pyproj import Transformer


# BASE DIRECTORY AND ENVIRONMENT VARIABLES
# AADTC Map/Front_Ends
BASE_DIR = Path(__file__).resolve().parent

# Main project folder:
# AADTC Map
PROJECT_ROOT = BASE_DIR.parent

# Data folder:
# AADTC Map/AATDC_Data_File_Paths
DATA_DIRECTORY = PROJECT_ROOT / "AATDC_Data_File_Paths"


# GOOGLE API KEYS
# AADTC Map/Front_Ends/.env
load_dotenv(BASE_DIR / ".env")

GOOGLE_GEOCODING_API_KEY = os.getenv(
    "GOOGLE_GEOCODING_API_KEY"
)

GOOGLE_MAPS_BROWSER_KEY = os.getenv(
    "GOOGLE_MAPS_BROWSER_KEY"
)

if not GOOGLE_GEOCODING_API_KEY:
    raise RuntimeError(
        "Missing GOOGLE_GEOCODING_API_KEY. "
        "Add it to the local .env file or Streamlit Secrets."
    )

if not GOOGLE_MAPS_BROWSER_KEY:
    raise RuntimeError(
        "Missing GOOGLE_MAPS_BROWSER_KEY. "
        "Add it to the local .env file or Streamlit Secrets."
    )


# FILE PATHS
EXCEL_FILE = BASE_DIR / "AADTC_annualized_statistics_new.xlsx"

OUTPUT_MAP = BASE_DIR / "traffic_map.html"


# STATE CONFIGURATIONS
STATE_CONFIGS = {
    "FL": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Florida" / "Florida.shp"
    },
    "CT": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Connecticut" / "Connecticut.shp"
    },
    "CO": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Colorado" / "Colorado.shp"
    },
    "DE": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Delaware" / "Deleware.shp"
    },
    "DC": {
        "type": "shapefile",
        "shapefile": (
            BASE_DIR / "District of Columbia" / "District of Columbia.shp"
        )
    },
    "ID": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Idaho" / "Idaho.shp"
    },
    "IL": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Illinois" / "Illinois.shp"
    },
    "IN": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Indiana" / "Indiana.shp"
    },
    "KY": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Kentucky" / "Kentucky.shp"
    },
    "LA": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Louisiana" / "Louisiana.shp"
    },
    "ME": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Maine" / "Maine.shp"
    },
    "MD": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Maryland" / "Maryland.shp"
    },
    "MI": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Michigan" / "Michigan.shp"
    },
    "MA": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Massachusetts" / "Massachusetts.shp"
    },
    "MN": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Minnesota" / "Minnesota.shp"
    },
    "MS": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Mississippi" / "Mississippi.shp"
    },
    "NH": {
        "type": "shapefile",
        "shapefile": (
            BASE_DIR / "New Hampshire" / "New Hampshire.shp"
        )
    },
    "NJ": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "New Jersey" / "New Jersey.shp"
    },
    "OH": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Ohio" / "Ohio.shp"
    },
    "OK": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Oklahoma" / "Oklahoma.shp"
    },
    "OR": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Oregon" / "Oregon.shp"
    },
    "PA": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Pennsylvania" / "Pennsylvania.shp"
    },
    "RI": {
        "type": "shapefile",
        "shapefile": (
            BASE_DIR / "Rhode Island" / "Rhode Island.shp"
        )
    },
    "VT": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Vermont" / "Vermont.shp"
    },
    "VA": {
        "type": "shapefile",
        "shapefile": BASE_DIR / "Virginia" / "Virginia.shp"
    },

    "SD": {
        "type": "excel",
        "sheet": "South Dakota",
        "epsg": "EPSG:6572",
        "projected": True
    },
    "CA": {
        "type": "excel",
        "sheet": "California",
        "epsg": "EPSG:2875",
        "projected": True
    },
    "WA": {
        "type": "excel",
        "sheet": "Washington",
        "epsg": "EPSG:3857",
        "projected": True
    },
    "WI": {
        "type": "excel",
        "sheet": "Wisconsin",
        "epsg": "EPSG:3071",
        "projected": True
    },

    "AK": {
        "type": "excel",
        "sheet": "Alaska",
        "projected": False
    },
    "AZ": {
        "type": "excel",
        "sheet": "Arizona",
        "projected": False
    },
    "GA": {
        "type": "excel",
        "sheet": "Georgia",
        "projected": False
    },
    "NV": {
        "type": "excel",
        "sheet": "Nevada",
        "projected": False
    },
    "NC": {
        "type": "excel",
        "sheet": "North Carolina",
        "projected": False
    },
    "NY": {
        "type": "excel",
        "sheet": "New York",
        "projected": False
    },
    "SC": {
        "type": "excel",
        "sheet": "South Carolina",
        "projected": False
    },
    "TN": {
        "type": "excel",
        "sheet": "Tennessee",
        "projected": False
    },
    "TX": {
        "type": "excel",
        "sheet": "Texas",
        "projected": False
    },
    "WV": {
        "type": "excel",
        "sheet": "West Virginia",
        "projected": False
    },
    "AR": {
        "type": "excel",
        "sheet": "Arkansas",
        "projected": False
    }
}


# GOOGLE GEOCODER
geolocator = GoogleV3(
    api_key=GOOGLE_GEOCODING_API_KEY,
    timeout=10
)


def geocode_address(address):
    """
    Convert an address into a geopy Location using Google.
    """

    try:
        return geolocator.geocode(address)

    except GeocoderTimedOut as error:
        raise ValueError(
            "Google took too long to geocode the address."
        ) from error

    except GeocoderServiceError as error:
        raise ValueError(
            f"Google geocoding failed: {error}"
        ) from error


# CLEANING FUNCTIONS
def clean_for_geojson(gdf):
    """
    Convert values that cannot be serialized to valid GeoJSON.
    """

    gdf = gdf.copy()

    for column in gdf.columns:
        if column == gdf.geometry.name:
            continue

        if str(gdf[column].dtype).startswith("datetime"):
            gdf[column] = gdf[column].astype(str)

        elif gdf[column].dtype == "object":
            gdf[column] = gdf[column].apply(clean_value)

    return gdf


def clean_value(value):
    """
    Convert individual values into JSON-safe values.
    """

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return value


def json_safe_number(value):
    """
    Convert a numeric value into a normal Python float or None.
    """

    if value is None or pd.isna(value):
        return None

    return float(value)


# AADT FIELD FINDER
def find_aadt_field(data):
    """
    Find the AADT field even when different states use
    different column names.
    """

    candidates = [
        "AADT",
        "AATD",
        "ATD6",
        "AADT_TO_11",
        "AADTYR",
        "AADT_AADT_",
        "CUR_AADT",
        "ADT",
        "FAADT",
        "CURRENT_AA",
        "LastCNT",
        "ADT_24",
        "CURRENT_VO"
    ]

    column_map = {
        str(column).upper(): column
        for column in data.columns
    }

    for candidate in candidates:
        if candidate.upper() in column_map:
            return column_map[candidate.upper()]

    return None


# DISTANCE FUNCTION
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate straight-line distance in miles between
    two latitude/longitude coordinates.
    """

    earth_radius_miles = 3958.8

    lat1, lon1, lat2, lon2 = map(
        radians,
        [lat1, lon1, lat2, lon2]
    )

    latitude_difference = lat2 - lat1
    longitude_difference = lon2 - lon1

    a = (
        sin(latitude_difference / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(longitude_difference / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius_miles * c


# GOOGLE MAP HTML GENERATOR
def generate_google_map_html(
    search_lat,
    search_lon,
    address,
    matched_address,
    traffic_points=None,
    traffic_geojson=None,
    aadt_field=None
):
    """
    Generate a complete HTML file that displays traffic data
    through the Google Maps JavaScript API.
    """

    traffic_points = traffic_points or []

    map_data = {
        "searchLocation": {
            "lat": float(search_lat),
            "lng": float(search_lon)
        },
        "enteredAddress": address,
        "matchedAddress": matched_address,
        "trafficPoints": traffic_points,
        "trafficGeoJson": traffic_geojson,
        "aadtField": aadt_field
    }

    map_data_json = json.dumps(
        map_data,
        ensure_ascii=False,
        allow_nan=False
    ).replace("</", "<\\/")

    browser_key = html.escape(
        GOOGLE_MAPS_BROWSER_KEY,
        quote=True
    )

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>AADT Traffic Map</title>

    <style>
        html,
        body {{
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}

        #map {{
            width: 100%;
            height: 100%;
        }}

        .info-window {{
            min-width: 190px;
            line-height: 1.5;
        }}

        .info-title {{
            margin-bottom: 6px;
            font-weight: bold;
        }}
    </style>
</head>

<body>
    <div id="map"></div>

    <script>
        const mapData = {map_data_json};

        function escapeHtml(value) {{
            if (value === null || value === undefined) {{
                return "N/A";
            }}

            return String(value)
                .replaceAll("&", "&amp;")
                .replaceAll("<", "&lt;")
                .replaceAll(">", "&gt;")
                .replaceAll('"', "&quot;")
                .replaceAll("'", "&#039;");
        }}

        function initMap() {{
            const searchLocation = mapData.searchLocation;

            const map = new google.maps.Map(
                document.getElementById("map"),
                {{
                    center: searchLocation,
                    zoom: 15,
                    mapTypeId: "roadmap",
                    mapTypeControl: true,
                    streetViewControl: true,
                    fullscreenControl: true
                }}
            );

            const bounds = new google.maps.LatLngBounds();
            bounds.extend(searchLocation);

            const searchMarker = new google.maps.Marker({{
                position: searchLocation,
                map: map,
                title: mapData.matchedAddress,
                label: "S"
            }});

            const searchInfoWindow = new google.maps.InfoWindow({{
                content: `
                    <div class="info-window">
                        <div class="info-title">
                            Search Address
                        </div>

                        <strong>Entered:</strong>
                        ${{escapeHtml(mapData.enteredAddress)}}
                        <br>

                        <strong>Google match:</strong>
                        ${{escapeHtml(mapData.matchedAddress)}}
                    </div>
                `
            }});

            searchMarker.addListener("click", () => {{
                searchInfoWindow.open({{
                    map: map,
                    anchor: searchMarker
                }});
            }});

            mapData.trafficPoints.forEach((point) => {{
                const position = {{
                    lat: point.lat,
                    lng: point.lng
                }};

                bounds.extend(position);

                const trafficMarker = new google.maps.Marker({{
                    position: position,
                    map: map,
                    title: `AADT: ${{point.aadt ?? "N/A"}}`
                }});

                const aadt = escapeHtml(point.aadt);
                const distance = Number(point.distance).toFixed(2);

                const infoWindow = new google.maps.InfoWindow({{
                    content: `
                        <div class="info-window">
                            <div class="info-title">
                                Traffic Count Station
                            </div>

                            <strong>AADT:</strong>
                            ${{aadt}}
                            <br>

                            <strong>Distance:</strong>
                            ${{distance}} miles
                        </div>
                    `
                }});

                trafficMarker.addListener("click", () => {{
                    infoWindow.open({{
                        map: map,
                        anchor: trafficMarker
                    }});
                }});
            }});

            if (
                mapData.trafficGeoJson &&
                Array.isArray(
                    mapData.trafficGeoJson.features
                )
            ) {{
                map.data.addGeoJson(
                    mapData.trafficGeoJson
                );

                map.data.setStyle({{
                    strokeColor: "#d32f2f",
                    strokeOpacity: 0.9,
                    strokeWeight: 5,
                    fillColor: "#d32f2f",
                    fillOpacity: 0.25
                }});

                map.data.forEach((feature) => {{
                    const geometry = feature.getGeometry();

                    if (geometry) {{
                        geometry.forEachLatLng((latLng) => {{
                            bounds.extend(latLng);
                        }});
                    }}
                }});

                const geoJsonInfoWindow =
                    new google.maps.InfoWindow();

                map.data.addListener(
                    "click",
                    (event) => {{
                        let aadt = "N/A";
                        let distance = "N/A";

                        if (mapData.aadtField) {{
                            const fieldValue =
                                event.feature.getProperty(
                                    mapData.aadtField
                                );

                            if (
                                fieldValue !== undefined &&
                                fieldValue !== null
                            ) {{
                                aadt = fieldValue;
                            }}
                        }}

                        const distanceValue =
                            event.feature.getProperty(
                                "Distance_Miles"
                            );

                        if (
                            distanceValue !== undefined &&
                            distanceValue !== null
                        ) {{
                            distance =
                                Number(distanceValue).toFixed(2);
                        }}

                        geoJsonInfoWindow.setContent(`
                            <div class="info-window">
                                <div class="info-title">
                                    Traffic Count Segment
                                </div>

                                <strong>AADT:</strong>
                                ${{escapeHtml(aadt)}}
                                <br>

                                <strong>Distance:</strong>
                                ${{escapeHtml(distance)}} miles
                            </div>
                        `);

                        geoJsonInfoWindow.setPosition(
                            event.latLng
                        );

                        geoJsonInfoWindow.open(map);
                    }}
                );
            }}

            if (
                mapData.trafficPoints.length > 0 ||
                (
                    mapData.trafficGeoJson &&
                    mapData.trafficGeoJson.features.length > 0
                )
            ) {{
                map.fitBounds(bounds);

                google.maps.event.addListenerOnce(
                    map,
                    "bounds_changed",
                    () => {{
                        if (map.getZoom() > 16) {{
                            map.setZoom(16);
                        }}
                    }}
                );
            }}
        }}

        window.initMap = initMap;
    </script>

    <script
        async
        defer
        src="https://maps.googleapis.com/maps/api/js?key={browser_key}&callback=initMap">
    </script>
</body>
</html>
"""

    OUTPUT_MAP.write_text(
        document,
        encoding="utf-8"
    )

    return str(OUTPUT_MAP)


# SHAPEFILE PROCESSING
def process_shapefile(
    config,
    search_lat,
    search_lon,
    num_points
):
    shapefile_path = Path(config["shapefile"])

    if not shapefile_path.exists():
        raise FileNotFoundError(
            f"Shapefile was not found: {shapefile_path}"
        )

    gdf = gpd.read_file(shapefile_path)

    if gdf.crs is None:
        raise ValueError(
            f"The shapefile has no CRS: {shapefile_path}"
        )

    # Use a projected CRS to calculate representative points.
    projected_gdf = gdf.to_crs("EPSG:5070")
    representative_points = (
        projected_gdf.geometry.representative_point()
    )

    representative_points = gpd.GeoSeries(
        representative_points,
        crs="EPSG:5070"
    ).to_crs("EPSG:4326")

    gdf = gdf.to_crs("EPSG:4326")

    gdf["Lat"] = representative_points.y.values
    gdf["Lon"] = representative_points.x.values

    gdf = gdf.dropna(
        subset=["Lat", "Lon"]
    ).copy()

    gdf["Distance_Miles"] = gdf.apply(
        lambda row: haversine(
            search_lat,
            search_lon,
            row["Lat"],
            row["Lon"]
        ),
        axis=1
    )

    nearest = (
        gdf
        .sort_values("Distance_Miles")
        .head(num_points)
        .copy()
    )

    aadt_field = find_aadt_field(nearest)

    nearest = clean_for_geojson(nearest)

    traffic_geojson = json.loads(
        nearest.to_json()
    )

    return traffic_geojson, aadt_field


# EXCEL PROCESSING
def process_excel(
    config,
    search_lat,
    search_lon,
    num_points
):
    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"Excel file was not found: {EXCEL_FILE}"
        )

    sheet_name = config["sheet"]
    use_projected_coordinates = config["projected"]

    transformer = None

    if use_projected_coordinates:
        transformer = Transformer.from_crs(
            config["epsg"],
            "EPSG:4326",
            always_xy=True
        )

    dataframe = pd.read_excel(
        EXCEL_FILE,
        sheet_name=sheet_name
    )

    if use_projected_coordinates:
        required_columns = {"X", "Y"}
    else:
        required_columns = {
            "Latitude",
            "Longitude"
        }

    missing_columns = (
        required_columns - set(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            f"{sheet_name} is missing columns: "
            f"{sorted(missing_columns)}"
        )

    def get_lat_lon(row):
        if use_projected_coordinates:
            longitude, latitude = transformer.transform(
                row["X"],
                row["Y"]
            )

            return latitude, longitude

        return (
            row["Latitude"],
            row["Longitude"]
        )

    coordinates = dataframe.apply(
        get_lat_lon,
        axis=1
    )

    dataframe["Lat"] = coordinates.apply(
        lambda value: value[0]
    )

    dataframe["Lon"] = coordinates.apply(
        lambda value: value[1]
    )

    dataframe = dataframe.dropna(
        subset=["Lat", "Lon"]
    ).copy()

    dataframe["Lat"] = pd.to_numeric(
        dataframe["Lat"],
        errors="coerce"
    )

    dataframe["Lon"] = pd.to_numeric(
        dataframe["Lon"],
        errors="coerce"
    )

    dataframe = dataframe.dropna(
        subset=["Lat", "Lon"]
    ).copy()

    dataframe["Distance_Miles"] = dataframe.apply(
        lambda row: haversine(
            search_lat,
            search_lon,
            row["Lat"],
            row["Lon"]
        ),
        axis=1
    )

    nearest = (
        dataframe
        .sort_values("Distance_Miles")
        .head(num_points)
        .copy()
    )

    aadt_field = find_aadt_field(nearest)

    traffic_points = []

    for _, row in nearest.iterrows():
        aadt_value = None

        if aadt_field:
            aadt_value = clean_value(
                row[aadt_field]
            )

        traffic_points.append({
            "lat": json_safe_number(row["Lat"]),
            "lng": json_safe_number(row["Lon"]),
            "aadt": aadt_value,
            "distance": json_safe_number(
                row["Distance_Miles"]
            )
        })

    return traffic_points


# MAIN FUNCTION
def create_map(address, state, num_points):
    """
    Geocode the address, find nearby traffic stations,
    and generate a Google Maps HTML file.
    """

    address = str(address).strip()
    state = str(state).strip().upper()

    if not address:
        raise ValueError(
            "An address is required."
        )

    if state not in STATE_CONFIGS:
        raise ValueError(
            f"Unsupported state: {state}"
        )

    try:
        num_points = int(num_points)
    except (TypeError, ValueError) as error:
        raise ValueError(
            "Number of points must be an integer."
        ) from error

    if num_points < 1:
        raise ValueError(
            "Number of points must be at least 1."
        )

    config = STATE_CONFIGS[state]

    location = geocode_address(address)

    if location is None:
        raise ValueError(
            "Google could not find the address."
        )

    search_lat = float(location.latitude)
    search_lon = float(location.longitude)

    traffic_points = []
    traffic_geojson = None
    aadt_field = None

    if config["type"] == "shapefile":
        traffic_geojson, aadt_field = (
            process_shapefile(
                config=config,
                search_lat=search_lat,
                search_lon=search_lon,
                num_points=num_points
            )
        )

    elif config["type"] == "excel":
        traffic_points = process_excel(
            config=config,
            search_lat=search_lat,
            search_lon=search_lon,
            num_points=num_points
        )

    else:
        raise ValueError(
            f"Unknown data type for {state}: "
            f"{config['type']}"
        )

    return generate_google_map_html(
        search_lat=search_lat,
        search_lon=search_lon,
        address=address,
        matched_address=location.address,
        traffic_points=traffic_points,
        traffic_geojson=traffic_geojson,
        aadt_field=aadt_field
    )
