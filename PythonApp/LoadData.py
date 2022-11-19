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
    q = AirRoute.query.join(AirPort, AirRoute.departure_id == AirPort.id and
                                AirRoute.destination_id == AirRoute.id).filter(AirPort.location.contains(destination and departure)).first()
    return q.id


def get_flight(departure, destination, time):
    query = Flight.query.filter()
    if departure and destination:
       query = query.filter(Flight.air_route_id.__eq__(get_airroute_id_by_name(departure, destination)))
    if time:
        query = query.join(Schedule, Flight.id == Schedule.id).filter(Schedule.flight_time >= time)
    return query.all()

if __name__ == "__main__":
    with app.app_context():
        print(get_flight('Hà Nội', 'Hồ Chí Minh', datetime.datetime.now()))