import datetime
from typing import List

from sqlalchemy.orm import Session

from db import DBOrders, DBCharacteristicInOrders
from queries.load_knitting_machines import get_deadline_for_characteristic_in_order


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


def get_order_by_id(session: Session, order_id: int) -> DBOrders:
    query = session.query(DBOrders).filter(DBOrders.id == order_id)
    return query.first()


def get_all_orders(session: Session) -> List[DBOrders]:
    query = session.query(DBOrders)
    return query.all()


def delete_order(session: Session, order_id: int):
    query = session.query(DBOrders).filter(DBOrders.id == order_id)
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
