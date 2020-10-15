from flask import Flask,jsonify

import datetime as dt
import sqlalchemy
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func

engine=create_engine('sqlite:///Resources/hawaii.sqlite')

#Reflect existing database into a new model
Base=automap_base()

#Reflect the tables
Base.prepare(engine,reflect=True)

#We can view all of the classes that automap found
Base.classes.keys()
#Save referenes to each table
Measurement=Base.classes.measurement
Station=Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    return(
        f'<h1>Welcome to Climate Analysis!</h1><br/>'
        f'Available Routes:<br/>'
        f'Precipitation: /api/v1.0/precipitation<br/>'
        f'Stations: /api/v1.0/stations<br/>'
        f'Temperature Observations: /api/v1.0/tobs<br/>'
        f'Temperature Stats with a Start - End Date (YYYY-MM_DD): /api/v1.0/temp/<s_input>/<e_input><br/>'

    )
#Convert results to dictionary

@app.route('/api/v1.0/precipitation')
def precp():
    session=Session(engine)
    last_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    results=session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=last_year).all()
    session.close()

    precipitation=[]

    for result in results:
        col={}
        col[result.date]=result.prcp
        precipitation.append(col)
    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():
    session=Session(engine)

    results=session.query(Station.station,Station.name).all()
    session.close()
    all_stations=[]
    for result in results:
        col={}
        col['station']=result.station
        col['name']=result.name
        all_stations.append(col)
    return jsonify(all_stations)

#Query the dates and temperature observations of the most active station for last year
@app.route('/api/v1.0/tobs')
def temp():

    session=Session(engine)
    last_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    results=session.query(Measurement.tobs).\
    filter(Measurement.station=='USC00519281').\
    filter(Measurement.date>=last_year).all()

    session.close()

    temps=list(np.ravel(results))


    return jsonify(temps=temps)

@app.route('/api/v1.0/<s_input>')
@app.route('/api/v1.0/<s_input>/<e_input>')
def begin(s_input=None,e_input=None):
    session=Session(engine)
    if e_input:
        results=session.query(func.min(Measurement.tobs).label('min'),func.max(Measurement.tobs).label('max'),func.avg(Measurement.tobs).label('average'))
        filtered=results.filter(Measurement.date>=s_input).filter(Measurement.date<=e_input).all()
    else:
        results=session.query(func.min(Measurement.tobs).label('min'),func.max(Measurement.tobs).label('max'),func.avg(Measurement.tobs).label('average'))
        filtered=results.filter(Measurement.date>=s_input).all()
    session.close()

    t_stats=[]
    for result in filtered:
        col={}
        col['min']=result.min
        col['max']=result.max
        col['average']=result.average
        t_stats.append(col)
        return jsonify(t_stats)

if __name__=='__main__':
    app.run(debug=True)
