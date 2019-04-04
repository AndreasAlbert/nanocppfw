#!/usr/bin/env python

from sqlalchemy import Column, Integer, String, Boolean, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey

import sys
import os

Base = declarative_base()
class Period(Base):
    # Properties
    __tablename__ = 'period'
    tag = Column(String(100), primary_key=True)

    # Relationships
    datasets = relationship("Dataset")

class Dataset(Base):
    # Properties
    __tablename__ = 'dataset'
    path = Column(String(100), primary_key=True)
    is_mc = Column(Boolean, nullable=False)
    xs = Column(Float)
    events = Column(Integer)

    # Relationships
    period_tag = Column(String(100), ForeignKey('period.tag'))
    files = relationship("File")


class Skim(Base):
    # Properties
    __tablename__ = "skim"
    tag = Column(String(100), primary_key=True)
    date = Column(Date)

    # Relationships
    files = relationship("File")


class File(Base):
    # Properties
    __tablename__ = 'file'
    path = Column(String(250), primary_key=True)
    size = Column(Float)
    nevents = Column(Integer)

    # Relationships
    dataset_path = Column(String(100), ForeignKey("dataset.path"))
    skim_tag = Column(String(100), ForeignKey("skim.tag"))


def main():
    try:
        path_to_db = sys.argv[1]
    except IndexError:
        path_to_db = "test.db"

    if os.path.exists(path_to_db):
        raise IOError("Will not overwrite existing input: {}.".format(path_to_db))

    prefix = "sqlite:///"
    if not path_to_db.startswith(prefix):
        path_to_db = prefix + path_to_db
    engine = create_engine(path_to_db)
    Base.metadata.create_all(engine)



if __name__ == "__main__":
    main()
