"""
Author: Frederik Sinniger
Date Created: 23.02.2025
Version: 0.0.1

Description:
    - Dieses Skript dient dazu, die GPS-Daten aus der Datenbank zu visualisieren.
    - Dazu wird eine Karte mit der Bibliothek 'folium' erstellt.
    - Die Daten werden aus der Datenbank abgerufen und in der Karte visualisiert.

Dependencies:
    - pandas
    - sqlalchemy
    - folium

Docs:
    - https://pandas.pydata.org/docs/
    - https://docs.sqlalchemy.org/en/14/
    - https://python-visualization.github.io/folium/
"""

import folium
import pandas as pd

# Beispiel-Daten (Latitude, Longitude, Zeitstempel)
data = [
    {"lat": 47.3769, "lon": 8.5417, "time": "2025-02-18 08:00:00"},
    {"lat": 47.3790, "lon": 8.5450, "time": "2025-02-18 09:00:00"},
]

# Karte initialisieren
m = folium.Map(location=[47.3769, 8.5417], zoom_start=14)

# Punkte & Linien hinzufügen
coordinates = []
for point in data:
    folium.Marker([point["lat"], point["lon"]], popup=point["time"]).add_to(m)
    coordinates.append([point["lat"], point["lon"]])

folium.PolyLine(coordinates, color="blue").add_to(m)

# Karte anzeigen
m.save("bewegungsprofil.html")
