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