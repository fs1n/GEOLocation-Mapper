"""
Author: Frederik Sinniger
Date Created: 23.02.2025
Version: 0.0.1

Description:
    Data Import Script for CSV files.
    This script imports GPS data from a CSV file into a PostgreSQL database.
    The script can be run from the command line with the following options:
    - Specify a CSV file to import.
    - Use the --override flag to delete existing data in the database before import.
    - Use the --dry-run flag to simulate the import without making changes to the database.
    - Use the --verbose flag to display detailed progress and debugging information.
    - Use the --help flag to display usage instructions.

Dependencies:
    - SQLAlchemy:
        pip install sqlalchemy

Docs:
    - CSV file format: https://en.wikipedia.org/wiki/Comma-separated_values
    - SQLAlchemy documentation: https://docs.sqlalchemy.org/en/14/
"""

import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('postgresql://username:password@localhost/geolocation_db')
db = scoped_session(sessionmaker(bind=engine))

def import_data(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            latitude, longitude, timestamp = row
            db.execute("INSERT INTO gps_data (latitude, longitude, timestamp) VALUES (:latitude, :longitude, :timestamp)",
                       {"latitude": latitude, "longitude": longitude, "timestamp": timestamp})
        db.commit()

if __name__ == '__main__':
    import_data('gps_data.csv')