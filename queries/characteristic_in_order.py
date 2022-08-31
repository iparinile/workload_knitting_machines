from typing import List

from sqlalchemy.orm import Session

from db import DBCharacteristicInOrders
from queries.characteristic import get_characteristic_by_id
from queries.nomenclature import get_nomenclature_by_characteristic_id
from queries.orders import get_order_by_id


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


def get_characteristic_in_order(session: Session, order_id: int, characteristic_id: int) -> DBCharacteristicInOrders:
    query = session.query(DBCharacteristicInOrders)
    query = query.filter(DBCharacteristicInOrders.order_id == order_id)
    query = query.filter(DBCharacteristicInOrders.characteristic_id == characteristic_id)
    return query.first()


def get_characteristic_in_order_by_id(
        session: Session,
        characteristic_in_order_id: int
) -> DBCharacteristicInOrders:
    query = session.query(DBCharacteristicInOrders).filter(DBCharacteristicInOrders.id == characteristic_in_order_id)
    return query.first()


def delete_characteristics_in_order(session: Session, order_id: int):
    query = session.query(DBCharacteristicInOrders).filter(DBCharacteristicInOrders.order_id == order_id)
    query.delete()
