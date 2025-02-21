import gpxpy
import gpxpy.gpx
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
import sys

# Database setup
engine = create_engine('postgresql://localhost/geolocation_db')
db = scoped_session(sessionmaker(bind=engine))

def import_gpx(file_path, override=False):
    """
    Import GPS data from a GPX file into the database.
    If override is True, existing data in the database will be deleted after confirmation.
    """
    try:
        # Open and parse the GPX file
        with open(file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
    except Exception as e:
        print(f"Error parsing GPX file: {e}")
        return

    # Check if override is enabled
    if override:
        # Warn the user and ask for confirmation
        print("WARNING: This will delete all existing data in the database!")
        confirmation = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
        if confirmation != "yes":
            print("Import canceled.")
            return

        # Delete existing data
        try:
            db.execute(text("DELETE FROM gps_data"))
            db.commit()
            print("All existing data has been deleted.")
        except Exception as e:
            print(f"Error deleting existing data: {e}")
            db.rollback()
            return

    # Prepare a list to hold all data points for batch insertion
    data = []

    try:
        # Iterate through tracks, segments, and points
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    # Extract latitude, longitude, elevation, and timestamp
                    latitude = point.latitude
                    longitude = point.longitude
                    elevation = point.elevation if point.elevation else None
                    timestamp = point.time.isoformat() if point.time else None

                    # Append the data point to the list
                    data.append({
                        "latitude": latitude,
                        "longitude": longitude,
                        "elevation": elevation,
                        "timestamp": timestamp
                    })

        # Perform batch insertion
        if data:
            db.execute(
                text("""
                    INSERT INTO gps_data (latitude, longitude, elevation, timestamp)
                    VALUES (:latitude, :longitude, :elevation, :timestamp)
                """),
                data
            )
            db.commit()
            print(f"Successfully imported {len(data)} data points from {file_path}.")
        else:
            print("No valid data points found in the GPX file.")

    except Exception as e:
        print(f"Error inserting data into the database: {e}")
        db.rollback()  # Rollback in case of an error

if __name__ == '__main__':
    # Check for command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python import_data.py <gpx_file> [--override]")
        sys.exit(1)

    # Get the GPX file path from the command line
    gpx_file_path = sys.argv[1]

    # Check if the override flag is provided
    override = "--override" in sys.argv

    # Import the GPX file
    import_gpx(gpx_file_path, override)