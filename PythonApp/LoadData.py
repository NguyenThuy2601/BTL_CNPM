import datetime
from PythonApp import app, db
from PythonApp.models import Account, Flight, AirRoute, AirPort, Schedule
import hashlib


def auth_user(username, passw):
    password = str(hashlib.md5(passw.strip().encode('utf-8')).digest())

    return Account.query.filter(Account.username.__eq__(username.strip()),
                             Account.password.__eq__(password)).first()

def get_user_by_id(user_id):
    return Account.query.get(user_id)


def get_airroute_id_by_name(departure, destination):
    q = AirRoute.query.join(AirPort, AirRoute.departure_id == AirPort.id).filter(AirPort.location.contains(departure)).all()
    p = AirRoute.query.join(AirPort, AirRoute.destination_id == AirPort.id).filter(AirPort.location.contains(destination)).all()
    if q is not None or q is not  None:
        for des in p:
            for dep in q:
                if des.id == dep.id:
                    return des.id
        return False


def get_flight(departure=None, destination=None, time=0):
    query = Flight.query.filter()
    if departure and destination:
        id = get_airroute_id_by_name(departure, destination)
        query = query.filter(Flight.air_route_id.__eq__(id))
    if time:
        query = query.join(Schedule, Flight.id == Schedule.id).filter(Schedule.flight_time >= time)
    return query.all()

def getLocation():
    return AirPort.query.all()

if __name__ == "__main__":
    with app.app_context():

            print(get_airroute_id_by_name('Đà Nẵng', 'Đà Nẵng'))
            print(get_flight('Đà Nẵng', 'Đà Nẵng'))