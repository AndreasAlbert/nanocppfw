import os

import luigi

import law
from law.target.local import LocalFileTarget, LocalDirectoryTarget
from law.workflow.local import LocalWorkflow
from law.contrib.wlcg.util import check_voms_proxy_validity, get_voms_proxy_lifetime

from nanocppfw.htcondor.workflows import CernHTCondorWorkflow
from nanocppfw.pybindings import HInvAnalyzer

__all__ = ["ExampleAnalysisTask"]

class MkdirTask(luigi.Task):
    path = luigi.Parameter()

    def output(self):
        return LocalDirectoryTarget(self.path)
    
    def run(self):
        os.makedirs(self.path)


class ExampleAnalysisTask(CernHTCondorWorkflow, LocalWorkflow):

    version = luigi.Parameter()

    def create_branch_map(self):
        return {1 : ["root://cms-xrd-global.cern.ch///store/mc/RunIIFall17NanoAODv4/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/007E0986-34E9-9741-A447-957FF2F1982C.root"],
        2:["root://cms-xrd-global.cern.ch///store/mc/RunIIFall17NanoAODv4/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/78341E3C-F2BD-A64E-95D6-550FCA8DDAD4.root"]
        }

    def requires(self):
        return MkdirTask(self.local_path())

    def run(self):
        if not check_voms_proxy_validity():
            raise RuntimeError("No VOMS proxy found. Please initialize!")
        if get_voms_proxy_lifetime() < 8*60*60:
            raise RuntimeError("VOMS proxy life time left should be longer than eight hours. Please renew!")

        inputdata = self.branch_data
        ana = HInvAnalyzer(inputdata)
        ana.set_fixed_dataset("dummy")

        ana.set_output_path(self.output().path)
        ana.run()

    def output(self):
        output_name = "output_HInvAnalyzer_{}.root".format(self.branch)
        return self.local_target(output_name)

    def local_path(self, *path):
        # ANALYSIS_DATA_PATH is defined in setup.sh
        parts = (os.getenv("ANALYSIS_DATA_PATH"),) + self.store_parts() + path
        return os.path.join(*parts)

    def local_target(self, *path):
        return law.LocalFileTarget(self.local_path(*path))

    def store_parts(self):
        return (self.__class__.__name__,self.version)
