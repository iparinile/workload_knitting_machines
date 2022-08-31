from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from queries.load_knitting_machines import get_grouped_loading_of_machines


def make_session():
    engine = create_engine('sqlite:///data.db')
    session = Session(bind=engine)
    return session


if __name__ == '__main__':
    test_session = make_session()
    # create_order_with_date_load(test_session, 1, 1, 2)
    get_grouped_loading_of_machines(test_session)
