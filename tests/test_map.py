import folium
from backend.map import MapUtil


def test_create_folium_map_returns_map():
    data = [
        (37.7749, -122.4194, 10, "2021-01-01T00:00:00Z"),
        (37.7750, -122.4195, 12, "2021-01-01T00:05:00Z"),
    ]
    fmap = MapUtil.create_folium_map(data)
    assert isinstance(fmap, folium.Map)


def test_create_folium_map_empty():
    assert MapUtil.create_folium_map([]) is None
