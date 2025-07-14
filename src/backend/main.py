from .datastore import Datastore, PostgresBackend, SQLiteBackend
from .webservice import WebService
from .map import MapUtil
import logging
import sys
import signal


def main():
    """
    Main entry point for the application.
    """
    # Initialize the logger
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    # Initialize the data source
    try:
        import sqlalchemy
        engine_url = "postgresql://localhost/geolocation_db"
        storage = lambda: PostgresBackend(engine_url=engine_url)
    except ImportError:
        log.warning(f"SQLAlchemy not found. Using SQLite fallback instead.")
        path = "geolocations.db"
        storage = lambda: SQLiteBackend(db_path=path)

    datastore = Datastore(storage)

    # Initialize the map service
    map_util = MapUtil()

    # Initialize the web service
    webservice = WebService(
        datastore=datastore,
        map_util=map_util
    )

    # Start the web service
    webservice.run(host="127.0.0.1")

if __name__ == "__main__":
    main()