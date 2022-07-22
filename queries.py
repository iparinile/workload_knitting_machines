from datetime import date, timedelta
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


def create_nomenclature(session: Session, article: str, name: str, time_references: int) -> None:
    new_nomenclature = DBNomenclature(
        article=article,
        name=name,
        time_references=time_references
    )
    session.add(new_nomenclature)
    session.commit()


def get_nomenclature_by_name(session: Session, name: str) -> DBNomenclature:
    query = session.query(DBNomenclature).filter(DBNomenclature.name == name)
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


def get_knitting_machine_by_name(session: Session, name: str) -> DBKnittingMachines:
    query = session.query(DBKnittingMachines)
    query = query.filter(DBKnittingMachines.name == name)
    return query.first()


def get_date_load(session: Session, selected_date: date, knitting_machine_id: id) -> DBDateLoads:
    query = session.query(DBDateLoads)
    query = query.filter(DBDateLoads.date == selected_date)
    query = query.filter(DBDateLoads.knitting_machine_id == knitting_machine_id)
    return query.first()


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


def create_order_with_date_load(session: Session, order_id: int, characteristic_id: int, amount: int):
    current_date = date.today()
    db_order = get_order_by_one_c_id(session, order_id)

    if db_order is None:
        db_order = create_order(session, order_id)

    db_characteristic_in_order = create_characteristic_in_order(session, db_order.id, characteristic_id, amount)

    db_nomenclature = get_nomenclature_by_characteristic_id(session, characteristic_id)

    knitting_machine_name = db_nomenclature.article.split("-")[0]
    db_knitting_machine = get_knitting_machine_by_name(session, knitting_machine_name)

    time_references = db_nomenclature.time_references * db_characteristic_in_order.amount

    while time_references != 0:
        current_date = current_date + timedelta(days=1)  # Смотрим следующий день и выбираем его текущим
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
    query: List[DBDateLoads] = session.query(DBDateLoads).all()
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


def get_characteristic_by_id(session: Session, characteristic_id: int) -> DBCharacteristic:
    query = session.query(DBCharacteristic).filter(DBCharacteristic.id == characteristic_id)
    return query.first()


def get_info_about_characteristic_in_order(session: Session, characteristic_in_order_id: int):
    query = session.query(DBCharacteristicInOrders).filter(DBCharacteristicInOrders.id == characteristic_in_order_id)
    db_characteristic_in_order: DBCharacteristicInOrders = query.first()
    db_order = get_order_by_id(session, db_characteristic_in_order.order_id)
    db_nomenclature = get_nomenclature_by_characteristic_id(session, db_characteristic_in_order.characteristic_id)
    db_characteristic = get_characteristic_by_id(session, db_characteristic_in_order.characteristic_id)

    characteristic_info_to_view = {
        "order_number": db_order.one_c_id,
        "nomenclature_name": db_nomenclature.name,
        "article": db_nomenclature.article,
        "characteristic_name": db_characteristic.name
    }

    return characteristic_info_to_view


if __name__ == '__main__':
    test_session = make_session()
    # create_order_with_date_load(test_session, 1, 1, 2)
    get_grouped_loading_of_machines(test_session)
