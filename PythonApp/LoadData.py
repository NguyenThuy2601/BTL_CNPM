import datetime
from sqlalchemy import func
from sqlalchemy.sql import extract
from PythonApp import app, db
from PythonApp.models import Account, Flight, AirRoute, AirPort, Schedule, StopOver, User, IDPaper, Papers, Ticket, \
    Seat, Customer, TicketPrice
from datetime import datetime
import hashlib
from sqlalchemy.orm import aliased


def auth_user(username, passw):
    password = str(hashlib.md5(passw.strip().encode('utf-8')).digest())

    return Account.query.filter(Account.username.__eq__(username.strip()),
                                Account.password.__eq__(password)).first()


def get_user_by_id(user_id):
    return Account.query.get(user_id)


def get_airroute_id_by_name(departure, destination):
    dep = aliased(AirPort)
    des = aliased(AirPort)
    query = AirRoute.query.join(dep, dep.id == AirRoute.departure_id) \
        .join(des, des.id == AirRoute.destination_id) \
        .filter(dep.location.contains(departure)) \
        .filter(des.location.contains(destination)).first()
    if query:
        return query.id
    else:
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


def get_customer_by_paper(s):
    query = User.query.join(Customer, Customer.id == User.id).join(IDPaper, User.id == IDPaper.owner_id).filter(
        IDPaper.code.__eq__(s)).first()
    if query:
        return query.id
    else:
        return None

def get_remaining_seat(f_id, sclass):
    num_o_ticket = Ticket.query.filter(Ticket.flight_id == f_id).filter(Ticket.seat_class == sclass).count()
    flight = get_flight_by_id(id=f_id)
    if sclass == 1:
        num_o_seat = flight.schedule[0].num_o_Fseat
    else:
        num_o_seat = flight.schedule[0].num_o_Sseat
    return num_o_seat - num_o_ticket

def update_seat(f, quantity, sclass):
    if sclass == 1:
        f.schedule[0].num_o_Fseat = quantity
    else:
        f.schedule[0].num_o_Sseat = quantity
    db.session.add(f)
    db.session.commit()


def get_seat(f_id, sclass):
    f = get_flight_by_id(f_id)
    seat_num = get_remaining_seat(f_id=f_id, sclass=sclass)
    if sclass == 1:
        seat_num = get_remaining_seat(f_id=f_id, sclass=sclass)
    else:
        seat_num = f.schedule[0].num_o_Sseat
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


def update_phone_number(sdt, id):
    u = User.query.get(id)
    if u.PhoneNum.__eq__(sdt):
        return True
    else:
        u.phoneNum = sdt
        db.session.add(u)
        db.session.commit()
        return u.phoneNum


def get_customer_by_name_and_dob(Fname, Lname, dob):
    query = User.query.join(Customer, Customer.id == User.id) \
        .filter(User.Lname.contains(Lname)) \
        .filter(User.Fname.contains(Fname)) \
        .filter(User.DOB == dob).first()
    if query:
        return query.id
    else:
        return None


def create_ticket(owner_id, sclass, flight_id, buyer_id, seller_id):
    seat_id = get_remaining_seat(f_id=flight_id, sclass=sclass)
    ticket = Ticket(seat_class=sclass, owner_id=owner_id, saleman_id=seller_id, buyer_id=buyer_id, flight_id=flight_id,
                    seat_id=seat_id, sold_time=datetime.now())
    db.session.add(ticket)
    db.session.commit()
    return ticket.id


def get_ticket(id=None):
    query = Ticket.query.filter()
    if id:
        query = query.filter(Ticket.id == id)
    return query.all()


def create_customer(Fname, Lname, dob=None, phone=None):
    u = create_user(Fname, Lname, dob, phone)
    c = Customer(id=u.id)
    db.session.add(c)
    db.session.commit()
    return c.id


