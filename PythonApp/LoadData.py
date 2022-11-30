import datetime
from PythonApp import app, db
from PythonApp.models import Account, Flight, AirRoute, AirPort, Schedule, StopOver, User, IDPaper, Papers, Ticket, Seat, Customer
from datetime import datetime
import hashlib


def auth_user(username, passw):
    password = str(hashlib.md5(passw.strip().encode('utf-8')).digest())

    return Account.query.filter(Account.username.__eq__(username.strip()),
                                Account.password.__eq__(password)).first()


def get_user_by_id(user_id):
    return Account.query.get(user_id)


def get_airroute_id_by_name(departure, destination):
    q = AirRoute.query.join(AirPort, AirRoute.departure_id == AirPort.id).filter(
        AirPort.location.contains(departure)).all()
    p = AirRoute.query.join(AirPort, AirRoute.destination_id == AirPort.id).filter(
        AirPort.location.contains(destination)).all()
    if q is not None or q is not None:
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
        query = query.join(Schedule, Flight.id == Schedule.id).filter(Schedule.time >= time)
    return query.all()


def get_flight_by_id(id):
    return Flight.query.get(id)


def get_flight_time_by_id(id):
    q = Schedule.query.get(id)
    return q


def get_stopover_by_airroute_id(id):
    q = StopOver.query.filter(StopOver.airroute_id == id).all()
    return q


def getLocation():
    return AirPort.query.all()



def get_user_by_paper(s):
    query = IDPaper.query.filter(IDPaper.code.__eq__(s)).first()
    if query:
        return query.owner_id
    else:
        return -1


def update_seat(f, quantity, sclass):
    if sclass == 1:
        f.schedule[0].num_o_Fseat = quantity
    else:
        f.schedule[0].num_o_Sseat = quantity
    db.session.add(f)
    db.session.commit()


def get_seat(f_id, sclass):
    f = get_flight_by_id(f_id)
    if sclass == 1:
        seat_num = f.schedule[0].num_o_Fseat
    else:
        seat_num = f.schedule[0].num_o_Fseat
    update_seat(f, seat_num - 1, sclass)
    return f.airplane.seat[seat_num - 1].id


def create_user(Fname, Lname, dob=None, phone=None):
    user = User(Fname=Fname, Lname=Lname, PhoneNum=phone, DOB=dob)
    db.session.add(user)
    db.session.commit()
    return user


def create_id_paper(code, type, u_id):
    p1 = IDPaper(code=code, paper_type=type, owner_id=u_id)
    db.session.add(p1)
    db.session.commit()


def get_user_by_name_and_dob(Fname, Lname, dob):
    query = User.query.filter(User.Fname.__eq__(Fname) and User.Lname.__eq__(Lname) and User.DOB == dob).first()
    if query:
        return query.id
    else:
        return -1


def create_ticket(owner_id, sclass, flight, buyer_id, seller_id):
    seat_id = get_seat(f_id=flight, sclass=sclass)
    ticket = Ticket(seat_class=sclass, owner_id=owner_id, saleman_id=seller_id, buyer_id=buyer_id, flight_id=flight,
                    seat_id=seat_id, sold_time= datetime.now())
    db.session.add(ticket)
    db.session.commit()
    return ticket.id

def create_customer(Fname, Lname, dob=None, phone=None):
    u = create_user(Fname, Lname, dob, phone)
    c = Customer(id=u.id)
    db.session.add(c)
    db.session.commit()
    return c.id


if __name__ == "__main__":
    with app.app_context():
        # print(get_airroute_id_by_name('Đà Nẵng', 'Đà Nẵng'))
        # print(get_flight('Đà Nẵng', 'Đà Nẵng'))
        f = get_flight_by_id(1)
        # f = f.airroute.rule.selling_ticket_hour

        # for i in get_stopover_by_airroute_id(13):
        #     print(i.airport)
        print(create_ticket(7, 1, 1, 7, 2))
