#!/usr/bin/env python
import sys
import PyBindings
import argparse


from database_objects import *
import sqlalchemy as db

from sqlalchemy.orm import sessionmaker
import re

def init_db_session(path_to_db):
    engine = db.create_engine('sqlite:///' + path_to_db)

    Session = sessionmaker(bind=engine)

    return Session()

def parse_cli():
    parser = argparse.ArgumentParser(description='Runs HInv Analysis')

    subparsers = parser.add_subparsers()

    analysis_args = parser.add_argument_group("Analysis")
    analysis_args.add_argument('--analyzer', default="HInvAnalyzer", type=str,
                        help='Analyzer to run.')

    input_args = parser.add_argument_group("Inputs")
    input_args.add_argument('--dataset', default=None, required=True, type=str,
                        help='Dataset name.')

    input_args.add_argument('--files', default=None, type=str, nargs='+',
                        help='Set file list manually.')

    input_args.add_argument('--db', default="../python/database/test.db", type=str,
                        help='Database file to use.')

    input_args.add_argument('--skim', default="19Mar19", type=str,
                        help='Skim to run over.')
    input_args.add_argument('--period', default="2017", type=str,
                        help='Period to run over.')


    parser_local = subparsers.add_parser("local")
    parser_local.set_defaults(func=do_local)

    parser_sub = subparsers.add_parser("submit")
    parser_local.set_defaults(func=do_submit)

    args = parser.parse_args()





    return args


def do_local(args):
    # Initialize right type of analyzer
    Analyzer = getattr(PyBindings, args.analyzer)

    if args.files:
        # Manual mode
        ana = Analyzer(args.files)
        ana.set_fixed_dataset(args.dataset)
        ana.run()
    else:
        # Database mode
        # /disk1/albert/hinv_vbf/slc7/analysis/nanocppfw/python/database/test.db
        session = init_db_session(args.db)

        for dataset in session.query(Dataset):

            # Period and dataset name must match
            match = re.match(args.period, dataset.period) \
                    and re.match(args.dataset, dataset.path)
            if not match:
                continue

            # Files from right skim
            files = [x for x in dataset.files if x.skim_tag == args.skim]

            ana = Analyzer(files)
            ana.set_fixed_dataset(args.dataset)
            ana.run()
    return

def do_submit(args):
    return

def main():
    args = parse_cli()


if __name__ == "__main__":
    main()