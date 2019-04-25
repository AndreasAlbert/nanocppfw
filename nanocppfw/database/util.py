import os
import re

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

from nanocppfw.database.database_objects import Dataset


def init_db_session(path_to_db):
    engine = db.create_engine('sqlite:///' + path_to_db)

    Session = sessionmaker(bind=engine)

    return Session()


class DatabaseInterface(object):
    """Common interfacing for accessing and filtering objects from the database"""

    def __init__(self, args=None, path_to_db=None, **kwargs):
        # Initialize session
        if path_to_db is None:
            self.path_to_db = os.environ["NANOCPPFW_DATABASE"]
        else:
            self.path_to_db = path_to_db
        self.session = init_db_session(self.path_to_db)

        # Allow filtering by period, path and short name
        self.filters = {}
        for filter_name in self.known_filter_names():
            optname = self.filter_name_to_cli_arg(filter_name).replace("-","_").strip("_")
            
            value = getattr(args, optname, self.default_filter())
            self.filters[filter_name] = value

        # Allow manual override of options
        for key, value in kwargs.items():
            if key.startswith("filter_"):
                setattr(self, key, value)

    def _dataset_matches_period(self, dataset):
        return re.match(self.filters["filter_period"], dataset.period_tag)

    def _dataset_matches_path(self, dataset):
        return re.match(self.filters["filter_dataset_path"], dataset.path)

    def _dataset_matches_shortname(self, dataset):
        return re.match(self.filters["filter_dataset_shortname"], dataset.shortname)

    def _dataset_matches_all(self, dataset):
        return self._dataset_matches_period(dataset) \
            and self._dataset_matches_path(dataset) \
            and self._dataset_matches_shortname(dataset)

    def get_datasets(self):
        return filter(self._dataset_matches_all, self.session.query(Dataset))

    @classmethod
    def known_filter_names(self):
        return [
            "filter_period",
            "filter_dataset_path",
            "filter_dataset_shortname"
        ]

    @classmethod
    def filter_name_to_cli_arg(self, filter_name):
        return "--db-"+filter_name.replace("_","-")

    @classmethod
    def default_filter(self):
        return ".*"

    @classmethod
    def add_cli_parsing(self, parser):
        dbargs = parser.add_argument_group("DatabaseInterface")
        for filter_name in self.known_filter_names():
            dbargs.add_argument(self.filter_name_to_cli_arg(filter_name), default=self.default_filter(), type=str,
                                 help="Regular expression to filter by {}".format(filter_name.replace("filter-", "")))
        # dbargs.add_argument('--db-filter-period', default=".*", type=str,
        #                     help='Regular expression to filter by period.')
        # dbargs.add_argument('--db-filter-dataset-path', default=".*", type=str,
        #                     help='Regular expression to filter by dataset path.')
        # dbargs.add_argument('--db-filter-dataset-shortname', default=".*", type=str,
        #                     help='Regular expression to filter by dataset short name.')
