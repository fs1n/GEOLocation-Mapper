import atexit
import time
from abc import ABC, abstractmethod

try:
    from sqlalchemy import create_engine, text, Result
    from sqlalchemy.orm import scoped_session, sessionmaker
except ImportError:
    import sqlite3

from typing import Sequence, Any, Union
import logging
import threading
import queue
from util import GeoPoint

class StorageBackend(ABC):
    """Interface to database"""
    def __init__(self):
        self.log = logging.getLogger(__name__)

    @abstractmethod
    def execute(self, query: str):
        pass

    @abstractmethod
    def fetch_all_from_query(self, query: str) -> Sequence[Any]:
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def close_and_cleanup(self):
        pass

    def execute_and_commit(self, query: str):
        self.execute(query)
        self.commit()

class SQLiteBackend(StorageBackend):
    """SQLite backend"""

    def __init__(self, *, db_path: str):
        super().__init__()
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.log.info(f"Connected to sqlite database: {db_path}")
        self.create_tables()

    def create_tables(self):
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS gps_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL,
                longitude REAL,
                elevation REAL, 
                timestamp TEXT
            )
            """
        )
        self.commit()

    def execute(self, query: str):
        return self.cursor.execute(query)

    def fetch_all_from_query(self, query: str) -> Sequence[Any]:
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close_and_cleanup(self):
        self.log.debug(f"Closing sqlite connection...")
        self.conn.close()

class PostgresBackend(StorageBackend):
    """PostgreSQL backend"""

    def __init__(self, *, engine_url: str):
        super().__init__()
        # 'postgresql://localhost/geolocation_db'
        self.engine = create_engine(engine_url)
        self.session = scoped_session(sessionmaker(bind=self.engine))
        self.log.info(f"Connected to postgres database: {engine_url}")

    def execute(self, query: str):
        query = text(query)
        return self.session.execute(query)

    def fetch_all_from_query(self, query: str) -> Sequence[Any]:
        query = text(query)
        return self.session.execute(query).fetchall()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close_and_cleanup(self):
        self.log.debug(f"Closing postgres connection...")
        self.session.close()


class DBWorker(threading.Thread):
    def __init__(self, storage_factory):
        super().__init__()
        self.storage_factory = storage_factory
        self.storage = None
        self.task_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.log = logging.getLogger(__name__)

    def run(self):
        self.storage = self.storage_factory()
        while not self.stop_event.is_set():
            try:
                # Each task is a tuple: (callable, args, kwargs, result_queue)
                func, args, kwargs, result_queue = self.task_queue.get(timeout=0.1)
                try:
                    result = func(*args, **kwargs)
                    if result_queue:
                        result_queue.put(result)
                except Exception as e:
                    self.log.error("Error executing DB operation", exc_info=True)
                    if result_queue:
                        result_queue.put(e)
                finally:
                    self.task_queue.task_done()
            except queue.Empty:
                continue
        self.storage.close_and_cleanup()

    def submit(self, func, *args, **kwargs):
        # Create a queue to retrieve a result if needed
        result_queue = queue.Queue()
        self.task_queue.put((func, args, kwargs, result_queue))
        # Block until the operation has finished and return the result
        return result_queue.get()

    def submit_and_forget(self, func, *args, **kwargs):
        self.task_queue.put((func, args, kwargs, None))

    def stop(self):
        self.stop_event.set()


class Datastore:
    """Interface to storage backend"""

    def __init__(self, storage_factory):
        self.log = logging.getLogger(__name__)
        self.db_worker = DBWorker(storage_factory)
        self.db_worker.start()
        atexit.register(self.db_worker.stop)
        self._cache = {}

    def load_gps_data(self):
        """
        Fetch GPS data from the database.
        Returns a list of tuples containing latitude, longitude, elevation, and timestamp.
        """
        def query_func():
            return self.db_worker.storage.fetch_all_from_query(
                "SELECT latitude, longitude, elevation, timestamp FROM gps_data ORDER BY timestamp"
            )
        result = self.db_worker.submit(query_func)
        if not isinstance(result, Exception):
            return result
        else:
            self.log.error("Failed to fetch GPS data", exc_info=True)
            return []

    def fetch_gps_data(self):
        """
        Fetch GPS data from the database.
        Returns a list of GeoPoint objects.
        """
        if not self._cache.get("gps_data"):
            rows = self.load_gps_data()
            self._cache["gps_data"] = [
                GeoPoint(latitude=row[0], longitude=row[1], elevation=row[2], timestamp=row[3])
                for row in rows
            ]
        return self._cache["gps_data"]

    def delete_gps_data(self):
        """Delete all GPS data from the database."""
        def delete_func():
            self.db_worker.storage.execute_and_commit("DELETE FROM gps_data")

        self.db_worker.submit_and_forget(delete_func)
        del self._cache["gps_data"]

    def insert_points(self, points: Union[GeoPoint, Sequence[GeoPoint]]):
        """Insert GPS data into the database."""
        def insert_func(seq):
            for p in seq:
                self.db_worker.storage.execute(
                    f"INSERT INTO gps_data (latitude, longitude, elevation, timestamp) "
                    f"VALUES ({p.latitude}, {p.longitude}, {p.elevation}, '{p.timestamp}')"
                )
            self.db_worker.storage.commit()

        if isinstance(points, GeoPoint):
            points = [points]
        self.db_worker.submit_and_forget(insert_func, points)
        cache_gps_data = self._cache.get("gps_data")
        if cache_gps_data:
            cache_gps_data.extend(points)
        else:
            self._cache["gps_data"] = points

    def revert(self):
        """Roll back the current transaction."""
        res = self.db_worker.submit(lambda: self.db_worker.storage.rollback())
        if not isinstance(res, Exception):
            self.log.debug("Transaction rolled back")
        else:
            self.log.error("Failed to revert transaction", exc_info=True)


