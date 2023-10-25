# Import the dependencies.
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup, either sqlite or postgresql
#################################################
#engine = create_engine("sqlite:///Resources/hawaii.sqlite")
engine = create_engine('postgresql+psycopg2://ns96:java100@localhost/Hawaii')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

# get the date for a year ago from the most recent date 
# entry in the database. This really should be done in the
# functions below, but since data is not being updated let's 
# grab values here
most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
date_year_ago = dt.date.fromisoformat(str(most_recent_date[0])) - dt.timedelta(days=365)
print("Date Year Ago From Latest Date:", date_year_ago)

# get the most active weather station
station_results = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

most_active_station = str(station_results[0][0])
print("Most Active Station:", most_active_station, "\n\n")


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
        f"Available Routes:<br/><br>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/iso_start_date<br>"
        f"/api/v1.0/iso_start_date/iso_end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation for the last year"""

    #Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.prcp != None).\
        filter(Measurement.date >= date_year_ago).\
        order_by(Measurement.date).all()

    # Save the query in a dictionary
    prec_dict = dict()
    
    for result in results:
        prec_dict[str(result[0])] = float(result[1])
    
    # Close the session
    session.close()

    return jsonify(prec_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return the stations in the database"""

    #Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all passengers
    results = session.query(Station.station, Station.name).all()

    # Save the query to a dictionary
    station_dict = dict()
    
    for result in results:
        station_dict[str(result[0])] = str(result[1])
    
    # Close the session
    session.close()

    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def temperature():
    """
    Return the min, max, average temperature for most active station
    for the past year in the database.
    """
    
    #Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.tobs != None).\
        filter(Measurement.date >= date_year_ago).\
        order_by(Measurement.date).all()
    
    
    # Save the query to a dictionary
    tobs_dict = dict()
    
    for result in results:
        tobs_dict[str(result[0])] = float(result[1])
    
    # Close the session
    session.close()
    
    return jsonify(tobs_dict)
                        
@app.route("/api/v1.0/<start>")
def temperature_from(start):
    """
    Return the min, average, and max temperature after the specified date
    """
    
    # convert the iso string to a date object
    start_date = dt.date.fromisoformat(start)
    
    #Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs),\
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).all()
        
    tobs_list = [float(str(results[0][0])), float(str(results[0][1])), float(str(results[0][2]))]
    
    # Close the session
    session.close()
    
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>/<end>")
def temperature_between(start, end):
    """
    Return the min, average, and max temperature between the specified start
    date and end date, inclusive.
    """
    
    # convert the iso strings to date objects
    start_date = dt.date.fromisoformat(start)
    end_date = dt.date.fromisoformat(end)
    
    #Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs),\
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).\
                            filter(Measurement.date <= end_date).all()
        
    tobs_list = [float(str(results[0][0])), float(str(results[0][1])), float(str(results[0][2]))]
    
    # Close the session
    session.close()
    
    return jsonify(tobs_list)
    
# start the application if it running in the console
if __name__ == '__main__':
    app.run(debug=True)