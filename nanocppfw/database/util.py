import os
import re

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

from nanocppfw.database.database_objects import Dataset

def init_db_session(path_to_db):
    engine = db.create_engine('sqlite:///' + path_to_db)

    Session = sessionmaker(bind=engine)

    return Session()

class DatabaseInterface():
    """Common interfacing for accessing and filtering objects from the database"""

    def __init__(self, path_to_db=None, filter_period=".*", filter_dataset_path=".*", filter_dataset_shortname=".*"):
        # Initialize session
        if path_to_db is None:
            self.path_to_db = os.environ["NANOCPPFW_DATABASE"]
        else:
            self.path_to_db = path_to_db
        self.session = init_db_session(self.path_to_db)

        # Allow filtering by period, path and short name
        self.filter_period = filter_period
        self.filter_dataset_path = filter_dataset_path
        self.filter_dataset_shortname = filter_dataset_shortname

    def _dataset_matches_period(self, dataset):
        return re.match(self.filter_period, dataset.period_tag)

    def _dataset_matches_path(self, dataset):
        return re.match(self.filter_dataset_path, dataset.path)

    def _dataset_matches_shortname(self, dataset):
        return re.match(self.filter_dataset_shortname, dataset.shortname)

    def _dataset_matches_all(self, dataset):
        return self._dataset_matches_period(dataset) \
            and self._dataset_matches_path(dataset) \
            and self._dataset_matches_shortname(dataset)

    def get_datasets(self):
        return filter(self._dataset_matches_all, self.session.query(Dataset))