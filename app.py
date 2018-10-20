# Import dependencies
import numpy as np

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
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    precips = session.query(Measurement).filter(Measurement.date >= '2016-08-23').all()
    all_precips = []

    for precip in precips:
        precip_dict = {}
        precip_dict[precip.date] = precip.prcp
        all_precips.append(precip_dict)

    return jsonify(all_precips)


@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station).all()

    stations_list = []
    for station in stations:
        stations_list.append(station.station)
    
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    temperatures = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.date >= '2016-08-23').all()
    temperatures_list = []
    for temperature in temperatures:
        temps_dict = {}
        temps_dict[temperature.date] = temperature.tobs
        temperatures_list.append(temps_dict)
    return jsonify(temperatures_list)

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

@app.route("/api/v1.0/<start>")
def start(start):

    last_date_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date_query[0]

    temps = calc_temps(start, last_date)

    temps_list = []
    temps_list.append({"Start Date": start, "End Date": last_date})
    temps_list.append({"Lowest Temperature": temps[0][0]})
    temps_list.append({"Average Temperature": temps[0][1]})
    temps_list.append({"Highest Temperature": temps[0][2]})
    return jsonify(temps_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    temps = calc_temps(start, end)
    temps_list = []
    temps_list.append({"Start Date": start, "End Date": end})
    temps_list.append({"Lowest Temperature": temps[0][0]})
    temps_list.append({"Average Temperature": temps[0][1]})
    temps_list.append({"Highest Temperature": temps[0][2]})
    return jsonify(temps_list)


# Conditions for running Flask API 
if __name__ == "__main__":
    app.run(debug = True)
