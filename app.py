# 1. import Flask
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

import numpy as np
import datetime as dt

# DB setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
#  Create an app, being sure to pass __name__
app = Flask(__name__)


# Define what to do when a user hits the index route
@app.route("/")
def home():
    """List all available api routes."""
    return"""<html>
    <h1>List of all available Honolulu, HI API routes</h1>
    <ul>
    <br>
    <li>
    Return a list of precipitations from last year:
    <br>
    <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
    </li>
    <br>
    <li>
    Return a JSON list of stations from the dataset: 
    <br>
   <a href="/api/v1.0/stations">/api/v1.0/stations</a>
   </li>
    <br>
    <li>
    Return a JSON list of Temperature Observations (tobs) for the previous year:
    <br>
    <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
    </li>
    <br>
    <li>
    Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided:
    <br>Replace &ltstart&gt with a date in Year-Month-Day format.
    <br>
    <a href="/api/v1.0/2017-01-01">/api/v1.0/2017-01-01</a>
    </li>
    <br>
    <li>
    Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive:
    <br>
    Replace &ltstart&gt and &ltend&gt with a date in Year-Month-Day format. 
    <br>
    <br>
    <a href="/api/v1.0/2017-01-01/2017-01-07">/api/v1.0/2017-01-01/2017-01-07</a>
    </li>
    <br>
    </ul>
    </html>
    """



#  Define what to do when a user hits the /precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation from last year"""
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # max_date
    max_date = max_date[0]

    num_days_in_year = 366

    # Calculate the date 1 year ago from the last data point in the database
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=num_days_in_year)

    # Perform a query to retrieve the data and precipitation scores
    query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    d = dict()
    for t in query: 
        d[t.date] = t.prcp

    return jsonify(d)

   

#  Define what to do when a user hits the /stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Design a query to show how many stations are available in this dataset
    available_stations = session.query(Measurement.station).distinct().all()
    l = list()
    for t in available_stations: 
        l.append(t.station)

    return jsonify(l)

#  Define what to do when a user hits the /tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""

    # Design a query to retrieve the last 12 months of precipitation data
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # max_date
    max_date = max_date[0]

    num_days_in_year = 366

    # Calculate the date 1 year ago from the last data point in the database
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=num_days_in_year)

    results_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()
    d = dict()
    for t in results_tobs: 
        d[t.date] = t.tobs

    return jsonify(d)
    

#  Define what to do when a user hits the /start route
@app.route("/api/v1.0/<start>")
def start(start=None):

    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""

    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    from_start_list=list(from_start)
    return jsonify(from_start_list)
#  Define what to do when a user hits the /end route    
@app.route("/api/v1.0/<start>/<end>")
def _end(start=None, end=None):
    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    between_dates_list=list(between_dates)
    return jsonify(between_dates_list)


if __name__ == "__main__":
    app.run(debug=True)

