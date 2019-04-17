"""pypi package setup."""
from __future__ import print_function
import os
import codecs
from os import path
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import shlex, subprocess
try:
    import ROOT  # pylint: disable=W0611
except ImportError:
    print("ROOT is required by this library.")

DEPS = ["law", "pybind11"]

HERE = path.abspath(path.dirname(__file__))

with codecs.open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()


class get_pybind_include(object):
    """Helper class to determine the pybind11 include path

    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)



def get_root_compile_opts():
    """Determines ROOT-related options for gcc"""

    # Simply call root-config on the command line
    cmd = "root-config --cflags --glibs"
    proc = subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE)
    stdout, _ = proc.communicate()

    # And return stdout
    return stdout.strip()

ext_modules = [
    Extension(
        'nanocppfw',
        [
        #     'obj/Analyzer.o',
        # 'obj/HInvAnalyzer.o',
        # 'pybind/PyBindings.so',
        # 'src/Analyzer.cc',
        #  'src/HInvAnalyzer.cc',
         'src/PyBindings.cc'
        ],
        #  ['src/PyBindings.cc'],
        include_dirs=[
            # Path to pybind11 headers
            get_pybind_include(),
            get_pybind_include(user=True),
            ".",
        ],
        language='c++'
    ),
]


class BuildCPP(build_ext):
    """A custom build extension for adding compiler-specific options."""

    def build_extensions(self):
        opts = []
        opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
        opts.append("-std=c++11")
        # opts.append("`root-config --cflags --glibs`")
        opts.append("-I .")
        opts.append("-fPIC")
        opts.extend(shlex.split(get_root_compile_opts()))
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)
        # subprocess.call(["make","PyBindings"])

os.environ["CC"] = "g++"
setup(
    name='nanocppfw',
    version='0.0.1',
    description='',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/AndreasAlbert/nanocppfw',
    author='Andreas Albert',
    author_email='andreas.albert@cern.ch',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    keywords='NanoAOD',
    packages=find_packages(),
    zip_safe=False,
    install_requires=DEPS,
    # setup_requires=['pytest-runner', 'pytest-cov'],
    # tests_require=['pytest'],
    # CPP Code
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildCPP},
    project_urls={
        'Source': 'https://github.com/AndreasAlbert/nanocppfw',
    }, )


# g++ -c -o obj/Analyzer.o src/Analyzer.cc -I. -std=c++11 `root-config --cflags --glibs` -fPIC

# g++ -c -o obj/Analyzer.o src/Analyzer.cc -I. -std=c++11 -pthread -std=c++11 -m64 -I/home/albert/software/root/6.16.00/build_py2/include -L/home/albert/software/root/6.16.00/build_py2/lib -lGui -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lMultiProc -lROOTDataFrame -pthread -lm -ldl -rdynamic -fPIC


# g++ -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -fno-strict-aliasing -Wdate-time -D_FORTIFY_SOURCE=2 -g -fdebug-prefix-map=/build/python2.7-3hk45v/python2.7-2.7.15~rc1=. -fstack-protector-strong -Wformat -Werror=format-security -fPIC -I/home/albert/code/virtualenv/testenv/include/site/python2.7 -I/home/albert/code/virtualenv/testenv/include/site/python2.7 -I. -I/usr/include/python2.7 -c src/Analyzer.cc -o build/temp.linux-x86_64-2.7/src/Analyzer.o -DVERSION_INFO="0.0.1" -std=c++11 -pthread -std=c++11 -m64 -I/home/albert/software/root/6.16.00/build_py2/include -L/home/albert/software/root/6.16.00/build_py2/lib -lGui -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lMultiProc -lROOTDataFrame -pthread -lm -ldl -rdynamic -I . -fPIC
