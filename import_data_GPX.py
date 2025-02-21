import gpxpy
import gpxpy.gpx
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
import sys
import os
import logging
from tqdm import tqdm  # For progress bar

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database setup
engine = create_engine('postgresql://localhost/geolocation_db')
db = scoped_session(sessionmaker(bind=engine))

def import_gpx(file_path, override=False, dry_run=False, verbose=False):
    """
    Import GPS data from a GPX file into the database.
    If override is True, existing data in the database will be deleted after confirmation.
    If dry_run is True, no changes will be made to the database.
    If verbose is True, detailed progress will be logged.
    """
    try:
        # Check if the GPX file exists
        if not os.path.exists(file_path):
            logging.error(f"GPX file not found: {file_path}")
            return

        # Open and parse the GPX file
        with open(file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
    except Exception as e:
        logging.error(f"Error parsing GPX file: {e}")
        return

    # Check if override is enabled
    if override and not dry_run:
        # Warn the user and ask for confirmation
        logging.warning("WARNING: This will delete all existing data in the database!")
        confirmation = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
        if confirmation != "yes":
            logging.info("Import canceled.")
            return

        # Delete existing data
        try:
            db.execute(text("DELETE FROM gps_data"))
            db.commit()
            logging.info("All existing data has been deleted.")
        except Exception as e:
            logging.error(f"Error deleting existing data: {e}")
            db.rollback()
            return

    # Prepare a list to hold all data points for batch insertion
    data = []

    try:
        # Iterate through tracks, segments, and points
        for track in gpx.tracks:
            for segment in track.segments:
                for point in tqdm(segment.points, desc="Processing points", disable=not verbose):
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

        # Perform batch insertion (if not in dry-run mode)
        if data and not dry_run:
            db.execute(
                text("""
                    INSERT INTO gps_data (latitude, longitude, elevation, timestamp)
                    VALUES (:latitude, :longitude, :elevation, :timestamp)
                """),
                data
            )
            db.commit()
            logging.info(f"Successfully imported {len(data)} data points from {file_path}.")
        elif dry_run:
            logging.info(f"Dry run: {len(data)} data points would be imported from {file_path}.")
        else:
            logging.warning("No valid data points found in the GPX file.")

    except Exception as e:
        logging.error(f"Error inserting data into the database: {e}")
        db.rollback()  # Rollback in case of an error

def validate_arguments(args):
    """
    Validate command-line arguments.
    Returns the GPX file path, override flag, dry-run flag, and verbose flag.
    """
    valid_flags = {"--override", "--dry-run", "--verbose", "--help"}
    override = False
    dry_run = False
    verbose = False
    gpx_file_path = None

    for arg in args[1:]:  # Skip the script name
        arg_lower = arg.lower()  # Make the argument case-insensitive
        if arg_lower == "--override":
            override = True
        elif arg_lower == "--dry-run":
            dry_run = True
        elif arg_lower == "--verbose":
            verbose = True
        elif arg_lower == "--help":
            print_help()
            sys.exit(0)
        elif arg_lower.startswith("--"):
            logging.error(f"Error: Invalid argument '{arg}'. Valid arguments are: --override, --dry-run, --verbose, --help")
            sys.exit(1)
        else:
            if gpx_file_path is not None:
                logging.error("Error: Only one GPX file can be specified.")
                sys.exit(1)
            gpx_file_path = arg

    if gpx_file_path is None:
        logging.error("Error: No GPX file specified.")
        print_help()
        sys.exit(1)

    return gpx_file_path, override, dry_run, verbose

def print_help():
    """Display usage instructions."""
    print("Usage: python import_data.py <gpx_file> [--override] [--dry-run] [--verbose] [--help]")
    print("\nOptions:")
    print("  --override   Delete existing data in the database before import.")
    print("  --dry-run    Simulate the import without making changes to the database.")
    print("  --verbose    Display detailed progress and debugging information.")
    print("  --help       Display this help message and exit.")

if __name__ == '__main__':
    # Validate command-line arguments
    gpx_file_path, override, dry_run, verbose = validate_arguments(sys.argv)

    # Import the GPX file
    import_gpx(gpx_file_path, override, dry_run, verbose)