def ticket_first_class_stat(month=None, year=None):
    query = db.session.query(AirRoute.id, func.count(Ticket.id), func.count(Ticket.id) * TicketPrice.Fprice) \
        .join(Flight, Flight.air_route_id == AirRoute.id, isouter=True) \
        .join(TicketPrice, TicketPrice.id == Flight.price_id, isouter=True) \
        .join(Ticket, Ticket.flight_id == Flight.id, isouter=True) \
        .filter(Ticket.seat_class == 1) \
        .group_by(AirRoute.id)

    if month:
        query = query.filter(func.month(Ticket.sold_time) == month)

    if year:
        query = query.filter(func.year(Ticket.sold_time) == year)

    return query.all()


def ticket_second_class_stat(month=None, year=None):
    query = db.session.query(AirRoute.id, func.count(Ticket.id), (func.count(Ticket.id) * TicketPrice.Sprice)) \
        .join(Flight, Flight.air_route_id == AirRoute.id, isouter=True) \
        .join(TicketPrice, TicketPrice.id == Flight.price_id, isouter=True) \
        .join(Ticket, Ticket.flight_id == Flight.id, isouter=True) \
        .filter(Ticket.seat_class == 2) \
        .group_by(AirRoute.id)

    if month:
        query = query.filter(func.month(Ticket.sold_time) == month)
    if year:
        query = query.filter(func.year(Ticket.sold_time) == year)

    return query.all()


def ticket_amount_stat(month=None, year=None):
    query = db.session.query(AirRoute.id, AirRoute.name, func.count(Flight.id), func.count(Ticket.id)) \
        .join(Flight, Flight.air_route_id == AirRoute.id, isouter=True) \
        .join(Ticket, Ticket.flight_id == Flight.id, isouter=True) \
        .group_by(AirRoute.id)

    if month:
        query = query.filter(func.month(Ticket.sold_time) == month)
    if year:
        query = query.filter(func.year(Ticket.sold_time) == year)

    return query.all()


def flight_stat_by_air_route(month=None, year=None):
    query = db.session.query(AirRoute.id, AirRoute.name, func.count(Flight.id)) \
        .join(Flight, AirRoute.id == Flight.air_route_id, isouter=True) \
        .join(Schedule, Flight.id == Schedule.id, isouter=True) \
        .group_by(AirRoute.id)
    if month:
        query = query.filter(func.month(Schedule.time) == month)
    if year:
        query = query.filter(func.year(Schedule.time) == year)

    return query.all()


def convert_to_list_of_list(tuple):
    for i in range(0, len(tuple)):
        tuple[i] = list(tuple[i])
    return tuple


def convert_to_list_of_tuple(list):
    for i in range(0, len(list)):
        list[i] = tuple(list[i])
    return list


def asign_to_temp(list):
    temp = []
    for i in range(0, len(list)):
        temp.append(list[i])
    return temp


def combine_ticket_income_stats(Fclass_stat, Sclass_stat):
    total = asign_to_temp(convert_to_list_of_list(Fclass_stat))

    for i in range(0, len(total)):
        for j in range(0, len(Sclass_stat)):
            if (Sclass_stat[j][0] == total[i][0]):
                total[i][1] += Sclass_stat[j][1]
                total[i][2] += Sclass_stat[j][2]

    flag = True
    temp = []
    for j in range(0, len(Sclass_stat)):
        flag = True
        index = 0
        for i in range(0, len(total)):
            if (Sclass_stat[j][0] != total[i][0]):
                flag = False
                index = j
            else:
                flag = True
                break
        if not flag:
            temp.append(list(Sclass_stat[index]))

    for i in range(0, len(temp)):
        total.append(temp[i])

    return total


def add_ticket_stat(ticket_income_total, flight_stats):
    total = asign_to_temp(convert_to_list_of_list(flight_stats))

    for i in range(0, len(total)):
        for j in range(0, 2):
            total[i].append(0)

    for i in range(0, len(total)):
        for j in range(0, len(ticket_income_total)):
            if (total[i][0] == ticket_income_total[j][0]):
                total[i][3] = ticket_income_total[j][1]
                total[i][4] = ticket_income_total[j][2]
    return total


