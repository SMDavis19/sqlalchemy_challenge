import numpy as np
import datetime as dt 
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

# Save reference to the table
Station = Base.classes.station
measurement = Base.classes.measurement

#Creating an app
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
#home 
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
	# Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query all of measurements 
    results = session.query(measurement).all()
    session.close()
    
    # Creating a dictionary for prcp data
    prcp_dict = []
	
    for result in results:
        prcp = {}
        prcp["date"] = result.date
        prcp["prcp"] = result.prcp
        prcp_dict.append(prcp)

    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
	# Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query all of stations  
    results = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    station = list(np.ravel(results))
    return jsonify(station)

@app.route("/api/v1.0/tobs")
def tobs():
	# Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Last date in data minus a year 
    year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    
    # Query all of stations  that fit the above parameters 
    results = session.query(measurement.tobs).filter(measurement.date > year).all()
    session.close()

    # Convert list of tuples into normal list
    temp = list(np.ravel(results))
    return jsonify(results)

@app.route("/api/v1.0/start_date")
def start():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Using stripe time method to parse the date format 
    start_date = dt.datetime.strptime(start,"%Y-%m-%d")

    # Searching for and returning given temp values based of start date
    temp = session.query(func.min(measurement.tobs), # Minium temp 
                         func.max(measurement.tobs),  # Maximum temp & Avgerage temp below....
                         func.avg(measurement.tobs))
    # Filtering above temps... based on date
    filter(measurement.date >= start_date).all()    
    session.close()

    # Convert list of tuples into normal list
    data = list(np.ravel(temp))

    return jsonify(data)

@app.route("/api/v1.0/start_date/end_date")
def start_end():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Using stripe time method to parse the date format 
    start_date = dt.datetime.strptime(start,"%Y-%m-%d")
    end_date = dt.datetime.strptime(end,"%Y-%m-%d")

    # Searching for and returning given temp values based of start date
    
    temp = session.query(func.min(measurement.tobs), # Minium temp 
                         func.max(measurement.tobs),  # Maximum temp & Avgerage temp below....
                         func.avg(measurement.tobs))
    # Filtering above temps... based on date
    filter(measurement.date(start_date, end_date)).all()    
    session.close()

    # Convert list of tuples into normal list
    data = list(np.ravel(temp))

    return jsonify(data)



if __name__ == '__main__':
    app.run(debug=True)      
