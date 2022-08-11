import datetime
from datetime import date, timedelta
from datetime import datetime as datetime_lib
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db import DBNomenclature, DBCharacteristic, DBKnittingMachines, DBDateLoads, DBOrders, DBCharacteristicInOrders, \
    DBLoadKnittingMachines
from exceptions import CharacteristicNotFoundException


def make_session():
    engine = create_engine('sqlite:///data.db')
    session = Session(bind=engine)
    return session


def create_nomenclature(session: Session, name: str, time_references: int) -> None:
    new_nomenclature = DBNomenclature(
        name=name,
        time_references=time_references
    )
    session.add(new_nomenclature)
    session.commit()


def get_nomenclature_by_name(session: Session, name: str) -> DBNomenclature:
    query = session.query(DBNomenclature).filter(DBNomenclature.name == name)
    query = query.first()
    return query


def get_nomenclature_by_id(session: Session, nomenclature_id: int) -> DBNomenclature:
    query = session.query(DBNomenclature).filter(DBNomenclature.id == nomenclature_id)
    query = query.first()
    return query


def get_all_nomenclature(session: Session) -> List[DBNomenclature]:
    query = session.query(DBNomenclature)
    query = query.all()
    return query


def get_characteristic_for_good(session: Session, good_id: int) -> List[DBCharacteristic]:
    query = session.query(DBCharacteristic)
    query = query.filter(DBCharacteristic.nomenclature_id == good_id)
    query = query.all()
    return query


def get_nomenclature_by_characteristic_id(session: Session, characteristic_id: int) -> DBNomenclature:
    query = session.query(DBCharacteristic)
    query = query.filter(DBCharacteristic.id == characteristic_id)
    db_characteristic: DBCharacteristic = query.first()
    if db_characteristic is None:
        raise CharacteristicNotFoundException

    query = session.query(DBNomenclature)
    query = query.filter(DBNomenclature.id == db_characteristic.nomenclature_id)
    return query.first()


def get_knitting_machine_by_name(session: Session, name: str) -> List[DBKnittingMachines]:
    query = session.query(DBKnittingMachines)
    query = query.filter(DBKnittingMachines.name == name)
    return query.all()


def get_date_load(session: Session, selected_date: date, knitting_machine_id: id) -> DBDateLoads:
    query = session.query(DBDateLoads)
    query = query.filter(DBDateLoads.date == selected_date)
    query = query.filter(DBDateLoads.knitting_machine_id == knitting_machine_id)
    return query.first()


def get_date_load_starting_tomorrow(session: Session, knitting_machine_id: id) -> List[DBDateLoads]:
    query = session.query(DBDateLoads)
    current_date = date.today()
    query = query.filter(DBDateLoads.date > current_date)
    query = query.filter(DBDateLoads.knitting_machine_id == knitting_machine_id)
    return query.all()


def create_date_load(
        session: Session,
        selected_date: date,
        knitting_machine_id: id,
        total_load: int = 720
) -> DBDateLoads:
    new_date_load = DBDateLoads(
        date=selected_date,
        total_load=total_load,
        knitting_machine_id=knitting_machine_id
    )

    session.add(new_date_load)
    session.commit()

    return new_date_load


def create_order(session: Session, order_id: int) -> DBOrders:
    new_order = DBOrders(
        one_c_id=order_id
    )
    session.add(new_order)
    session.commit()

    return new_order


def get_order_by_one_c_id(session: Session, order_id: int) -> DBOrders:
    query = session.query(DBOrders)
    query = query.filter(DBOrders.one_c_id == order_id)
    return query.first()


def create_characteristic(session: Session, name: str, nomenclature_id: int) -> DBCharacteristic:
    new_characteristic = DBCharacteristic(
        name=name,
        nomenclature_id=nomenclature_id
    )
    session.add(new_characteristic)
    session.commit()

    return new_characteristic


def create_characteristic_in_order(
        session: Session,
        order_id: int,
        characteristic_id: int,
        amount: int
) -> DBCharacteristicInOrders:
    new_characteristic_in_order = DBCharacteristicInOrders(
        order_id=order_id,
        characteristic_id=characteristic_id,
        amount=amount
    )

    session.add(new_characteristic_in_order)
    session.commit()

    return new_characteristic_in_order


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


