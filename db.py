import datetime

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, TIMESTAMP, Date, Float
from sqlalchemy.orm import declarative_base

engine = create_engine('sqlite:///data.db')

Base = declarative_base()


class DBNomenclature(Base):
    __tablename__ = "Nomenclature"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    time_references = Column(Integer, nullable=False)


class DBCharacteristic(Base):
    __tablename__ = "Characteristic"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=False)
    nomenclature_id = Column(Integer, ForeignKey('Nomenclature.id'), nullable=False)


class DBKnittingMachines(Base):
    __tablename__ = "Knitting_machines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)


class DBCharacteristicInOrders(Base):
    __tablename__ = "Characteristic_in_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('Orders.id'), nullable=False)
    characteristic_id = Column(Integer, ForeignKey('Characteristic.id'), nullable=False)
    amount = Column(Integer, nullable=False)


class DBOrders(Base):
    __tablename__ = "Orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    one_c_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)


class DBDateLoads(Base):
    __tablename__ = "Date_loads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    total_load = Column(Integer, nullable=False)
    knitting_machine_id = Column(Integer, ForeignKey('Knitting_machines.id'), nullable=False)


class DBLoadKnittingMachines(Base):
    __tablename__ = "Load_knitting_machines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_load_id = Column(Integer, ForeignKey('Date_loads.id'), nullable=False)
    characteristic_in_order_id = Column(Integer, ForeignKey('Characteristic_in_orders.id'), nullable=False)
    time_references = Column(Integer, nullable=False)
