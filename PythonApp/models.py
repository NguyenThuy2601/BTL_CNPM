import datetime
import hashlib

from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, Enum, DATETIME, DATE
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from PythonApp import app, db
from enum import Enum as E
from flask_login import UserMixin


class UserRole(E):
    USER = 1
    EMPLOYEE = 2
    ADMIN = 3


class Papers(E):
    PASSPORT = 1
    CCCD = 2

    @staticmethod
    def from_str(label):

        if label == 1:
            return Papers.PASSPORT
        else:
            return Papers.CCCD


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    Fname = Column(String(50))
    Lname = Column(String(50))
    DOB = Column(DATE)
    PhoneNum = Column(String(10))

    owner = relationship('IDPaper', backref='user', lazy=True)
    customer = relationship('Customer', backref='user', lazy=True)
    employee = relationship('Employee', backref='user', lazy=True)


class Customer(db.Model):
    __tablename__ = 'customer'
    id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), primary_key=True)

    # buyer = relationship('Ticket', backref='Customer', lazy=True)
    # saleman = relationship('Ticket', backref='Employee', lazy=True)

    def __str__(self):
        return self.Fname


class Employee(db.Model):
    __tablename__ = 'employee'
    id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), primary_key=True)
    position = Column(String(30), nullable=True)
    incharge_ticket = relationship('Ticket', backref='Employee', lazy=True)

    def __str__(self):
        return self.Fname


class Account(BaseModel, UserMixin):
    __tablename__ = 'account'
    id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), primary_key=True)
    email = Column(String(100), nullable=False, unique=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.USER)

    def __str__(self):
        return self.username


class Ticket(BaseModel):
    __tablename__ = 'ticket'
    seat_class = Column(Integer, default=2)
    owner_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
    buyer_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
    saleman_id = Column(Integer, ForeignKey(Employee.id), nullable=True)
    flight_id = Column(Integer, ForeignKey('flight.id', ondelete='CASCADE'), nullable=False)
    seat_id = Column(Integer, ForeignKey('seat.id'), nullable=False)
    sold_time = Column(DATETIME, nullable=False)

    buyer = relationship('Customer', foreign_keys=[buyer_id])
    owner = relationship('Customer', foreign_keys=[owner_id])

    def __str__(self):
        return self.id


class IDPaper(BaseModel):
    __tablename__ = 'idpaper'
    code = Column(String(20), nullable=False)
    paper_type = Column(Enum(Papers), nullable=False)
    owner_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False)

    def __str__(self):
        return self.code


class Rule(BaseModel):
    __tablename__ = 'rule'
    max_stopover = Column(Integer)
    min_stoptime = Column(Float)
    max_stoptime = Column(Float)
    flying_hour = Column(Float)
    selling_ticket_hour = Column(Float)
    online_selling_ticket_hour = Column(Float)
    air_route = relationship('AirRoute', backref='rule', lazy=True)

    def __str__(self):
        return str(self.id)


class AirPort(BaseModel):
    __tablename__ = 'airport'
    name = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)
    stop_over = relationship('StopOver', backref='airport')

    def __str__(self):
        return self.location


class AirRoute(BaseModel):
    __tablename__ = 'airroute'
    name = Column(String(50), nullable=False)
    departure_id = Column(Integer, ForeignKey(AirPort.id), nullable=False)
    destination_id = Column(Integer, ForeignKey(AirPort.id), nullable=False)
    rule_id = Column(Integer, ForeignKey(Rule.id), nullable=False)

    departure = relationship('AirPort', foreign_keys=[departure_id], backref='departure')
    destination = relationship('AirPort', foreign_keys=[destination_id], backref='destination')
    stop_over = relationship('StopOver', backref='airroute')
    flight = relationship('Flight', backref='airroute', lazy=True)

    def __str__(self):
        return self.name


class Flight(BaseModel):
    __tablename__ = 'flight'
    air_route_id = Column(Integer, ForeignKey(AirRoute.id, ondelete='CASCADE'), nullable=False)
    airplane_id = Column(Integer, ForeignKey('airplane.id'), nullable=False)
    price_id = Column(Integer, ForeignKey('ticketprice.id'), nullable=False)

    schedule = relationship('Schedule', backref='flight', lazy='subquery')
    ticket = relationship('Ticket', backref='flight', lazy=True)

    def __str__(self):
        return str(self.id)


