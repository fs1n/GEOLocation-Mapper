"""
Author: Frederik Sinniger
Date Created: 23.02.2025
Version: 0.0.1

Description:
    Data Import Script for GPX files.
    This script imports GPS data from one or more GPX files into a PostgreSQL database.
    The script can be run from the command line with the following options:
    - Specify one or more GPX files to import.
    - Specify a folder containing GPX files to import all files in the folder and its subfolders.
    - Use the --override flag to delete existing data in the database before import.
    - Use the --dry-run flag to simulate the import without making changes to the database.
    - Use the --verbose flag to display detailed progress and debugging information.
    - Use the --help flag to display usage instructions.

Dependencies:
    - gpxpy:
        pip install gpxpy
    - tqdm:
        pip install tqdm
    - SQLAlchemy:
        pip install sqlalchemy

Docs:
    - GPX file format: https://www.topografix.com/gpx.asp
    - gpxpy documentation:
"""

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
        logging.error(f"Error parsing GPX file {file_path}: {e}")
        return

    # Prepare a list to hold all data points for batch insertion
    data = []

    try:
        # Iterate through tracks, segments, and points
        for track in gpx.tracks:
            for segment in track.segments:
                for point in tqdm(segment.points, desc=f"Processing {os.path.basename(file_path)}", disable=not verbose):
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
            logging.warning(f"No valid data points found in {file_path}.")

    except Exception as e:
        logging.error(f"Error inserting data from {file_path} into the database: {e}")
        db.rollback()  # Rollback in case of an error

def find_gpx_files(folder_path):
    """
    Recursively find all .gpx files in the specified folder and its subfolders.
    """
    gpx_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".gpx"):
                gpx_files.append(os.path.join(root, file))
    return gpx_files

def validate_arguments(args):
    """
    Validate command-line arguments.
    Returns the GPX file paths, override flag, dry-run flag, verbose flag, and data folder.
    """
    valid_flags = {"--override", "--dry-run", "--verbose", "--help", "--data-folder"}
    override = False
    dry_run = False
    verbose = False
    data_folder = None
    gpx_files = []

    i = 1
    while i < len(args):
        arg = args[i]
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
        elif arg_lower == "--data-folder":
            if i + 1 >= len(args):
                logging.error("Error: --data-folder requires a folder path.")
                sys.exit(1)
            data_folder = args[i + 1]
            i += 1  # Skip the next argument (folder path)
        elif arg_lower.startswith("--"):
            logging.error(f"Error: Invalid argument '{arg}'. Valid arguments are: --override, --dry-run, --verbose, --data-folder, --help")
            sys.exit(1)
        else:
            gpx_files.append(arg)
        i += 1

    # If --data-folder is specified, find all .gpx files in the folder
    if data_folder:
        if not os.path.isdir(data_folder):
            logging.error(f"Error: Data folder not found: {data_folder}")
            sys.exit(1)
        gpx_files.extend(find_gpx_files(data_folder))

    if not gpx_files:
        logging.error("Error: No GPX files specified.")
        print_help()
        sys.exit(1)

    return gpx_files, override, dry_run, verbose

def print_help():
    """Display usage instructions."""
    print("Usage: python import_data.py <gpx_file> [<gpx_file> ...] [--data-folder <folder>] [--override] [--dry-run] [--verbose] [--help]")
    print("\nOptions:")
    print("  --override     Delete existing data in the database before import.")
    print("  --dry-run      Simulate the import without making changes to the database.")
    print("  --verbose      Display detailed progress and debugging information.")
    print("  --data-folder  Import all .gpx files from the specified folder and its subfolders.")
    print("  --help         Display this help message and exit.")

if __name__ == '__main__':
    # Validate command-line arguments
    gpx_files, override, dry_run, verbose = validate_arguments(sys.argv)

    # Check if override is enabled (only once, before processing files)
    if override and not dry_run:
        # Warn the user and ask for confirmation
        logging.warning("WARNING: This will delete all existing data in the database!")
        confirmation = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
        if confirmation != "yes":
            logging.info("Import canceled.")
            sys.exit(0)

        # Delete existing data
        try:
            db.execute(text("DELETE FROM gps_data"))
            db.commit()
            logging.info("All existing data has been deleted.")
        except Exception as e:
            logging.error(f"Error deleting existing data: {e}")
            db.rollback()
            sys.exit(1)

    # Import each GPX file
    for gpx_file in gpx_files:
        import_gpx(gpx_file, override=False, dry_run=dry_run, verbose=verbose)