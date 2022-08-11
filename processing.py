from sqlalchemy.orm import Session

from queries import get_order_by_one_c_id, get_characteristics_for_order, delete_load_machine_for_characteristic, \
    delete_characteristics_in_order, delete_order, get_nomenclature_by_characteristic_id, get_knitting_machine_by_name, \
    get_date_load_starting_tomorrow, get_load_knitting_machines_by_date_load_id, get_characteristic_by_id, \
    get_characteristic_in_order_by_id, create_date_load_to_characteristic


def delete_order_and_update_date_loads(session: Session, order_one_c_id: int):
    db_order = get_order_by_one_c_id(session, order_one_c_id)

    machines = []  # Все машины, у которых нужно изменить очередь загрузки

    all_characteristics_in_order = get_characteristics_for_order(session, db_order.id)

    for db_characteristic_in_order in all_characteristics_in_order:
        db_nomenclature = get_nomenclature_by_characteristic_id(session, db_characteristic_in_order.characteristic_id)
        machine_name = db_nomenclature.name.split("-")[0]
        if machine_name not in machines:
            machines.append(machine_name)
        delete_load_machine_for_characteristic(session, db_characteristic_in_order.id)

    delete_characteristics_in_order(session, db_order.id)
    delete_order(session, db_order.id)

    characteristics = dict()

    for machine_name in machines:
        db_machine = get_knitting_machine_by_name(session, machine_name)[0]
        all_date_loads = get_date_load_starting_tomorrow(session, db_machine.id)
        for db_date_load in all_date_loads:
            all_loads = get_load_knitting_machines_by_date_load_id(session, db_date_load.id)
            for db_load in all_loads:
                db_characteristic_in_order = get_characteristic_in_order_by_id(
                    session,
                    db_load.characteristic_in_order_id
                )
                db_nomenclature = get_nomenclature_by_characteristic_id(session,
                                                                        db_characteristic_in_order.characteristic_id)
                characteristic_in_order_id = db_characteristic_in_order.id
                if characteristic_in_order_id not in characteristics.keys():
                    characteristics[characteristic_in_order_id] = db_characteristic_in_order
                delete_load_machine_for_characteristic(session, characteristic_in_order_id)

    for characteristic_in_order_id in characteristics.keys():
        db_characteristic_in_order = characteristics[characteristic_in_order_id]
        create_date_load_to_characteristic(session, db_characteristic_in_order,
                                           db_characteristic_in_order.characteristic_id,
                                           db_characteristic_in_order.amount)
