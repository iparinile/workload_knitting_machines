from typing import List

from db import DBCharacteristicInOrders


def make_dict_with_characteristics_in_order(characteristics_in_order: List[DBCharacteristicInOrders]) -> dict:
    characteristics_dict = {}
    for db_characteristic_in_order in characteristics_in_order:
        characteristics_dict[db_characteristic_in_order.characteristic_id] = {
            "id": db_characteristic_in_order.id,
            "amount": db_characteristic_in_order.amount
        }
    return characteristics_dict
