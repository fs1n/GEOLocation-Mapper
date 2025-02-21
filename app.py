"""
Author: Frederik Sinniger
Date Created: 21.02.2025
Version: 0.0.1

Description:
    Main App for the Geolocation project, Serving the Flask app.

Dependencies:
    - Flask
    - SQLAlchemy

Docs:
    To Serve Folium Maps with Flask: https://python-visualization.github.io/folium/latest/advanced_guide/flask.html

"""
from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
import folium
from folium.plugins import PolyLineTextPath
import signal
import sys
import atexit
from datetime import datetime

# Flask app setup
app = Flask(__name__)

# Database setup
engine = create_engine('postgresql://localhost/geolocation_db')
db = scoped_session(sessionmaker(bind=engine))

def fetch_gps_data():
    """
    Fetch GPS data from the database.
    Returns a list of tuples containing latitude, longitude, elevation, and timestamp.
    """
    try:
        gps_data = db.execute(text("SELECT latitude, longitude, elevation, timestamp FROM gps_data ORDER BY timestamp")).fetchall()
        return gps_data
    except Exception as e:
        print(f"Error fetching GPS data: {e}")
        return []

def create_folium_map(gps_data):
    """
    Create a Folium map with GPS data displayed as lines.
    Hovering over the line shows the timestamp and shortened coordinates.
    """
    if not gps_data:
        return None

    # Create a Folium map centered on the first GPS point
    map_center = [gps_data[0][0], gps_data[0][1]]
    folium_map = folium.Map(location=map_center, zoom_start=13, tiles="OpenStreetMap")

    # Extract coordinates and timestamps
    coordinates = [(point[0], point[1]) for point in gps_data]
    timestamps = [point[3] for point in gps_data]

    # Create a PolyLine
    line = folium.PolyLine(
        locations=coordinates,
        color="blue",
        weight=5,
        opacity=0.7,
        tooltip="GPS Path"  # Single tooltip for the entire line
    )

    # Add the line to the map
    line.add_to(folium_map)

    # Optional: Add directional arrows
    PolyLineTextPath(
        line,
        text="➤",
        repeat=True,
        offset=7,
        attributes={"fill": "blue", "font-size": "12"}
    ).add_to(folium_map)

    return folium_map

@app.route('/')
def index():
    """
    Render the Folium map in the Flask app.
    """
    # Fetch GPS data from the database
    gps_data = fetch_gps_data()

    # Create the Folium map
    folium_map = create_folium_map(gps_data)

    if folium_map:
        # Save the map to an HTML string
        map_html = folium_map._repr_html_()
    else:
        map_html = "<p>No GPS data available.</p>"

    # Render the map in the template
    return render_template('index.html', map_html=map_html)

@app.route('/editor')
def editor():
    """Render the manual map editor page."""
    # Remove Folium map initialization here
    return render_template('editor.html')  # No map_html passed

@app.route('/save_manual_data', methods=['POST'])
def save_manual_data():
    """Save manually added markers to the database."""
    data = request.get_json()
    overwrite = data.get('overwrite', False)
    
    try:
        if overwrite:
            # Delete existing data
            db.execute(text("DELETE FROM gps_data"))
            db.commit()

        # Insert new data
        for point in data['points']:
            db.execute(
                text("""
                    INSERT INTO gps_data (latitude, longitude, timestamp)
                    VALUES (:lat, :lng, :timestamp)
                """),
                {
                    "lat": point['lat'],
                    "lng": point['lng'],
                    "timestamp": point['timestamp']
                }
            )
        db.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)})
    
def shutdown_handler(signum, frame):
    """
    Handle graceful shutdown.
    """
    print("\nShutting down gracefully...")
    db.remove()  # Close database connections
    sys.exit(0)

def cleanup():
    """
    Clean up resources on exit.
    """
    print("Cleaning up resources...")
    db.remove()  # Close database connections

# Register the shutdown handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, shutdown_handler)

# Register the cleanup function
atexit.register(cleanup)

if __name__ == '__main__':
    app.run(debug=True)