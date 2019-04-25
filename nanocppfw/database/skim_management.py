#!/usr/bin/env python

from sqlalchemy import String
import luigi
from luigi.contrib import sqla

from database_objects import Period, Dataset, Skim, File
from dasgowrapper import das_go_query

import os
import tarfile
import json
import re
import subprocess
import sys

class skim(luigi.Config):
    cmssw_base = luigi.Parameter(default='')

class InitializePeriod(sqla.CopyToTable):
    period = luigi.Parameter()

    reflect = True
    connection_string = "sqlite:///test.db"  # in memory SQLite database
    table = "period"  # name of the table to store data

    def rows(self):
        yield (self.period,)

def pretty_dataset_name(dataset, is_mc):
    ### Prettify data set name
    dataset_simplified, conditions = dataset.split("/")[1:3]

    if is_mc:
        # Attach short campaign identifier
        for campaign in ["RunIIFall17", "RunIIAutumn18"]:
            if campaign in conditions:
                dataset_simplified = "{}_{}".format(campaign, dataset_simplified)

        # Check if extension
        m = re.match(".*(ext\d+)", conditions);
        if m:
            groups = m.groups()
            assert len(groups) == 1
            dataset_simplified = "{}_{}".format(dataset_simplified, groups[0])
    else:
        m = re.match("(Run\d+[A-Z])", conditions)
        if m:
            groups = m.groups()
            assert len(groups) == 1
            dataset_simplified = "{}_{}".format(dataset_simplified, groups[0])

    return dataset_simplified

class GetDatasets(luigi.Task):
    input_path = luigi.Parameter()

    def output(self):
        return MockTarget("mock")

    def expand_input_path(self):
        """Expand a dataset path into a list of matching paths

        If the input path is already a fully formed path,
        the output list will simply contain that path as its
        only element. If, however, there are asterisks in the
        input, a DAS query will be used to find all data set
        names matching this pattern.

        :raises RuntimeError: If DAS reports that no matching paths are found.
        """
        rawlines = das_go_query("dataset={}".format(self.input_path))

        paths = list(map(lambda x: x.decode("utf-8").strip(), rawlines.splitlines()))
        if not len(paths):
            raise RuntimeError("No datasets found for path {}.".format(self.input_path))
        self.paths = paths

    def run(self):
        self.expand_input_path()
        out = self.output().open("w")
        rawline = "{path} {shortname} {is_mc} {xs} {nevents} {period}\n"
        for ipath in self.paths:
            # Get data set properties from DAS
            props = json.loads(das_go_query("dataset={}".format(ipath), json=True))
            data = {}
            for entry in props:
                data.update(entry["dataset"][0])

            # Number of events in data set
            nevents = int(data["nevents"])

            # MC or not?
            is_mc = data["datatype"] != "data"

            # Run period
            period = data["acquisition_era_name"]

            yield InitializePeriod(period)

            # Shortened name
            shortname = pretty_dataset_name(ipath, is_mc)

            # Dummy
            xs = 0


            # Construct row
            line = rawline.format(path=ipath, shortname=shortname, is_mc=is_mc, xs=xs, nevents=nevents, period=period)
            out.write(line)
        out.close()

class RegisterDatasets(sqla.CopyToTable):
    input_path = luigi.Parameter()

    reflect = True
    connection_string = "sqlite:///test.db"
    table = "dataset"
    column_separator=" "
    def requires(self):
        return GetDatasets(self.input_path)

from datetime import datetime
class RegisterSkim(sqla.CopyToTable):
    skim_tag = luigi.Parameter()

    reflect = True
    connection_string = "sqlite:///test.db"
    table = "skim"

    def rows(self):
        yield [self.skim_tag, datetime(2019,4,3)]

class ExtractTarMember(luigi.Task):
    """Task that extracts a given tar file

    :param tarpath: Path to the tar file.
    :type tarpath: string
    :param member: Member of the tar file to extract.
    :type member: string
    """

    tarpath = luigi.Parameter()
    member = luigi.Parameter()

    def run(self):
        tf = tarfile.open(self.tarpath)
        tf.extract(self.member, path=os.path.dirname(self.tarpath))

    def output(self):
        output_path = os.path.join(os.path.dirname(self.tarpath), self.member)
        return luigi.LocalTarget(path=output_path)


import imp
from crab_helpers import get_crab_files
from luigi.mock import MockTarget

class GetCrabFiles(luigi.Task):
    """
    Compiles output file info for a CRAB task

    For each file, a line of information is written into a
    mock target. The lines are correctly formatted to be fed
    into the sqla File constructor.
    """
    crab_path = luigi.Parameter()

    def run(self):
        # Read the config file to determine the dataset and skim tag
        configfile = os.path.join(self.crab_path,"inputs/debug/crabConfig.py")
        dummy =  imp.load_source('dummy', configfile)

        dataset = dummy.config.Data.inputDataset
        skim_tag = dummy.config.Data.outputDatasetTag

        # Make sure dataset is registered
        yield RegisterDatasets(dataset)
        yield RegisterSkim(skim_tag)

        # Extract file list and write
        rawline = "{path} {size} {events} {dataset} {skim_tag}\n"
        out = self.output().open("w")
        for path in get_crab_files(self.crab_path):
            size = 0
            events = 0
            line = rawline.format(path=path, size=size, events=events, dataset=dataset, skim_tag=skim_tag)
            out.write(line)
        out.close()

    def output(self):
        return MockTarget("mymock")

    def requires(self):
        yield ExtractTarMember(tarpath=os.path.join(self.crab_path,"inputs/debugFiles.tgz"),
                                member="debug/crabConfig.py")

class RegisterCrabFiles(sqla.CopyToTable):
    crab_path = luigi.Parameter()

    reflect = True
    connection_string = "sqlite:///test.db"
    table = "file"
    column_separator=" "
    def requires(self):
        return GetCrabFiles(self.crab_path)

if __name__ == '__main__':
    tasks = []
    for path in sys.argv:
        if not os.path.isdir(path):
            continue
        tasks.append(
            RegisterCrabFiles(crab_path=path)
        )

    luigi.build(tasks, local_scheduler=True)
