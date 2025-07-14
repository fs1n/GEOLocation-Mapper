import folium
from folium.plugins import PolyLineTextPath
from typing import Sequence, Any, Optional

class MapUtil:
    """Interface to map utilities"""
    def __init__(self):
        pass

    @staticmethod
    def create_folium_map(gps_data: Sequence[Any]) -> Optional[folium.Map]:
        """
        Create a Folium map with GPS data displayed as lines.
        Hovering over the line shows the timestamp and shortened coordinates.
        """
        if not gps_data:
            return None

        # Support both tuple rows and GeoPoint objects
        first = gps_data[0]
        if hasattr(first, "latitude"):
            map_center = [first.latitude, first.longitude]
            coordinates = [(p.latitude, p.longitude) for p in gps_data]
        else:
            map_center = [first[0], first[1]]
            coordinates = [(p[0], p[1]) for p in gps_data]
        folium_map = folium.Map(location=map_center, zoom_start=13, tiles="OpenStreetMap")

        # Create a PolyLine
        line = folium.PolyLine(
            locations=coordinates,
            color="blue",
            weight=5,
            opacity=0.7,
            tooltip="GPS Path"  # Single tooltip for the entire line
        )

        # Add the line to the map
        line.add_to(folium_map)

        # Optional: Add directional arrows
        PolyLineTextPath(
            line,
            text="➤",
            repeat=True,
            offset=7,
            attributes={"fill": "blue", "font-size": "12"}
        ).add_to(folium_map)

        return folium_map
