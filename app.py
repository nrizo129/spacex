import streamlit as st
import googlemaps
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# ✅ PASTE YOUR GOOGLE MAPS API KEY BELOW
API_KEY = "AIzaSyC2Lr7iKIXJnNKgVjS8Gcz0C6l__NstQfo"

# Initialize Google Maps client
gmaps = googlemaps.Client(key=API_KEY)

# Define the crash site coordinates (center of the damage zone)
CRASH_SITE = (25.997, -97.156)  # Replace with actual coordinates
DAMAGE_ZONES = {
    "High Damage (Red)": 3,
    "Moderate Damage (Orange)": 5,
    "Low Damage (Yellow)": 7
}

# Initialize session state for persistence
if "map_data" not in st.session_state:
    st.session_state.map_data = None
if "zone_message" not in st.session_state:
    st.session_state.zone_message = ""

def is_within_damage_zone(address):
    """Checks if the address is within the 7-mile damage zone."""
    try:
        geocode_result = gmaps.geocode(address)
        if not geocode_result:
            return None, None, "Address not found", None
        
        location = geocode_result[0]['geometry']['location']
        address_coords = (location['lat'], location['lng'])
        distance = geodesic(CRASH_SITE, address_coords).miles
        
        if distance <= 3:
            return address_coords, True, "High Damage Zone ✅", distance
        elif distance <= 5:
            return address_coords, True, "Moderate Damage Zone ✅", distance
        elif distance <= 7:
            return address_coords, True, "Low Damage Zone ✅", distance
        else:
            return address_coords, False, "Outside Damage Zone ❌", distance
    except Exception as e:
        return None, None, f"Error: {str(e)}", None

# Streamlit UI
st.title("Property Damage Zone Checker")

# ✅ Use a form so pressing "Enter" triggers the search
with st.form("address_form"):
    address = st.text_input("Enter an address:")
    submit_button = st.form_submit_button("Check Address")

# ✅ Execute search if "Enter" is pressed or button is clicked
if submit_button and address:
    coords, in_zone, message, distance = is_within_damage_zone(address)

    if coords:
        # ✅ Store message in session state for persistent display
        st.session_state.zone_message = (
            f"**Address:** {address}  \n"
            f"**Distance from crash site:** {distance:.2f} miles  \n"
            f"**Zone Status:** {message}"
        )

        # ✅ Adjust zoom to ensure both crash site and searched address are visible
        map_center = [(CRASH_SITE[0] + coords[0]) / 2, (CRASH_SITE[1] + coords[1]) / 2]
        m = folium.Map(location=map_center, zoom_start=10)

        # ✅ Add damage zones (heat circles)
        colors = {"High Damage (Red)": "red", "Moderate Damage (Orange)": "orange", "Low Damage (Yellow)": "yellow"}
        for label, radius in DAMAGE_ZONES.items():
            folium.Circle(
                location=CRASH_SITE, 
                radius=radius * 1609,  # Convert miles to meters
                color=colors[label], 
                fill=True, 
                fill_color=colors[label], 
                fill_opacity=0.3,
                popup=label
            ).add_to(m)

        # ✅ Add crash site marker
        folium.Marker(
            CRASH_SITE, popup="Crash Site", icon=folium.Icon(color="red", icon="warning")
        ).add_to(m)

        # ✅ Add a marker for the entered address
        folium.Marker(
            coords, 
            popup=f"{address}<br>{message}", 
            icon=folium.Icon(color="green" if in_zone else "red", icon="ok-sign" if in_zone else "remove-sign")
        ).add_to(m)

        # ✅ Store map data in session state so it stays visible
        st.session_state.map_data = m

# ✅ Display the zone status message **between the form and the map**
if st.session_state.zone_message:
    st.markdown(f"### {st.session_state.zone_message}")

# ✅ Display the map from session state (so it doesn't disappear)
if st.session_state.map_data:
    st_folium(st.session_state.map_data, width=725, height=500)
