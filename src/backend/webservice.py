"""
Author: Frederik Sinniger
Date Created: 21.02.2025
Version: 0.0.1

Description:
    Main App for the Geolocation project, Serving the Flask app.

Dependencies:
    - Flask
    - SQLAlchemy

Docs:
    To Serve Folium Maps with Flask: https://python-visualization.github.io/folium/latest/advanced_guide/flask.html

"""
from flask import Flask, render_template, request, jsonify
from .datastore import Datastore
from .map import MapUtil
from .util import get_templates_from_json, GeoPoint
import logging

class WebService:

    def __init__(self, datastore: Datastore, map_util: MapUtil):
        self.ds = datastore
        self.map = map_util
        self.app = Flask(__name__)
        self.log = logging.getLogger(__name__)
        self.register_routes()
        self.templates: dict = get_templates_from_json("templates/templates.json")

    def register_routes(self) -> None:
        # could also be outsourced to a json file
        if not self.app:
            raise Exception("Flask app not initialized.")

        self.app.route('/')(self.index)
        self.app.route('/editor')(self.editor)
        self.app.route('/save_manual_data', methods=['POST'])(self.save_manual_data)

    def run(self, host: str) -> None:
        """
        Start the Flask app.
        """
        if not self.app:
            raise Exception("Flask app not initialized.")
        do_log = True if self.log.getEffectiveLevel() <= logging.DEBUG else False
        self.app.run(host=host, debug=do_log)

    def index(self) -> str:
        """
        Render the Folium map in the Flask app.
        """
        # Fetch GPS data from the database
        gps_data = self.ds.fetch_gps_data()

        # Create the Folium map
        folium_map = self.map.create_folium_map(gps_data)

        if folium_map:
            # Save the map to an HTML string
            map_html = folium_map._repr_html_()
        else:
            map_html = "<p>No GPS data available.</p>"

        # Render the map in the template
        return render_template(self.templates['index'], map_html=map_html)

    def editor(self):
        """Render the manual map editor page."""
        # Remove Folium map initialization here
        return render_template(self.templates['editor'])  # No map_html passed

    def save_manual_data(self):
        """Save manually added markers to the database."""
        data = request.get_json()
        overwrite = data.get('overwrite', False)

        try:
            if overwrite:
                # Delete existing data
                self.ds.delete_gps_data()

            # Insert new data
            points = [GeoPoint.from_dict(point) for point in data['points']]
            self.ds.insert_points(points)

            return jsonify({"status": "success"})
        except Exception as e:
            self.ds.revert()
            self.log.error(f"Failed to save manual data", exc_info=True)
            return jsonify({"status": "error", "message": str(e)})