def get_total_income(total_stat):
    sum = 0
    for i in range(0, len(total_stat)):
        sum += total_stat[i][4]

    if sum == 0:
        sum = 1
    return sum


# def update_remaining_seat(flight_id, sclass):
#     flight = Flight.query.get(flight_id)
#     if sclass == 1:
#         flight.schedule[0].num_o_Fseat += 1
#     else:
#         flight.schedule[0].num_o_Sseat += 1
#     db.session.add(flight)
#     db.session.commit()
#     return True


def updateTicket(flight_id, ticket_id):
    ticket = Ticket.query.get(ticket_id)
    ticket.flight_id = flight_id
    ticket.seat_id = get_remaining_seat(f_id=flight_id, sclass=ticket.seat_class)
    db.session.add(ticket)
    db.session.commit()
    return ticket.id


def get_ticket_by_id(id):
    return Ticket.query.get(id)



if __name__ == "__main__":
    with app.app_context():
        # print(get_airroute_id_by_name('Hà Nội', 'Hà Nội'))
        # print(get_flight('Đà Nẵng', 'Đà Nẵng'))
        f = get_flight_by_id(1)
        # f = f.airroute.rule.selling_ticket_hour

        # for i in get_stopover_by_airroute_id(13):
        #     print(i.airport)
        # u = get_customer_by_paper('101010')
        # print(u)
        # func.sum(Ticket.query.filter(Ticket.seat_class == 1).count() * TicketPrice.Fprice)

        # print(update_phone_number('09090909',3))
        # s = flight_stat(month=12)
        # t = flight_stat_by_air_route(month=10)
        # print(t)
        # a = ticket_first_class_stat()
        # b = ticket_second_class_stat()
        # print('before a: ')
        # print(a)
        # print('before b:')
        # print(b)
        # for i in range(0, len(a)):
        #     a[i] = list(a[i])
        #     for j in range(0, len(b)):
        #         b[j] = list(b[j])
        #         if (b[j][0] == a[i][0]):
        #             a[i][1] += b[j][1]
        #         b[j] = tuple(b[j])
        #     a[i] = tuple(a[i])
        # print('after a: ')
        # print(a)
        # x = convert_to_list_of_tuple(
        #     combine_ticket_income_stats(Fclass_stat=ticket_first_class_stat(), Sclass_stat=ticket_second_class_stat()))
        # y = convert_to_list_of_tuple(
        #     combine_flight_stats_with_ticket(flight_stat=flight_stat_by_air_route(), ticket_stat=ticket_amount_stat()))
        # print("flight: ")
        # print(flight_stat_by_air_route())
        # print("overall ticket: ")
        # print(ticket_amount_stat())
        # print("final ticket: ")
        # print(y)
        # z = flight_stat_by_air_route()
        # print('test')
        # print(add_income_stat(income_ticket_stat=x, flight_stats_overall=y))
        #
        # month = 10
        # year = 2023
        #
        # Fclass_ticket_stat = ticket_first_class_stat(month=month, year=year)
        # Sclass_ticket_stat = ticket_second_class_stat(month=month, year=year)
        # flight_stat = flight_stat_by_air_route(month=month, year=year)
        # ticket_amount_stat = ticket_amount_stat(month=month, year=year)
        #
        # ticket_income_total = convert_to_list_of_tuple(
        #     combine_ticket_income_stats(Fclass_stat=Fclass_ticket_stat, Sclass_stat=Sclass_ticket_stat))
        #
        # total_stat = convert_to_list_of_tuple(
        #     add_ticket_stat(flight_stats=flight_stat, ticket_income_total=ticket_income_total))
        #
        # print(total_stat)
        # print(Flight.query.get(1).schedule[0].num_o_Fseat)
        # print(update_remaining_seat(1, 1))

        # print(create_ticket(owner_id=4, sclass=1, flight=2, buyer_id=4, seller_id=2))
        print(get_remaining_seat(f_id=10, sclass=2))
