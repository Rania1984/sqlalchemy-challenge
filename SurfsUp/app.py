# Import the dependencies.
import numpy as np
from datetime import datetime, timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    last_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = datetime.strptime(last_date, '%Y-%m-%d') - timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).filter(
    Measurement.date >= one_year_ago.strftime('%Y-%m-%d')
     ).all()

    session.close()

    # Convert results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Station.station).all()
    session.close()

    station_list = [station[0] for station in results]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the most-active station from the Measurement table
    most_active_station = (
        session.query(Measurement.station)
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .first()
    )[0]

    last_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = datetime.strptime(last_date, '%Y-%m-%d') - timedelta(days=365)

    results = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station == most_active_station)
        .filter(Measurement.date >= one_year_ago.strftime('%Y-%m-%d'))
        .all()
    )
    session.close()

    # Convert the results into a list of dictionaries
    temperature_data = [{"date": date, "temperature": tobs} for date, tobs in results]

    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>")
def start_route(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query TMIN, TAVG, TMAX for all dates >= start date
    results = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start)
        .all()
    )

    # Format the results
    stats = {
        "start_date": start,
        "end_date": "latest",
        "TMIN": results[0][0],
        "TAVG": round(results[0][1], 2),
        "TMAX": results[0][2],
    }

    # Return JSON response
    return jsonify(stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end_route(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)


    results = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start)
        .filter(Measurement.date <= end)
        .all()
    )

    # Format the results
    stats = {
        "start_date": start,
        "end_date": end,
        "TMIN": results[0][0],
        "TAVG": round(results[0][1], 2),
        "TMAX": results[0][2],
    }

    # Return JSON response
    return jsonify(stats)


if __name__ == '__main__':
    app.run(debug=True)
