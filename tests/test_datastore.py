from backend.datastore import SQLiteBackend, Datastore
from backend.util import GeoPoint


def test_insert_and_fetch(tmp_path):
    db_file = tmp_path / "test.db"
    ds = Datastore(lambda: SQLiteBackend(db_path=str(db_file)))
    points = [GeoPoint(1.0, 2.0, 3.0, "2024-01-01T00:00:00Z")]
    ds.insert_points(points)
    ds.db_worker.task_queue.join()

    fetched = ds.fetch_gps_data()
    assert len(fetched) == 1
    assert fetched[0].latitude == 1.0

    ds.delete_gps_data()
    ds.db_worker.task_queue.join()
    assert ds.fetch_gps_data() == []

    ds.db_worker.stop()
    ds.db_worker.join(timeout=1)
