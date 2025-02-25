import streamlit as st
import googlemaps
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic

# Set up Google Maps API
API_KEY = "AIzaSyC2Lr7iKIXJnNKgVjS8Gcz0C6l__NstQfo"  # Replace this with your actual API key
gmaps = googlemaps.Client(key=API_KEY)

# Define the crash site coordinates (center of the damage zone)
CRASH_SITE = (25.997, -97.156)  # Replace with actual coordinates
DAMAGE_RADIUS_MILES = 7  # Max damage radius

def is_within_damage_zone(address):
    """Checks if the address is within the 7-mile damage zone."""
    try:
        geocode_result = gmaps.geocode(address)
        if not geocode_result:
            return None, None, "Address not found"
        
        location = geocode_result[0]['geometry']['location']
        address_coords = (location['lat'], location['lng'])
        distance = geodesic(CRASH_SITE, address_coords).miles
        
        if distance <= DAMAGE_RADIUS_MILES:
            return address_coords, True, "Within damage zone ✅"
        else:
            return address_coords, False, "Outside damage zone ❌"
    except Exception as e:
        return None, None, f"Error: {str(e)}"

# Streamlit UI
st.title("Property Damage Zone Checker")
address = st.text_input("Enter an address:")

if st.button("Check Address"):
    coords, in_zone, message = is_within_damage_zone(address)
    
    if coords:
        st.write(message)
        
        # Create the map
        map_center = CRASH_SITE if in_zone else coords
        m = folium.Map(location=map_center, zoom_start=12)
        
        # Add crash site marker
        folium.Marker(CRASH_SITE, popup="Crash Site", icon=folium.Icon(color="red", icon="warning"))
        
        # Add user address marker
        icon_color = "green" if in_zone else "red"
        icon_symbol = "ok-sign" if in_zone else "remove-sign"
        folium.Marker(
            coords, 
            popup=address, 
            icon=folium.Icon(color=icon_color, icon=icon_symbol)
        ).add_to(m)
        
        # Display the map
        folium_static(m)
    else:
        st.error(message)
