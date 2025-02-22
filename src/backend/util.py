import json
from dataclasses import dataclass

def get_templates_from_json(filename: str) -> dict:
    with open(filename, 'r') as f:
        return json.load(f)

@dataclass
class GeoPoint:
    latitude: float = 0.0
    longitude: float = 0.0
    elevation: float = 0.0
    timestamp: str = ""

    def __str__(self) -> str:
        return f"POINT| lat: {self.latitude}, lng: {self.longitude}, elev: {self.elevation}, ts: {self.timestamp}"

    @classmethod
    def from_dict(cls, data: dict) -> 'GeoPoint':
        return cls(
            data.get('latitude', 0.0),
            data.get('longitude', 0.0),
            data.get('elevation', 0.0),
            data.get('timestamp', "")
        )
