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
from sqlalchemy import create_engine, text

# Datenbankverbindung herstellen
engine = create_engine('postgresql://localhost/geolocation_db')

# Daten aus der Datenbank abrufen
query = text("SELECT latitude AS lat, longitude AS lon, timestamp AS time FROM gps_data")
data = pd.read_sql(query, engine)

# Karte initialisieren
m = folium.Map(location=[data['lat'].mean(), data['lon'].mean()], zoom_start=14)

# Punkte & Linien hinzufügen
coordinates = []
for _, point in data.iterrows():
    folium.Marker([point["lat"], point["lon"]], popup=point["time"]).add_to(m)
    coordinates.append([point["lat"], point["lon"]])

folium.PolyLine(coordinates, color="blue").add_to(m)

# Karte anzeigen
m.save("bewegungsprofil.html")