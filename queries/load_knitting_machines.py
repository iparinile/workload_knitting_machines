import datetime
from datetime import date, timedelta, datetime as datetime_lib
from typing import List

from sqlalchemy.orm import Session

from db import DBLoadKnittingMachines, DBCharacteristicInOrders, DBDateLoads
from queries.date_loads import get_date_load, create_date_load, get_date_load_by_id
from queries.knitting_machines import get_knitting_machine_by_name
from queries.nomenclature import get_nomenclature_by_characteristic_id


def create_load_knitting_machines(
        session: Session,
        characteristic_in_order_id: int,
        date_load_id: int,
        time_references: int
) -> DBLoadKnittingMachines:
    new_load_knitting_machines = DBLoadKnittingMachines(
        date_load_id=date_load_id,
        characteristic_in_order_id=characteristic_in_order_id,
        time_references=time_references
    )

    session.add(new_load_knitting_machines)
    session.commit()

    return new_load_knitting_machines


def get_busy_minutes(session: Session, date_load_id: int) -> int:
    query = session.query(DBLoadKnittingMachines)
    query = query.filter(DBLoadKnittingMachines.date_load_id == date_load_id)
    result: List[DBLoadKnittingMachines] = query.all()
    total_load = 0
    for load in result:
        total_load += load.time_references

    return total_load


def create_date_load_to_characteristic(
        session: Session,
        db_characteristic_in_order: DBCharacteristicInOrders,
        characteristic_id: int,  # убрать, уже есть в DBCharacteristicInOrders
        amount: int  # убрать, уже есть в DBCharacteristicInOrders
):
    current_date = date.today()

    db_nomenclature = get_nomenclature_by_characteristic_id(session, characteristic_id)

    knitting_machine_name = db_nomenclature.name.split("-")[0]
    db_knitting_machines = get_knitting_machine_by_name(session, knitting_machine_name)

    time_references = db_nomenclature.time_references * db_characteristic_in_order.amount

    while time_references != 0:
        current_date = current_date + timedelta(days=1)  # Смотрим следующий день и выбираем его текущим
        for db_knitting_machine in db_knitting_machines:
            db_date_load = get_date_load(session, current_date, db_knitting_machine.id)

            if db_date_load is None:
                db_date_load = create_date_load(session, current_date, db_knitting_machine.id)

            busy_minutes = get_busy_minutes(session, db_date_load.id)

            total_load = db_date_load.total_load - busy_minutes

            if total_load <= 0:
                continue
            elif time_references <= total_load:
                create_load_knitting_machines(session, db_characteristic_in_order.id, db_date_load.id, time_references)
                time_references = 0
            else:
                sewing_time = 0
                for _ in range(amount):
                    if db_nomenclature.time_references > total_load:
                        break
                    sewing_time += db_nomenclature.time_references
                    time_references -= db_nomenclature.time_references
                    total_load -= db_nomenclature.time_references

                if sewing_time != 0:
                    create_load_knitting_machines(session, db_characteristic_in_order.id, db_date_load.id, sewing_time)


def get_load_knitting_machines_by_date_load_id(session: Session, date_load_id: int) -> List[DBLoadKnittingMachines]:
    query = session.query(DBLoadKnittingMachines)
    query = query.filter(DBLoadKnittingMachines.date_load_id == date_load_id)
    return query.all()


def get_grouped_loading_of_machines(session: Session) -> dict:
    yesterday_date = datetime_lib.now() - timedelta(days=1)
    query: List[DBDateLoads] = session.query(DBDateLoads).filter(DBDateLoads.date >= yesterday_date).all()
    loading_machines = dict()
    for db_date_load in query:
        if db_date_load.knitting_machine_id not in loading_machines.keys():
            loading_machines[db_date_load.knitting_machine_id] = []

        load_machine_data = get_load_knitting_machines_by_date_load_id(session, db_date_load.id)
        loading_machines[db_date_load.knitting_machine_id].append({
            "date": db_date_load.date,
            "total_load": db_date_load.total_load,
            "load_machine_data": load_machine_data
        })

    return loading_machines


def get_load_knitting_machines_filter_by_characteristic_in_order_id(
        session: Session,
        characteristic_in_order_id: int
) -> List[DBLoadKnittingMachines]:
    query = session.query(DBLoadKnittingMachines)
    query = query.filter(DBLoadKnittingMachines.characteristic_in_order_id == characteristic_in_order_id)
    return query.all()


def finding_deadline_date_obj(session: Session, load_knitting_machines_data: List[DBLoadKnittingMachines]) -> datetime:
    deadline_date = None
    for current_load_machines in load_knitting_machines_data:
        db_date_load = get_date_load_by_id(session, current_load_machines.date_load_id)
        if deadline_date is None:
            deadline_date = db_date_load.date
        elif db_date_load.date > deadline_date:
            deadline_date = db_date_load.date

    return deadline_date


def get_deadline_for_characteristic_in_order(session: Session, characteristic_in_order_id: int) -> datetime:
    loads_knitting_machine = get_load_knitting_machines_filter_by_characteristic_in_order_id(
        session,
        characteristic_in_order_id
    )
    deadline_date = finding_deadline_date_obj(session, loads_knitting_machine)
    return deadline_date


def delete_load_machine_for_characteristic(session: Session, characteristic_in_order_id: int):
    query = session.query(DBLoadKnittingMachines).filter(
        DBLoadKnittingMachines.characteristic_in_order_id == characteristic_in_order_id)
    query.delete()


def get_load_machine_by_date_load(session: Session, date_load_id: int) -> DBLoadKnittingMachines:
    query = session.query(DBLoadKnittingMachines).filter(DBLoadKnittingMachines.date_load_id == date_load_id)
    return query.first()
