#!/usr/bin/env python
import sys
import nanocppfw.pybindings
import argparse
import os

from nanocppfw.database.database_objects import Dataset
import sqlalchemy as db

from sqlalchemy.orm import sessionmaker
import re

import logging

log = logging.getLogger("trybind")

def init_db_session(path_to_db):
    engine = db.create_engine('sqlite:///' + path_to_db)

    Session = sessionmaker(bind=engine)

    return Session()

def parse_cli():
    parser = argparse.ArgumentParser(description='Runs Analysis')


    general_args = parser.add_argument_group("General")
    general_args.add_argument('--debug', default="INFO", type=str, choices=logging._levelNames.keys(),
                        help='Debug level.')
    general_args.add_argument('--jobs','-j', default=1, type=int,
                        help='Number of parallel processes for the analysis.')

    analysis_args = parser.add_argument_group("Analysis")
    analysis_args.add_argument('--analyzer', default="HInvAnalyzer", type=str,
                        help='Analyzer to run.')

    input_args = parser.add_argument_group("Inputs")
    input_args.add_argument('--dataset', default=None, required=False, type=str,
                        help='Dataset name.')

    input_args.add_argument('--files', default=None, type=str, nargs='+',
                        help='Set file list manually.')

    input_args.add_argument('--db', default="../python/database/test.db", type=str,
                        help='Database file to use.')

    input_args.add_argument('--skim', default="19Mar19", type=str,
                        help='Skim to run over.')
    input_args.add_argument('--period', default="2017", type=str,
                        help='Period to run over.')

    subparsers = parser.add_subparsers  ()

    parser_local = subparsers.add_parser("local")
    parser_local.set_defaults(func=do_local)

    parser_sub = subparsers.add_parser("submit")
    parser_sub.set_defaults(func=do_submit)

    args = parser.parse_args()


    # Logger
    format = '%(levelname)s (%(name)s) [%(asctime)s]: %(message)s'
    date = '%F %H:%M:%S'
    logging.basicConfig(
        level=logging._levelNames[args.debug], format=format, datefmt=date)


    args.func(args)


def do_local(args):
    print "Running locally."

    # Initialize right type of analyzer
    Analyzer = getattr(nanocppfw.pybindings, args.analyzer)

    if args.files:
        # Manual mode
        ana = Analyzer(args.files)
        ana.set_fixed_dataset(args.dataset)
        ana.run()
    else:
        # Database mode
        # /disk1/albert/hinv_vbf/slc7/analysis/nanocppfw/python/database/test.db
        session = init_db_session(os.path.expanduser(args.db))

        for dataset in session.query(Dataset):

            # Period and dataset name must match
            match = re.match(args.period, dataset.period_tag) \
                    and re.match(args.dataset, dataset.path)
            if not match:
                log.debug("No match: {}".format(dataset.path))
                continue

            log.debug("Matching dataset: {}".format(dataset.path))

            # Files from right skim
            files = [x.path for x in dataset.files if x.skim_tag == args.skim]

            if not files:
                log.debug("No files found with skim: {}".format(skim_tag))
                continue
            ana = Analyzer(files)
            ana.set_fixed_dataset(dataset.shortname)
            ana.set_ncpu(args.jobs)
            ana.run()
    return

def do_submit(args):
    return

def main():
    parse_cli()


if __name__ == "__main__":
    main()