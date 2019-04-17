import os


import law
law.contrib.load("glite")
from law.contrib.glite import GLiteWorkflow
from law.contrib.wlcg import WLCGDirectoryTarget,WLCGFileTarget
from law.task.base import Task

from law.target.local import LocalFileTarget, LocalDirectoryTarget
from law.contrib.tasks import TransferLocalFile
from law.workflow.local import LocalWorkflow
from law.contrib.git import BundleGitRepository

__all__ = ["ExampleAnalysisTask","CustomBundleGitRepository"]

class AnalysisBaseTask(LocalWorkflow, GLiteWorkflow):
    

    def output(self):
        return WLCGFileTarget("output_{}.txt".format(self.branch))

    def glite_bootstrap_file(self):
        return law.util.rel_path(__file__, "../scripts/grid_bootstrap.sh")

    def glite_output_directory(self):
        return WLCGDirectoryTarget(path="subfolder")

    def glite_output_uri(self):
        return self.glite_output_directory().url(cmd="listdir")
        # return self.glite_output_directory()

    def glite_job_config(self, config, job_num, branches):
        config = law.GLiteWorkflow.glite_job_config(self, config, job_num, branches)
        config.vo = "cms:/cms/dcms"
        return config

    def glite_workflow_requires(self):
        reqs = {}
        reqs["bundle"] = BundleGitRepository.req(self,repo_path=os.environ["NANOCPPFW_BASE"], exclude_files=["*.tgz","data"])
        reqs["software"] = UploadSoftware.req(self, source_path=reqs["bundle"].output().path,replicas=5, _prefer_cli=["replicas"])
        return reqs

import luigi
from law import Task, LocalFileTarget, CSVParameter, NO_STR
from datetime import datetime
class CustomBundleGitRepository(BundleGitRepository):
    # repo_path = luigi.Parameter(description="the path to the repository to bundle")
    # exclude_files = CSVParameter(default=[], description="patterns of files to exclude")
    # include_files = CSVParameter(default=[], description="patterns of files to force-include, "
    #     "takes precedence over .gitignore")
    # custom_checksum = luigi.Parameter(default=NO_STR, description="a custom checksum to use")

    # def __init__(self, *args, **kwargs):
    #     super(CustomBundleGitRepository, self).__init__(*args, **kwargs)

    # @property
    # def checksum(self):
    #     super(CustomBundleGitRepository,self).checksum()
    #     cs = "{}-{}-{}_{}".format(datetime.now().year(),
    #                               datetime.now().month(),
    #                               datetime.now().day(),
    #                               self._checksum)
    #     self._checksum = cs
    #     print cs
    #     return cs
    def output(self):
        return LocalFileTarget("gridpacks/{}_{}_{}.tgz".format(os.path.basename(self.repo_path),
                                                     datetime.strftime(datetime.now(), '%y-%m-%d'),self.checksum))

class UploadSoftware(TransferLocalFile):

    version = None
    task_namespace = None

    def single_output(self):
        return WLCGFileTarget(os.path.basename(self.source_path))


class ExampleAnalysisTask(AnalysisBaseTask):
    def create_branch_map(self):
        return {1 : "abc", 2:"def"}

    def run(self):
        inputdata = self.branch_data

        outputdata = 3 * inputdata

        output = self.output()
        output.parent.touch()

        output.dump({"input":inputdata, "output":outputdata})
