from flask import Flask, render_template
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Database setup
engine = create_engine('postgresql://username:password@localhost/geolocation_db')
db = scoped_session(sessionmaker(bind=engine))

@app.route('/')
def index():
    # Fetch data from the database
    gps_data = db.execute(text("SELECT latitude, longitude FROM gps_data")).fetchall()
    return render_template('index.html', gps_data=gps_data)

if __name__ == '__main__':
    app.run(debug=True)