def get_characteristic_in_order(session: Session, order_id: int, characteristic_id: int) -> DBCharacteristicInOrders:
    query = session.query(DBCharacteristicInOrders)
    query = query.filter(DBCharacteristicInOrders.order_id == order_id)
    query = query.filter(DBCharacteristicInOrders.characteristic_id == characteristic_id)
    return query.first()


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


def get_order_by_id(session: Session, order_id: int) -> DBOrders:
    query = session.query(DBOrders).filter(DBOrders.id == order_id)
    return query.first()


def get_all_orders(session: Session) -> List[DBOrders]:
    query = session.query(DBOrders)
    return query.all()


def get_characteristic_by_id(session: Session, characteristic_id: int) -> DBCharacteristic:
    query = session.query(DBCharacteristic).filter(DBCharacteristic.id == characteristic_id)
    return query.first()


def get_characteristic_in_order_by_id(
        session: Session,
        characteristic_in_order_id: int
) -> DBCharacteristicInOrders:
    query = session.query(DBCharacteristicInOrders).filter(DBCharacteristicInOrders.id == characteristic_in_order_id)
    return query.first()


def get_info_about_characteristic_in_order(session: Session, characteristic_in_order_id: int) -> dict:
    query = session.query(DBCharacteristicInOrders).filter(DBCharacteristicInOrders.id == characteristic_in_order_id)
    db_characteristic_in_order: DBCharacteristicInOrders = query.first()
    db_order = get_order_by_id(session, db_characteristic_in_order.order_id)
    db_nomenclature = get_nomenclature_by_characteristic_id(session, db_characteristic_in_order.characteristic_id)
    db_characteristic = get_characteristic_by_id(session, db_characteristic_in_order.characteristic_id)

    characteristic_info_to_view = {
        "order_number": db_order.one_c_id,
        "nomenclature_name": db_nomenclature.name,
        "characteristic_name": db_characteristic.name,
        "amount": db_characteristic_in_order.amount
    }

    return characteristic_info_to_view


def get_all_characteristics_in_order(session: Session) -> List[DBCharacteristicInOrders]:
    query = session.query(DBCharacteristicInOrders)
    return query.all()


def get_characteristics_for_order(session: Session, order_id: int) -> List[DBCharacteristicInOrders]:
    query = session.query(DBCharacteristicInOrders).filter(DBCharacteristicInOrders.order_id == order_id)
    return query.all()


def get_load_knitting_machines_filter_by_characteristic_in_order_id(
        session: Session,
        characteristic_in_order_id: int
) -> List[DBLoadKnittingMachines]:
    query = session.query(DBLoadKnittingMachines)
    query = query.filter(DBLoadKnittingMachines.characteristic_in_order_id == characteristic_in_order_id)
    return query.all()


def get_date_load_by_id(session: Session, date_load_id: int) -> DBDateLoads:
    query = session.query(DBDateLoads).filter(DBDateLoads.id == date_load_id)
    return query.first()


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


def delete_order(session: Session, order_id: int):
    query = session.query(DBOrders).filter(DBOrders.id == order_id)
    query.delete()


def delete_characteristics_in_order(session: Session, order_id: int):
    query = session.query(DBCharacteristicInOrders).filter(DBCharacteristicInOrders.order_id == order_id)
    query.delete()


def delete_load_machine_for_characteristic(session: Session, characteristic_in_order_id: int):
    query = session.query(DBLoadKnittingMachines).filter(
        DBLoadKnittingMachines.characteristic_in_order_id == characteristic_in_order_id)
    query.delete()


def get_deadline_for_order(session: Session, order_id: int) -> datetime:
    query = session.query(DBCharacteristicInOrders).filter(DBCharacteristicInOrders.order_id == order_id)
    db_characteristics_in_order: List[DBCharacteristicInOrders] = query.all()
    order_deadline_date = None
    for current_characteristic_in_order in db_characteristics_in_order:
        characteristic_deadline = get_deadline_for_characteristic_in_order(session, current_characteristic_in_order.id)
        if order_deadline_date is None:
            order_deadline_date = characteristic_deadline
        elif characteristic_deadline > order_deadline_date:
            order_deadline_date = characteristic_deadline

    return order_deadline_date


if __name__ == '__main__':
    test_session = make_session()
    # create_order_with_date_load(test_session, 1, 1, 2)
    get_grouped_loading_of_machines(test_session)
