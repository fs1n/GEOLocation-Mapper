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

        # Create a Folium map centered on the first GPS point
        map_center = [gps_data[0][0], gps_data[0][1]]
        folium_map = folium.Map(location=map_center, zoom_start=13, tiles="OpenStreetMap")

        # Extract coordinates and timestamps
        coordinates = [(point[0], point[1]) for point in gps_data]
        timestamps = [point[3] for point in gps_data]

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
