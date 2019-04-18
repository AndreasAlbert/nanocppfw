import os
import luigi

import law
law.contrib.load("glite")
from law.contrib.glite import GLiteWorkflow
from law.contrib.wlcg import WLCGDirectoryTarget,WLCGFileTarget
from law.task.base import Task

from law.target.local import LocalFileTarget, LocalDirectoryTarget
from law.contrib.tasks import TransferLocalFile
from law.workflow.local import LocalWorkflow
from law.contrib.git import BundleGitRepository

from nanocppfw.pybindings import HInvAnalyzer
__all__ = ["ExampleAnalysisTask","NanoCPPFWUpload"]

class NanoCPPFWGLiteWorkflow(LocalWorkflow, GLiteWorkflow):

    def glite_bootstrap_file(self):
        return law.util.rel_path(__file__, "./scripts/grid_bootstrap.sh")

    def glite_output_directory(self):
        return WLCGDirectoryTarget(path="subfolder")

    def glite_output_uri(self):
        return self.glite_output_directory().url(cmd="listdir")

    def glite_workflow_requires(self):
        return {"software" : NanoCPPFWUpload(source_path="", replicas=1)}

    def _setup_render_variables(self, config, reqs):
        config.render_variables["GRIDPACK_NAME"] = self.glite_workflow_requires()["software"].single_output().path.replace("/","")
        config.render_variables["GRIDPACK_PATH"] = self.glite_workflow_requires()["software"].output().dir.url()

    def glite_job_config(self, config, job_num, branches):
        config = law.GLiteWorkflow.glite_job_config(self, config, job_num, branches)
        self._setup_render_variables(config, self.glite_workflow_requires())
        config.vo = "cms:/cms/dcms"
        return config

from datetime import datetime
class BundleGitRepositoryWithDateStamp(BundleGitRepository):
    def output(self):
        return LocalFileTarget("gridpacks/{}_{}_{}.tgz".format(os.path.basename(self.repo_path),
                                                     datetime.strftime(datetime.now(), '%y-%m-%d'),self.checksum))

class UploadSoftware(TransferLocalFile):

    version = None
    task_namespace = None

    def single_output(self):
        return WLCGFileTarget(os.path.basename(self.source_path))


class NanoCPPFWUpload(UploadSoftware):

    # def run(self):

    def requires(self):
        return BundleGitRepositoryWithDateStamp(repo_path=os.environ["NANOCPPFW_BASE"], exclude_files=["*.tgz","data"])
    def single_output(self):
        return WLCGFileTarget(os.path.basename(self.requires().output().path))


class ExampleAnalysisTask(NanoCPPFWGLiteWorkflow):

    def create_branch_map(self):
        return {1 : ["root://cms-xrd-global.cern.ch///store/mc/RunIIFall17NanoAODv4/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/007E0986-34E9-9741-A447-957FF2F1982C.root"],
        # 2:["root://cms-xrd-global.cern.ch///store/mc/RunIIFall17NanoAODv4/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/78341E3C-F2BD-A64E-95D6-550FCA8DDAD4.root"]
        }

    def run(self):
        inputdata = self.branch_data
        ana = HInvAnalyzer(inputdata)
        ana.set_fixed_dataset("dummy")
        ana.set_output_path(self.output().path)
        ana.run()

    def output(self):
        output_name = "output_HInvAnalyzer_{}.root".format(self.branch)
        return WLCGFileTarget(output_name)

