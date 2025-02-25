import streamlit as st
import folium
from streamlit_folium import st_folium
import googlemaps
from geopy.distance import geodesic

GOOGLE_MAPS_API_KEY = "AIzaSyD-0TYSx882QsMrUw_kC-9Ys4EbPPWv8HM"

# Initialize Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

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

# Function to get geolocation using Google Maps API
def get_location(address):
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            return None
    except Exception as e:
        return None  # Prevents crashes if the API request fails

# Address input
address = st.text_input("Enter an address to check its location:")

if address:
    location = get_location(address)

    if location:
        address_coords = (location[0], location[1])
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
            location=[location[0], location[1]],
            popup=f"{address}<br>Distance: {round(distance_miles, 2)} miles<br>{zone}",
            icon=folium.Icon(color="blue" if zone == "Outside Damage Zone" else "black")
        ).add_to(m)

        st.write(f"✅ **{address} is {round(distance_miles, 2)} miles from the launch site → {zone}**")
    else:
        st.write("❌ Address not found. Try again.")

# Show map
st_folium(m, width=725, height=500)
