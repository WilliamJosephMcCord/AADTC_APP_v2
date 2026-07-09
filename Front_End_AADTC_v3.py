import streamlit as st
from Engine_AATDC_v6 import create_map

st.title("AADT Traffic Search")

address = st.text_input("Address")

state = st.selectbox(
    "State",
    ["AK","AZ","CA","CO","FL","GA","ID","IL","MD","MI","NC","NH","NV","NY","OH","OK","OR","RI","SC","SD","TX","VT","WA","WI","WV"] 
)

num_points = st.slider(
    "Number of nearest traffic counts",
    1,
    50,
    25
)

if st.button("Search"):

    if not address:
        st.error("Please enter an address.")
        st.stop()

    output_file = create_map(
        address,
        state,
        num_points
    )

    with open(output_file, "r", encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=700, scrolling=True)