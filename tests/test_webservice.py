from backend.datastore import SQLiteBackend, Datastore
from backend.util import GeoPoint
from backend.webservice import WebService
from backend.map import MapUtil


def test_index_returns_html(tmp_path):
    db_file = tmp_path / "test.db"
    ds = Datastore(lambda: SQLiteBackend(db_path=str(db_file)))
    ds.insert_points([GeoPoint(1.0, 2.0, 3.0, "2024-01-01T00:00:00Z")])
    ds.db_worker.task_queue.join()

    ws = WebService(ds, MapUtil())
    with ws.app.app_context():
        html = ws.index()
    assert "<div" in html

    ds.db_worker.stop()
    ds.db_worker.join(timeout=1)
