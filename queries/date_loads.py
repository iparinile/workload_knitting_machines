from datetime import date
from typing import List

from sqlalchemy.orm import Session

from db import DBDateLoads


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


def get_date_load_for_knitting_machine(session: Session, knitting_machine_id: id) -> List[DBDateLoads]:
    query = session.query(DBDateLoads).filter(DBDateLoads.knitting_machine_id == knitting_machine_id)
    return query.all()


def get_date_load_for_machine_on_date(session: Session, knitting_machine_id: id, current_date: date) -> DBDateLoads:
    query = session.query(DBDateLoads)
    query = query.filter(DBDateLoads.knitting_machine_id == knitting_machine_id)
    query = query.filter(DBDateLoads.date == current_date)
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


def get_date_load_by_id(session: Session, date_load_id: int) -> DBDateLoads:
    query = session.query(DBDateLoads).filter(DBDateLoads.id == date_load_id)
    return query.first()
