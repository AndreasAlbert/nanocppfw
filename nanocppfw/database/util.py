import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

def init_db_session(path_to_db):
    engine = db.create_engine('sqlite:///' + path_to_db)

    Session = sessionmaker(bind=engine)

    return Session()