class StopOver(BaseModel):
    __tablename__ = 'stopover'
    airport_id = Column(ForeignKey(AirPort.id))
    airroute_id = Column(ForeignKey(AirRoute.id))
    stop_minute = Column(Float, nullable=False)
    note = Column(String(50))

    def __str__(self):
        return str(self.id)


class Schedule(BaseModel):
    __tablename__ = 'schedule'
    id = Column(Integer, ForeignKey(Flight.id), primary_key=True)
    time = Column(DATETIME, nullable=False)
    num_o_Fseat = Column(Integer, nullable=False)
    num_o_Sseat = Column(Integer, nullable=False)

    def __str__(self):
        return self.time


class Type(BaseModel):
    __tablename__ = 'type'
    model = Column(String(50))
    generation = Column(String(50))
    num_o_seat = Column(Integer, nullable=False)

    airplane = relationship('Airplane', backref='type', lazy=True)

    def __str__(self):
        return self.model


class Airplane(BaseModel):
    __tablename__ = 'airplane'
    load = Column(Float)
    name = Column(String(50))
    brand = Column(String(50))

    flight = relationship(Flight, backref='airplane', lazy=True)
    type_id = Column(Integer, ForeignKey(Type.id))

    seat = relationship('Seat', backref='airplane', lazy=True)

    def __str__(self):
        return self.name


class Seat(BaseModel):
    __tablename__ = 'seat'
    seatName = Column(String(50), nullable=False)
    Sclass = Column(Integer, default=2)

    airplane_id = Column(Integer, ForeignKey(Airplane.id), nullable=False)

    ticket = relationship('Ticket', backref='seat', lazy=True)

    def __str__(self):
        return self.seatName


