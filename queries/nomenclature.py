from typing import List

from sqlalchemy.orm import Session

from db import DBNomenclature, DBCharacteristic
from exceptions import CharacteristicNotFoundException


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


def get_nomenclature_by_characteristic_id(session: Session, characteristic_id: int) -> DBNomenclature:
    query = session.query(DBCharacteristic)
    query = query.filter(DBCharacteristic.id == characteristic_id)
    db_characteristic: DBCharacteristic = query.first()
    if db_characteristic is None:
        raise CharacteristicNotFoundException

    query = session.query(DBNomenclature)
    query = query.filter(DBNomenclature.id == db_characteristic.nomenclature_id)
    return query.first()
