import os
import re
import shutil

import luigi

import law
from law.target.local import LocalFileTarget, LocalDirectoryTarget
from law.workflow.local import LocalWorkflow
from law.contrib.wlcg.util import check_voms_proxy_validity, get_voms_proxy_lifetime

from nanocppfw.htcondor.workflows import CernHTCondorWorkflow
from nanocppfw.pybindings import HInvAnalyzer
from nanocppfw.database.util import init_db_session
from nanocppfw.database.database_objects import Dataset

__all__ = ["AnalyzerTask","MultiDatasetAnalysisTask"]

class MkdirTask(law.Task):
    path = luigi.Parameter()

    def output(self):
        return LocalDirectoryTarget(self.path)

    def run(self):
        os.makedirs(self.path)


class AnalyzerTask(CernHTCondorWorkflow, LocalWorkflow):
    """Analysis task for a set of files."""

    version = luigi.Parameter()
    dryrun = luigi.BoolParameter(default=False, description="Do not do real analysis, just touch output files.")
    ncpu = luigi.IntParameter(default=1,description="The number of CPUs to run on.")

    def create_branch_map(self):
        return {1 : ["root://cms-xrd-global.cern.ch///store/mc/RunIIFall17NanoAODv4/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/007E0986-34E9-9741-A447-957FF2F1982C.root"],
        2:["root://cms-xrd-global.cern.ch///store/mc/RunIIFall17NanoAODv4/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/78341E3C-F2BD-A64E-95D6-550FCA8DDAD4.root"]
        }

    def requires(self):
        return MkdirTask(path=self.local_path())

    def run_dry(self):
        with open(self.output().path,"w") as f:
            for filepath in self.branch_data:
                f.write("{}\n".format(filepath))

    def run_real(self):
        if not check_voms_proxy_validity():
            raise RuntimeError("No VOMS proxy found. Please initialize!")
        if get_voms_proxy_lifetime() < 8*60*60:
            raise RuntimeError("VOMS proxy life time left should be longer than eight hours. Please renew!")

        files = self.branch_data
        ana = HInvAnalyzer(files)
        ana.set_fixed_dataset(self.dataset_name())

        # The output is first written into a temporary file
        tmp_name = "tmp.root"
        ana.set_output_path(tmp_name)
        ana.set_ncpu(self.ncpu)
        ana.run()

        # And then copied only once the analysis is complete
        shutil.copy2(tmp_name, self.output().path)

    def run(self):
        if self.dryrun:
            self.run_dry()
        else:
            self.run_real()

    def output(self):
        output_name = "HInvAnalyzer_{}_{}.root".format(self.dataset_name(), self.branch)
        return self.local_target(output_name)

    def local_path(self, *path):
        parts = (os.getenv("ANALYSIS_DATA_PATH"),) + self.store_parts() + path
        return os.path.join(*parts)

    def local_target(self, *path):
        return law.LocalFileTarget(self.local_path(*path))

    def store_parts(self):
        return (self.__class__.__name__,self.version)

    def dataset_name(self):
        return "dummy"

def chunks(iterable, chunksize):
    """Divides an iterable into chunks of a given size."""
    if not isinstance(chunksize, int):
        raise TypeError("Chunk size should be integer. Instead, found type: {}.".format(type(chunksize)))
    return [iterable[i:i + chunksize] for i in xrange(0, len(iterable), chunksize)]

class DatasetAnalysisTask(AnalyzerTask):
    """
    Analysis task for a single dataset and skim.

    Matching files are determined from the data base.
    """
    dataset = luigi.Parameter(description="Dataset path to analyze.")
    skim = luigi.Parameter("Skim to analyze.")
    files_per_branch = luigi.IntParameter(default=5)

    _dataset_object = None

    def create_branch_map(self):
        # Get files for skim
        files = filter(lambda x: x.skim_tag == self.skim, self.dataset_object().files)

        file_paths = [x.path for x in files]
        # Create dictionary
        branches = {}
        for counter, chunk in enumerate(chunks(file_paths, self.files_per_branch)):
            branches[counter] = chunk
        return branches

    def dataset_object(self):
        """Reads the Dataset object corresponding to the dataset of this task from the database"""
        if not self._dataset_object:
            # Get matching datasets
            session = init_db_session(os.environ["NANOCPPFW_DATABASE"])

            matching_datasets = session.query(Dataset) \
                    .filter(Dataset.path==self.dataset)

            matching_datasets = list(matching_datasets)
            nmatch = len(matching_datasets)
            if nmatch == 0:
                raise RuntimeError("No matching datasets found.")
            if nmatch > 1:
                raise RuntimeError("Too many matching datasets found.")

            self._dataset_object = matching_datasets[0]

        return self._dataset_object

    def dataset_name(self):
        return self.dataset_object().shortname

import subprocess
class HaddTask(law.Task):
    """Merges ROOT files using the 'hadd' function."""
    input_files = luigi.ListParameter()
    output_file = luigi.Parameter()

    def run(self):
        cmd = ["hadd", self.output_file] + list(self.input_files)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        stdout, _ = proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError("Could not run hadd command: {}.".format(" ".join(cmd)))

    def requires(self):
        return MkdirTask(path=os.path.dirname(self.output().path))
    def output(self):
        return LocalFileTarget(self.output_file)

class MultiDatasetAnalysisTask(law.Task):
    """
    Wrapper task to analyze multiple datasets.

    Each dataset is analyzed by a separate DatasetAnalysisTask,
    which is required by this task.
    """
    dataset_regex = luigi.Parameter()
    period_regex = luigi.Parameter()
    skim = luigi.Parameter()
    dryrun = luigi.BoolParameter()
    workflow = luigi.Parameter()
    version = luigi.Parameter()
    retries = luigi.IntParameter()

    def get_matching_datasets(self):
        """
        Query the data base to find datasets matching Task criteria

        Regular expression matching is performed using the 're.match'
        function.

        :raises RuntimeError: If no matching data sets are found
        :return: List of dataset paths
        :rtype: list of strings
        """
        session = init_db_session(os.environ["NANOCPPFW_DATABASE"])
        good_datasets = []
        for dataset in session.query(Dataset):
            # Period and dataset name must match
            match = re.match(self.period_regex, dataset.period_tag) \
                    and re.match(self.dataset_regex, dataset.path)
            if match:
                good_datasets.append(dataset.path)

        if not good_datasets:
            raise RuntimeError("No matching datasets found.")
        return good_datasets

    def run(self):
        merged_files = []
        for req in self.requires():
            root_files = []
            for target in req.output()["collection"].targets.values():
                root_files.append(target.path)
            merged_path = re.sub("_(\d+).root","_merged.root", root_files[0])
            yield HaddTask(input_files=root_files, output_file=merged_path)
            merged_files.append(merged_path)
        yield HaddTask(input_files=merged_files, output_file=self.output().path)


    def output(self):
        output_name = "HInvAnalyzer_merged.root"
        return self.local_target(output_name)

    def local_path(self, *path):
        # ANALYSIS_DATA_PATH is defined in setup.sh
        parts = (os.getenv("ANALYSIS_DATA_PATH"),) + self.store_parts() + path
        return os.path.join(*parts)

    def local_target(self, *path):
        return law.LocalFileTarget(self.local_path(*path))

    def store_parts(self):
        return (self.__class__.__name__,self.version)


    def requires(self):
        return (DatasetAnalysisTask(dataset=ds, skim=self.skim, version=self.version,dryrun=self.dryrun,workflow=self.workflow, retries=self.retries) for ds in self.get_matching_datasets())