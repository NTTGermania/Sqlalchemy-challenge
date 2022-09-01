from flask import Flask, jsonify
from sqlalchemy import create_engine,func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime
import datetime as dt
import numpy as np
from sqlalchemy import desc


# Create engine
engine = create_engine ("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect a table
Base.prepare(engine, reflect = True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask route
app = Flask(__name__)


@app.route("/")
def home():
    print("server received request for Hawaii weather information page...")
    return ("Welcome to my Hawaii weather information page <br/>"
        f"For any temperature inquiries, please enter any dates between 2010-01-01 and 2017-08-27 in the yyyy-mm-dd format in place of 'start' and/or 'end' <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    prcp_results = session.query(Measurement.date,Measurement.prcp).all()

    prcp_dict = [{result.date : result.prcp} for result in prcp_results]
    

    return jsonify(prcp_dict)
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    station_results = session.query(Station.station, Station.name).all()

    session.close()

    station_ls = list(np.ravel(station_results))

    return jsonify(station_ls)

@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)
    
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date = dt.date(2017,8,23)

    # Calculate the date one year from the last date in data set.
    date_one_year_from_latest_date = latest_date - dt.timedelta(days=365)

    most_active_stations = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(desc(func.count(Measurement.station))).all()
    most_active_station_id = most_active_stations[0][0]
    most_active_station_query = session.query(Measurement.date,Measurement.tobs).filter(Measurement.station == most_active_station_id)\
                            .filter(Measurement.date.between(date_one_year_from_latest_date, latest_date)).all()

    session.close()

    tobs_ls = list(np.ravel(most_active_station_query))
    return jsonify(tobs_ls)     

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end = None):
    session = Session(engine)
    start = datetime.strptime(start,'%Y-%m-%d')

    if (end != None):
        end = datetime.strptime(end,'%Y-%m-%d')
        tavg = session.query(func.avg(Measurement.tobs))\
        .filter(Measurement.date.between(start,end)).all()[0][0]
        tmin = session.query(func.min(Measurement.tobs))\
        .filter(Measurement.date.between(start,end)).all()[0][0]
        tmax = session.query(func.max(Measurement.tobs))\
        .filter(Measurement.date.between(start,end)).all()[0][0]
        output = ( ['Entered start date: ' + str(start),
            'The lowest temperature was ' + str(tmin) + '°F',
            'The average temperature was ' + str(round(tavg,2)) + '°F',
            'The highest temperature was ' + str(tmax) + '°F'])
        return jsonify(output)
    
    
    tavg = session.query(func.avg(Measurement.tobs))\
    .filter(Measurement.date >= start).all()[0][0]
    tmin = session.query(func.min(Measurement.tobs))\
    .filter(Measurement.date >= start).all()[0][0]
    tmax = session.query(func.max(Measurement.tobs))\
    .filter(Measurement.date >= start).all()[0][0]
    
    output = ( ['Entered start date: ' + str(start),
            'Entered end date: ' + str(end),
            'The lowest temperature was ' + str(tmin) + '°F',
            'The average temperature was ' + str(round(tavg,2)) + '°F',
            'The highest temperature was ' + str(tmax) + '°F'])
    return jsonify(output)
   
if __name__ == "__main__":
    app.run(debug=True)