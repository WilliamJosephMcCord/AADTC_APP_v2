import streamlit as st
from AADT_v21 import create_map

st.title("AADT Traffic Search")

address = st.text_input("Address")

state = st.selectbox(
    "State",
    [
        "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE",
        "FL", "GA", "ID", "IL", "IN", "KY", "LA", "MA",
        "MD", "ME", "MI", "MN", "MS", "NC", "NH", "NJ",
        "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "VA", "VT", "WA", "WI", "WV"
    ]
)

num_points = st.slider(
    "Number of nearest traffic counts",
    min_value=1,
    max_value=50,
    value=25
)

if st.button("Search"):

    if not address:
        st.error("Please enter an address.")

    else:
        try:
            output_file = create_map(
                address,
                state,
                num_points
            )

            with open(output_file, "r", encoding="utf-8") as f:
                html = f.read()

            st.components.v1.html(
                html,
                height=700,
                scrolling=True
            )

        except Exception as error:
            st.error(f"Unable to create the map: {error}")

st.divider()

st.subheader("Other State Traffic Websites")

st.write(
    "Use these official state traffic websites for states that do "
    "not currently provide the data needed for this project."
)

other_traffic_websites = {
    "AL": "https://aldotgis.dot.state.al.us/TDMPublic/",
    "HI": "https://experience.arcgis.com/experience/3b630bae39bd4d4e824f55d854450a84/page/Traffic-Volume",
    "IA": "https://www.arcgis.com/apps/mapviewer/index.html?webmap=8304ce251dac4c5cbde64c04a4a46c4b",
    "MO": "https://www.modot.org/traffic-volume-maps",
    "MT": "https://mdt.maps.arcgis.com/apps/mapviewer/index.html?webmap=8a0308abed8846b6b533781e7a96eedd",
    "NE": "https://gis.ne.gov/portal/apps/experiencebuilder/experience/?id=0c2801cfc8884cdb8a76269b5f9e21f1",
    "NM": "https://experience.arcgis.com/experience/80e6622cd81f48f788772b737337b9fb",
    "ND": "https://gis.dot.nd.gov/external/ge_html/?viewer=ext_transinfo",
    "UT": "https://data-uplan.opendata.arcgis.com/datasets/52da935542464cdaa29fc872a489b580_13/explore?location=39.489984%2C-111.577404%2C6"
}

for state_code, website_url in other_traffic_websites.items():
    st.markdown(
        f"**{state_code}:** [{website_url}]({website_url})"
    )