class TicketPrice(BaseModel):
    __tablename__ = 'ticketprice'
    Fprice = Column(Float, nullable=False)
    Sprice = Column(Float, nullable=False)

    flight = relationship(Flight, backref='ticketprice', lazy=True)

    def __str__(self):
        return self.price


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()

        # tao nv

        u1 = User(Fname='Thuy', Lname='Cao Nguyen', DOB=datetime(2002, 1, 26), PhoneNum='0303030303')
        u2 = User(Fname='Tai', Lname='Ngo Thi Kim', DOB=datetime(2002, 3, 18), PhoneNum='0707077007')
        db.session.add_all([u1, u2])
        db.session.commit()
        e1 = Employee(id=u1.id, position='Quản trị')
        e2 = Employee(id=u2.id, position='Nhân viên')
        db.session.add_all([e1, e2])
        db.session.commit()
        cccd_u1 = IDPaper(code='123', paper_type=Papers.CCCD, owner_id=u1.id)
        cccd_u2 = IDPaper(code='456', paper_type=Papers.CCCD, owner_id=u2.id)
        db.session.add_all([cccd_u1, cccd_u2])
        db.session.commit()
        passw = str(hashlib.md5('1'.encode('utf-8')).digest())
        ac_u1 = Account(id=u1.id, email='2051052135thuy@ou.edu.vn', username='Thuy',
                        password=passw, user_role=UserRole.ADMIN)
        ac_u2 = Account(id=u2.id, email='2051052040tai@ou.edu.vn', username='Tai', password=passw,
                        user_role=UserRole.EMPLOYEE)
        db.session.add_all([ac_u1, ac_u2])
        db.session.commit()

        # Tao khach hang

        u3 = User(Fname='Huy', Lname='Doan Gia', DOB=datetime(2002, 1, 3), PhoneNum='0909090909')
        u4 = User(Fname='Nhi', Lname='Nguyen Đang Tuyet', DOB=datetime(2002, 11, 23), PhoneNum='0101010101')
        u5 = User(Fname='Tien', Lname='Pham Gia', DOB=datetime(1999, 12, 7), PhoneNum='0202020202')
        u6 = User(Fname='Toi', Lname='Le Quang', DOB=datetime(2002, 9, 25), PhoneNum='1234566789')
        u7 = User(Fname='Ly', Lname='Dinh Pham Yen', DOB=datetime(2002, 7, 15), PhoneNum='9999999999')
        u8 = User(Fname='Linh', Lname='Lung thi', DOB=datetime(2008, 12, 7), PhoneNum='0202020202')
        u9 = User(Fname='Thanh', Lname='Ngo Minh', DOB=datetime(2002, 1, 13), PhoneNum='1313131313')
        u10 = User(Fname='Hieu', Lname='Tran Duc', DOB=datetime(2002, 1, 2), PhoneNum='1212121212')
        u11 = User(Fname='A', Lname='Nguyen Van', DOB=datetime(1989, 6, 8), PhoneNum='6868686868')
        u12 = User(Fname='B', Lname='Nguyen Thi', DOB=datetime(2001, 3, 4), PhoneNum='3434343434')
        db.session.add_all([u3, u4, u5, u6, u7, u8, u9, u10, u11,u12])
        db.session.commit()

        c1 = Customer(id=u3.id)
        c2 = Customer(id=u4.id)
        c3 = Customer(id=u5.id)
        c4 = Customer(id=u6.id)
        c5 = Customer(id=u7.id)
        c6 = Customer(id=u8.id)
        c7 = Customer(id=u9.id)
        c8 = Customer(id=u10.id)
        c9 = Customer(id=u11.id)
        c10 = Customer(id=u12.id)
        db.session.add_all([c1, c2, c3, c4, c5,
                            c6, c9, c10])
        db.session.commit()
        cccd_u3 = IDPaper(code='987', paper_type=Papers.CCCD, owner_id=u3.id)
        pp_u3 = IDPaper(code='919191', paper_type=Papers.PASSPORT, owner_id=u3.id)
        cccd_u4 = IDPaper(code='101010', paper_type=Papers.CCCD, owner_id=u4.id)
        cccd_u5 = IDPaper(code='78787', paper_type=Papers.CCCD, owner_id=u5.id)
        pp_u6 = IDPaper(code='919191', paper_type=Papers.PASSPORT, owner_id=u6.id)
        cccd_u7 = IDPaper(code='54444', paper_type=Papers.CCCD, owner_id=u7.id)
        cccd_u8 = IDPaper(code='929292', paper_type=Papers.CCCD, owner_id=u8.id)
        cccd_u9 = IDPaper(code='2222', paper_type=Papers.CCCD, owner_id=u9.id)
        cccd_u10 = IDPaper(code='989898', paper_type=Papers.CCCD, owner_id=u10.id)
        cccd_u11 = IDPaper(code='939393', paper_type=Papers.CCCD, owner_id=u11.id)
        cccd_u12 = IDPaper(code='949494', paper_type=Papers.CCCD, owner_id=u12.id)
        db.session.add_all([cccd_u3, cccd_u4, cccd_u5, pp_u3, pp_u6,
                            cccd_u7, cccd_u8, cccd_u9, cccd_u10, cccd_u11, cccd_u12])
        db.session.commit()
        passw = str(hashlib.md5('1'.encode('utf-8')).digest())
        ac_u3 = Account(id=u3.id, email='2051052054huy@ou.edu.vn', username='Huy', password=passw)
        ac_u4 = Account(id=u4.id, email='2051050318nhi@ou.edu.vn', username='Nhi', password=passw)
        ac_u5 = Account(id=u5.id, email='2051052136tien@ou.edu.vn', username='Tien', password=passw)
        db.session.add_all([ac_u3, ac_u4, ac_u5])
        db.session.commit()

        # Tao quy dinh

        r1 = Rule(max_stopover=2, min_stoptime=20, max_stoptime=30, flying_hour=0.5, selling_ticket_hour=4,
                  online_selling_ticket_hour=12)
        db.session.add(r1)
        db.session.commit()

        # Tao san bay

        ap1 = AirPort(name='Nội Bài', location='Hà Nội, Việt Nam')
        ap2 = AirPort(name='Tân Sơn Nhất', location='Hồ Chí Minh, Việt Nam')
        ap3 = AirPort(name='Cảng hàng không quốc tế Đà Nẵng', location='Đà Nẵng, Việt Nam')
        ap4 = AirPort(name='Haneda', location='Tokyo, Nhật Bản')
        ap5 = AirPort(name='Incheon', location='Seoul, Hàn Quốc')
        ap6 = AirPort(name='Newark Liberty', location='New York, Mỹ')
        ap7 = AirPort(name='Cam Ranh', location='Khánh Hòa, Việt Nam')
        ap8 = AirPort(name='Phú Quốc', location='Phú Quốc, Việt Nam')
        ap9 = AirPort(name='Melbourn, Úc', location='Melbourne, Úc')
        ap10 = AirPort(name='Paris Charles de Gaulle', location='Paris, Pháp')
        db.session.add_all([ap1, ap2, ap3, ap4, ap5,
                            ap6, ap7, ap8, ap9, ap10])
        db.session.commit()

        # Tao tuyen bay

        ar1 = AirRoute(name='Hà Nội - HCM', departure_id=ap1.id, destination_id=ap2.id, rule_id=r1.id)
        ar2 = AirRoute(name='HCM - Đà Nẵng', departure_id=ap2.id, destination_id=ap3.id, rule_id=r1.id)
        ar3 = AirRoute(name='HCM - Hàn Quốc', departure_id=ap2.id, destination_id=ap5.id, rule_id=r1.id)
        ar4 = AirRoute(name='HCM - Pháp', departure_id=ap2.id, destination_id=ap10.id, rule_id=r1.id)
        ar5 = AirRoute(name='Hà Nội - Khánh Hòa', departure_id=ap1.id, destination_id=ap7.id, rule_id=r1.id)
        ar6 = AirRoute(name='Hà Nội - Hàn Quốc', departure_id=ap1.id, destination_id=ap5.id, rule_id=r1.id)
        ar7 = AirRoute(name='Đà Nẵng - Hồ Chí Minh', departure_id=ap3.id, destination_id=ap2.id, rule_id=r1.id)
        ar8 = AirRoute(name='HCM - Phú Quốc', departure_id=ap2.id, destination_id=ap8.id, rule_id=r1.id)
        ar9 = AirRoute(name='Đà Nẵng - Phú Quốc', departure_id=ap3.id, destination_id=ap8.id, rule_id=r1.id)
        ar10 = AirRoute(name='Phú Quốc - Hồ Chí Minh', departure_id=ap8.id, destination_id=ap2.id, rule_id=r1.id)
        ar11 = AirRoute(name='Paris - Hồ Chí Minh', departure_id=ap10.id, destination_id=ap2.id, rule_id=r1.id)
        ar12 = AirRoute(name='Melbourn - Hồ Chí Minh', departure_id=ap9.id, destination_id=ap2.id, rule_id=r1.id)
        ar13 = AirRoute(name='HCM - New York', departure_id=ap2.id, destination_id=ap6.id, rule_id=r1.id)
        db.session.add_all([ar1, ar2, ar3, ar4, ar5, ar6,
                            ar7, ar8, ar9, ar10, ar11, ar12, ar13])
        db.session.commit()

        # Tao trung gian
        stopover1 = StopOver(airport_id=ap5.id, airroute_id=ar13.id, stop_minute=22)
        stopover2 = StopOver(airport_id=ap4.id, airroute_id=ar13.id, stop_minute=24)
        stopover3 = StopOver(airport_id=ap4.id, airroute_id=ar10.id, stop_minute=20)

        db.session.add_all([stopover1, stopover2, stopover3])
        db.session.commit()

        # Tao bang gia ve
        pt1 = TicketPrice(Sprice=15000000, Fprice=25000000)
        pt2 = TicketPrice(Sprice=5000000, Fprice=6000000)
        pt3 = TicketPrice(Sprice=1000000, Fprice=2000000)
        pt4 = TicketPrice(Sprice=500000, Fprice=700000)

        db.session.add_all([pt1, pt2, pt3, pt4])
        db.session.commit()

        # Tao loai may bay

        t1 = Type(model='AirBus', generation='A370', num_o_seat=100)
        t2 = Type(model='Boeing', generation='A52', num_o_seat=150)

        db.session.add_all([t1, t2])
        db.session.commit()

        # Tao may bay

        plane1 = Airplane(load=7, name='abc', brand='VN airline', type_id=t1.id)
        plane2 = Airplane(load=5, name='awe', brand='France airline', type_id=t1.id)
        plane3 = Airplane(load=6, name='oue', brand='VietJet', type_id=t1.id)
        plane4 = Airplane(load=4, name='mim', brand='Bamboo', type_id=t1.id)
        plane5 = Airplane(load=8, name='mi0', brand='Korea Airline', type_id=t1.id)
        plane6 = Airplane(load=4, name='pop', brand='VN airline', type_id=t1.id)
        plane7 = Airplane(load=8, name='nnd', brand='Korea Airline', type_id=t2.id)
        plane8 = Airplane(load=4, name='pii', brand='Bamboo', type_id=t2.id)
        plane9 = Airplane(load=8, name='nqq', brand='VietJet', type_id=t2.id)
        plane10 = Airplane(load=4, name='aaa', brand='VN airline', type_id=t2.id)
        plane11 = Airplane(load=8, name='ll', brand='VN airline', type_id=t2.id)
        plane12 = Airplane(load=4, name='pz', brand='VN airline', type_id=t2.id)

        db.session.add_all([plane1, plane2, plane3, plane4, plane5, plane6,
                            plane7, plane8, plane9, plane10, plane11, plane12])
        db.session.commit()

        # Tao chuyen bay

        # ar2
        f1 = Flight(air_route_id=ar2.id, airplane_id=plane1.id, price_id=pt1.id)
        f2 = Flight(air_route_id=ar2.id, airplane_id=plane1.id, price_id=pt2.id)
        f3 = Flight(air_route_id=ar2.id, airplane_id=plane1.id, price_id=pt4.id)
        # ar7
        f4 = Flight(air_route_id=ar7.id, airplane_id=plane1.id, price_id=pt1.id)
        f5 = Flight(air_route_id=ar7.id, airplane_id=plane2.id, price_id=pt2.id)
        f6 = Flight(air_route_id=ar7.id, airplane_id=plane4.id, price_id=pt4.id)
        f7 = Flight(air_route_id=ar7.id, airplane_id=plane2.id, price_id=pt1.id)
        f8 = Flight(air_route_id=ar7.id, airplane_id=plane3.id, price_id=pt3.id)
        # ar1
        f9 = Flight(air_route_id=ar1.id, airplane_id=plane4.id, price_id=pt3.id)
        # ar13
        f10 = Flight(air_route_id=ar13.id, airplane_id=plane4.id, price_id=pt1.id)
        f11 = Flight(air_route_id=ar13.id, airplane_id=plane1.id, price_id=pt2.id)
        # ar11
        f12 = Flight(air_route_id=ar11.id, airplane_id=plane3.id, price_id=pt4.id)

        db.session.add_all([f1, f2, f3, f4, f5, f6,
                            f7, f8, f9, f10, f11, f12])
        db.session.commit()

        # Tao lich bay

        sc1 = Schedule(id=f1.id, time=datetime(2023, 10, 11, 9, 10, 0, 0),
                       num_o_Fseat=10, num_o_Sseat=40)
        sc2 = Schedule(id=f2.id, time=datetime(2023, 1, 11, 22, 10, 0, 0),
                       num_o_Fseat=14, num_o_Sseat=80)
        sc3 = Schedule(id=f3.id, time=datetime(2022, 12, 30, 8, 10, 0, 0),
                       num_o_Fseat=20, num_o_Sseat=70)
        sc4 = Schedule(id=f4.id, time=datetime(2023, 3, 11, 12, 0, 0, 0),
                       num_o_Fseat=40, num_o_Sseat=30)
        sc5 = Schedule(id=f5.id, time=datetime(2023, 10, 11, 8, 10, 0, 0),
                       num_o_Fseat=10, num_o_Sseat=60)
        sc6 = Schedule(id=f6.id, time=datetime(2023, 3, 11, 10, 10, 0, 0),
                       num_o_Fseat=30, num_o_Sseat=50)
        sc7 = Schedule(id=f7.id, time=datetime(2023, 4, 14, 4, 10, 0, 0),
                       num_o_Fseat=40, num_o_Sseat=45)
        sc8 = Schedule(id=f8.id, time=datetime(2023, 1, 1, 0, 10, 0, 0),
                       num_o_Fseat=20, num_o_Sseat=60)
        sc9 = Schedule(id=f9.id, time=datetime(2023, 9, 9, 5, 10, 0, 0),
                       num_o_Fseat=10, num_o_Sseat=70)
        sc10 = Schedule(id=f10.id, time=datetime(2023, 6, 7, 21, 10, 0, 0),
                        num_o_Fseat=10, num_o_Sseat=40)
        sc11 = Schedule(id=f11.id, time=datetime(2023, 5, 11, 18, 1, 0, 0),
                        num_o_Fseat=20, num_o_Sseat=50)
        sc12 = Schedule(id=f12.id, time=datetime(2023, 3, 3, 23, 10, 0, 0),
                        num_o_Fseat=10, num_o_Sseat=90)

        db.session.add_all([sc1, sc2, sc3, sc4, sc5, sc6,
                            sc7, sc8, sc9, sc10, sc11, sc12])
        db.session.commit()

        # Tao ghe

        # Tao cho 6 may bay dau ghe hang 1
        for i in range(1, 7):
            for j in range(1, 51):
                seat = Seat(seatName=str(j), Sclass=1, airplane_id=i)
                db.session.add(seat)
                db.session.commit()

            # Tao cho 6 may bay dau ghe hang 2
        for i in range(1, 7):
            for j in range(51, 101):
                seat = Seat(seatName=str(j), Sclass=2, airplane_id=i)
                db.session.add(seat)
                db.session.commit()

            # Tao cho 6 chuyen sau ghe hang 1
        for i in range(7, 13):
            for j in range(1, 51):
                seat = Seat(seatName=str(j), Sclass=1, airplane_id=i)
                db.session.add(seat)
                db.session.commit()

            # Tao cho 6 chuyen sau ghe hang 2
        for i in range(7, 13):
            for j in range(51, 151):
                seat = Seat(seatName=str(j), Sclass=2, airplane_id=i)
                db.session.add(seat)
                db.session.commit()

        ticket1 = Ticket(seat_class=1, owner_id=3, buyer_id=3, saleman_id=2, flight_id=2, seat_id=15,
                         sold_time=datetime(2022, 12, 4, 18, 6, 50))
        ticket2 = Ticket(seat_class=2, owner_id=4, buyer_id=4, saleman_id=2, flight_id=6, seat_id=50,
                         sold_time=datetime(2022, 2, 4, 18, 16, 1))
        ticket3 = Ticket(seat_class=2, owner_id=6, buyer_id=6, saleman_id=2, flight_id=2, seat_id=80,
                         sold_time=datetime(2022, 1, 4, 18, 16, 1))
        ticket4 = Ticket(seat_class=2, owner_id=7, buyer_id=7, saleman_id=2, flight_id=5, seat_id=60,
                         sold_time=datetime(2022, 1, 4, 18, 16, 1))
        ticket5 = Ticket(seat_class=2, owner_id=8, buyer_id=7, saleman_id=2, flight_id=2, seat_id=14,
                         sold_time=datetime(2022, 1, 4, 18, 16, 1))
        ticket6 = Ticket(seat_class=1, owner_id=5, buyer_id=6, saleman_id=2, flight_id=12, seat_id=10,
                         sold_time=datetime(2022, 2, 4, 18, 16, 1))
        ticket7 = Ticket(seat_class=2, owner_id=8, buyer_id=8, saleman_id=2, flight_id=9, seat_id=70,
                         sold_time=datetime(2022, 5, 4, 18, 16, 1))
        ticket8 = Ticket(seat_class=1, owner_id=7, buyer_id=6, saleman_id=2, flight_id=7, seat_id=40,
                         sold_time=datetime(2022, 4, 4, 18, 16, 1))
        ticket9 = Ticket(seat_class=2, owner_id=3, buyer_id=3, saleman_id=2, flight_id=11, seat_id=50,
                         sold_time=datetime(2022, 7, 4, 18, 16, 1))
        ticket10 = Ticket(seat_class=1, owner_id=12, buyer_id=12, saleman_id=2, flight_id=2, seat_id=12,
                          sold_time=datetime(2022, 8, 4, 18, 16, 1))
        ticket11 = Ticket(seat_class=2, owner_id=11, buyer_id=11, saleman_id=2, flight_id=10, seat_id=40,
                         sold_time=datetime(2022, 9, 4, 18, 16, 1))
        ticket12 = Ticket(seat_class=1, owner_id=11, buyer_id=11, saleman_id=2, flight_id=11, seat_id=20,
                         sold_time=datetime(2022, 10, 4, 18, 16, 1))
        db.session.add_all([ticket1, ticket2, ticket3, ticket4, ticket5, ticket6,
                            ticket7, ticket8, ticket9, ticket10, ticket11, ticket12])
        db.session.commit()
