import os
import luigi
import law

from law.target.local import LocalDirectoryTarget
from law.contrib.htcondor import HTCondorWorkflow
from law.contrib.wlcg.util import get_voms_proxy_file

from pytimeparse.timeparse import timeparse

class CernHTCondorWorkflow(HTCondorWorkflow):
    """
    Batch systems are typically very heterogeneous by design, and so is HTCondor. Law does not aim
    to "magically" adapt to all possible HTCondor setups which would certainly end in a mess.
    Therefore we have to configure the base HTCondor workflow in law.contrib.htcondor to work with
    the CERN HTCondor environment. In most cases, like in this example, only a minimal amount of
    configuration is required.
    """

    job_max_runtime = luigi.Parameter(default="1h", significant=False, description="Maximal "
        "job run time. May be any string parseable by pytimeparse.timeparse")
    job_request_cpus = luigi.Parameter(default="1", significant=False, description="Number "
        "of CPUs to request.")

    def htcondor_output_directory(self):
        # the directory where submission meta data should be stored
        return LocalDirectoryTarget(self.local_path())

    def htcondor_bootstrap_file(self):
        # each job can define a bootstrap file that is executed prior to the actual job
        # in order to setup software and environment variables
        return law.util.rel_path(__file__, "scripts/htcondor_cern_bootstrap.sh")

    def htcondor_job_config(self, config, job_num, branches):
        # render_data is rendered into all files sent with a job
        config.render_variables["nanocppfw_base"] = os.getenv("NANOCPPFW_BASE")

        # force to run on CC7, http://batchdocs.web.cern.ch/batchdocs/local/submit.html#os-choice
        config.custom_content.append(("requirements", "(OpSysAndVer =?= \"CentOS7\")"))

        # copy the entire environment
        config.custom_content.append(("getenv", "true"))

        # the CERN htcondor setup requires a "log" config, but we can safely set it to /dev/null
        # if you are interested in the logs of the batch system itself, set a meaningful value here
        config.custom_content.append(("log", "log.log "))

        # Job resources
        config.custom_content.append(("MaxRuntime", timeparse(self.job_max_runtime)))
        config.custom_content.append(("RequestCpus", self.job_request_cpus))

        # voms proxy file
        config.input_files.append(get_voms_proxy_file())

        return config
