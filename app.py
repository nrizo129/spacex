import streamlit as st
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Set the title
st.title("SpaceX Damage Zone Checker")

# Define launch site coordinates
launch_pad_lat, launch_pad_lon = 25.997, -97.156  

# Define damage zones
damage_zones = {
    "High Damage (Red)": 3 * 1609,
    "Moderate Damage (Orange)": 5 * 1609,
    "Low Damage (Yellow)": 7 * 1609
}

# Create the base map
m = folium.Map(location=[launch_pad_lat, launch_pad_lon], zoom_start=12)

# Add damage zones to the map
colors = {"High Damage (Red)": "red", "Moderate Damage (Orange)": "orange", "Low Damage (Yellow)": "yellow"}
for label, radius in damage_zones.items():
    folium.Circle(
        location=[launch_pad_lat, launch_pad_lon], 
        radius=radius, 
        color=colors[label], 
        fill=True, 
        fill_color=colors[label], 
        fill_opacity=0.3,
        popup=label
    ).add_to(m)

# Address input
address = st.text_input("Enter an address to check its location:")

if address:
    from geopy.exc import GeocoderTimedOut

def get_location(address):
    geolocator = Nominatim(user_agent="geo_checker", timeout=10)  # Added timeout
    try:
        return geolocator.geocode(address)
    except GeocoderTimedOut:
        return None  # Prevents crash if geocoder times out

location = get_location(address)  # Uses the new function


    if location:
        address_coords = (location.latitude, location.longitude)
        launch_coords = (launch_pad_lat, launch_pad_lon)
        distance_miles = geodesic(launch_coords, address_coords).miles

        # Determine damage zone
        if distance_miles <= 3:
            zone = "High Damage Zone (Red)"
        elif distance_miles <= 5:
            zone = "Moderate Damage Zone (Orange)"
        elif distance_miles <= 7:
            zone = "Low Damage Zone (Yellow)"
        else:
            zone = "Outside Damage Zone"

        # Add marker for the entered address
        folium.Marker(
            location=[location.latitude, location.longitude],
            popup=f"{address}<br>Distance: {round(distance_miles, 2)} miles<br>{zone}",
            icon=folium.Icon(color="blue" if zone == "Outside Damage Zone" else "black")
        ).add_to(m)

        st.write(f"✅ **{address} is {round(distance_miles, 2)} miles from the launch site → {zone}**")
    else:
        st.write("❌ Address not found. Try again.")

# Show map
folium_static(m)
