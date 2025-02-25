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
            return None, None, "Address not found"
        
        location = geocode_result[0]['geometry']['location']
        address_coords = (location['lat'], location['lng'])
        distance = geodesic(CRASH_SITE, address_coords).miles
        
        if distance <= 3:
            return address_coords, True, "High Damage Zone ✅"
        elif distance <= 5:
            return address_coords, True, "Moderate Damage Zone ✅"
        elif distance <= 7:
            return address_coords, True, "Low Damage Zone ✅"
        else:
            return address_coords, False, "Outside Damage Zone ❌"
    except Exception as e:
        return None, None, f"Error: {str(e)}"

# Streamlit UI
st.title("Property Damage Zone Checker")
address = st.text_input("Enter an address:")

if st.button("Check Address"):
    coords, in_zone, message = is_within_damage_zone(address)

    if coords:
        # ✅ Store message in session state for persistent display
        st.session_state.zone_message = message

        # ✅ Create a map and store it in session state
        m = folium.Map(location=CRASH_SITE, zoom_start=12)

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

# ✅ Display the map from session state (so it doesn't disappear)
if st.session_state.map_data:
    st_folium(st.session_state.map_data, width=725, height=500)

# ✅ Display the zone status message **below the "Check Address" button**
if st.session_state.zone_message:
    st.markdown(f"### {st.session_state.zone_message}")
