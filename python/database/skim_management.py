#!/usr/bin/env python3

from sqlalchemy import String
import luigi
from luigi.contrib import sqla

from database_objects import Period, Dataset, Skim, File
from dasgowrapper import das_go_query


class skim(luigi.Config):
    cmssw_base = luigi.Parameter(default='')

class InitializePeriod(sqla.CopyToTable):
    # If database table is already created, then the schema can be loaded
    # by setting the reflect flag to True
    reflect = True
    connection_string = "sqlite:///test.db"  # in memory SQLite database
    table = "period"  # name of the table to store data

    def rows(self):
        for row in [("2017",),("2018",)]:
            yield row


class InitializeDatasets(sqla.CopyToTable):
    input_path = luigi.Parameter()

    reflect = True
    connection_string = "sqlite:///test.db"  # in memory SQLite database
    table = "dataset"

    def expand_input_path(self):
        """Expand a dataset path into a list of matching paths

        If the input path is already a fully formed path,
        the output list will simply contain that path as its
        only element. If, however, there are asterisks in the 
        input, a DAS query will be used to find all data set
        names matching this pattern.
        
        :raises RuntimeError: If DAS reports that no matching paths are found.
        """
        paths = das_go_query(f"dataset={self.input_path}")
        if not len(paths):
            raise RuntimeError(f"No datasets found for path {self.input_path}")
        self.paths = paths

    def rows(self):
        self.expand_input_path()
        for ipath in self.paths:

            # Get number of events from DAS
            lines = das_go_query(f"dataset={ipath} | grep dataset.nevents")
            assert(len(lines)==1)
            nevents = int(lines[0])

            # Deduce run period
            if "RunIISummer16" in ipath:
                period = "2016"
            elif "RunIIFall17" in ipath:
                period = "2017"
            elif "RunIIAutumn18" in ipath:
                period = "2018"
            
            # MC or not?
            is_mc = ipath.endswith("SIM")

            # Dummy
            xs = None
            # Construct row
            irow = (ipath, is_mc, xs, nevents, period)
            yield irow


class ExtractTarFile(luigi.Task):
    """Task that extracts a given tar file
    
    :param filepath: Path to the tar file.
    :type luigi: string
    """

    filepath = luigi.Parameter()

    def run(self):
        self.unpack_path = os.path.join(filepath, "untar")

        os.makedirs(unpack_path)
        tf = tarfile.open(filepath)
        tf.extract(path=unpack_path)
    
    def output(self):
        return luigi.LocalTarget(path=self.unpack_path)

class PrepareSkimFolder(luigi.Task):
    skim_folder = luigi.Parameter()

    def run(self):

        debug_folder = pjoin(skim_folder,"input")
        debug_file = pjoin(debug_folder,"debugFiles.tgz")

        tf = tarfile.open(debug_file)
        tf.extract(path=debug_file)

class RegisterSkimFolder(luigi.Task):
    skim_folder = luigi.Parameter()


class PerformSkim(luigi.Task):
    dataset = luigi.Parameter()
    
    def run(self):
        print(skim().cmssw_base)

if __name__ == '__main__':

    # task = InitializePeriod()

    # stub = "/ZJetsToNuNu_HT-100To200_13TeV-madgraph/*NanoAODv4*/NANOAODSIM"
    # task2 = InitializeDatasets(input_path=stub)

    # tasks = []

    task = ExtractTarFile(filepath="/disk1/albert/hinv_vbf/slc6/CMSSW_10_2_11/src/PhysicsTools/NanoAODTools/crab/wdir/19Mar19/crab_nano_post_19Mar19_SingleElectron_Run2017C/inputs/debugFiles.tgz")
    luigi.build([task], local_scheduler=True)