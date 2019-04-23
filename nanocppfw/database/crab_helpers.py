import subprocess

def get_crab_files(crab_path):
    """Get a list of output files for a CRAB directory."""

    # CRAB does the heavy lifting
    cmd = ["crab", "out", "--dump","--xrootd", crab_path]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, _ = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError("Could not run CRAB command: {}.".format(" ".join(cmd)))

    paths = []
    for line in stdout.splitlines():
        paths.append(line.strip())

    return paths

