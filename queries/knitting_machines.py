from typing import List

from sqlalchemy.orm import Session

from db import DBKnittingMachines


def get_knitting_machine_by_name(session: Session, name: str) -> List[DBKnittingMachines]:
    query = session.query(DBKnittingMachines)
    query = query.filter(DBKnittingMachines.name == name)
    return query.all()


def get_all_knitting_machines(session: Session) -> List[DBKnittingMachines]:
    query = session.query(DBKnittingMachines)
    return query.all()
