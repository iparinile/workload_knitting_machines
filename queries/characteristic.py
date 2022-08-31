from typing import List

from sqlalchemy.orm import Session

from db import DBCharacteristic


def get_characteristic_for_good(session: Session, good_id: int) -> List[DBCharacteristic]:
    query = session.query(DBCharacteristic)
    query = query.filter(DBCharacteristic.nomenclature_id == good_id)
    query = query.all()
    return query


def create_characteristic(session: Session, name: str, nomenclature_id: int) -> DBCharacteristic:
    new_characteristic = DBCharacteristic(
        name=name,
        nomenclature_id=nomenclature_id
    )
    session.add(new_characteristic)
    session.commit()

    return new_characteristic


def get_characteristic_by_id(session: Session, characteristic_id: int) -> DBCharacteristic:
    query = session.query(DBCharacteristic).filter(DBCharacteristic.id == characteristic_id)
    return query.first()
