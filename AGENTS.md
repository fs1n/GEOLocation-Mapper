# Guidelines for AI Contributors

- Run `flake8 src` and `PYTHONPATH=src pytest` after modifying code. A `setup.cfg` is provided with lax rules.
- The project is a simple Flask app that displays GPS data from a SQLite/Postgres database on a Folium map. Key modules are in `src/backend`.
- Tests are located in `tests/` and rely on the `backend` package. Ensure threads from `Datastore.DBWorker` are stopped in tests.
- Use relative imports within the `backend` package. `src/__init__.py` marks the package root.
- Keep feature descriptions short and precise.
