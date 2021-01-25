from flask import Flask, jsonify
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
import matplotlib.pyplot as plt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
station = Base.classes.station


app = Flask(__name__)

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/stations"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    sel = [measurement.station, measurement.date, measurement.prcp]
    results = session.query(*sel).all()

    session.close()

    # Convert list of tuples into normal list
    station_prcp = list(np.ravel(results))

    return jsonify(station_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    sel = [station.id, station.station]
    results = session.query(*sel).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # find latest date
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    latest_date = dt.datetime.strptime(latest_date[0], "%Y-%m-%d")

    # find min date for query
    query_date = latest_date - dt.timedelta(days=365)

    # query to find the most active station
    col = [measurement.station,
       func.count(measurement.date),
      ]
    columns = [
        'Station', 
        'Number of Observations'
    ]
    station_activity = session.query(*col).filter(measurement.station == station.station).group_by(measurement.station).all()
    station_activity = pd.DataFrame(station_activity, columns = columns)

    max_station = station_activity.loc[station_activity['Number of Observations'] == station_activity['Number of Observations'].max()]
    max_station_id = max_station.iloc[0]['Station']

    # query to return station id, name, and min/max/avg temp over the last year
    sel = [station.id, station.station, measurement.date, measurement.tobs]
    results = session.query(*sel).filter(measurement.station == station.station).filter(measurement.date >= query_date).filter(measurement.station == max_station_id).group_by(measurement.station).all()


    session.close()

    # Convert list of tuples into normal list
    tobs_max12m = list(np.ravel(results))

    return jsonify(tobs_max12m)

