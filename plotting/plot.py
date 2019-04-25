#!/usr/bin/env python

import ROOT as r
from nanocppfw.root.histogram_tools import sum_of_histograms
from nanocppfw.database.util import DatabaseInterface
import argparse
import logging
from collections import namedtuple
import os
import re
log = logging.getLogger("plotting")

r.gROOT.SetBatch(r.kTRUE)

def parse_cli():
    parser = argparse.ArgumentParser(description='Runs Analysis')

    general_args = parser.add_argument_group("General")
    general_args.add_argument('--debug', default="INFO", type=str, choices=logging._levelNames.keys(),
                              help='Debug level.')

    input_args = parser.add_argument_group("Inputs")
    input_args.add_argument('input_file', default=None, type=str,
                            help='Input file to read histograms from.')
    input_args.add_argument('--plot-filter-plot', default=None, type=str,
                            help='Regular expression to select plots by name.')
    input_args.add_argument('--plot-filter-variation', default=None, type=str,
                            help='Regular expression to select plots by variation.')

    # plot_args = parser.add_argument_group("Plot")
    DatabaseInterface.add_cli_parsing(parser)

    args = parser.parse_args()

    # Logger
    format = '%(levelname)s (%(name)s) [%(asctime)s]: %(message)s'
    date = '%F %H:%M:%S'
    logging.basicConfig(
        level=logging._levelNames[args.debug], format=format, datefmt=date)

    return args


HistWrap = namedtuple("HistWrap", [
    "name",
    "histogram",
    "is_mc",
    "is_signal"
])


class PlotInputs(object):
    def __init__(self,histogram_dict={}):
        self.data_histograms = []
        self.data_stack = None
        self.data_sum = None
        self.mc_histograms = []
        self.mc_stack = None
        self.mc_sum = None
        if histogram_dict:
            self.init_from_dict(histogram_dict)

    def _make_stacks(self, mc=None):
        if mc is None:
            self._make_stacks(True)
            self._make_stacks(False)
            return

        stack = r.THStack()
        for hwrap in self.mc_histograms if mc else self.data_histograms:
            stack.Add(hwrap.histogram,"HIST")

        if mc:
            self.mc_stack = stack
        else:
            self.data_stack = stack

    def _make_sums(self, mc=None):
        if mc is None:
            self._make_sums(True)
            self._make_sums(False)
            return
        
        if mc:
            histograms_to_sum = [hwrap.histogram for hwrap in self.mc_histograms if not hwrap.is_signal]
            self.mc_sum = sum_of_histograms(histograms_to_sum)
        else:
            histograms_to_sum = [hwrap.histogram for hwrap in self.data_histograms]
            self.data_sum = sum_of_histograms(histograms_to_sum)

    def init_from_dict(self, histogram_dict):
        """Reads histograms from dictionary

        The histogram should have this structure:
            key = Name of histogram
            value = ROOT histogram object

        :param histogram_dict: dictionary of input histograms
        :type histogram_dict: dict
        """
        for name, histogram in histogram_dict.items():
            hwrap = HistWrap(name=name, histogram=histogram,
                     is_mc="Run20" in name, is_signal=False)
            if hwrap.is_mc:
                self.mc_histograms.append(hwrap)
            else:
                self.data_histograms.append(hwrap)

        self._make_stacks()
        self._make_sums()


class Plotter(DatabaseInterface):
    def __init__(self, path_to_file, **kwargs):
        self._path_to_file = path_to_file
        self._tfile = r.TFile(self._path_to_file)

        self._filter_plot = kwargs.pop("filter_plot", self.default_filter())
        self._filter_variation = kwargs.pop(
            "filter_variation", self.default_filter())

        # Keep track of what inputs are available in the file
        self._available_plots = set()
        self._available_variations = set()
        self._available_plots = set()
        self._initialize_available_inputs()

        super(Plotter, self).__init__(**kwargs)

    def _initialize_available_inputs(self):
        available_plots = set()
        available_variations = set()
        available_datasets = set()
        # Loop over datasets, variations, plots
        for dataset_dir_key in self._tfile.GetListOfKeys():
            available_datasets.add(dataset_dir_key.GetName())
            for variation_dir_key in dataset_dir_key.ReadObj().GetListOfKeys():
                available_variations.add(variation_dir_key.GetName())
                for plot_key in variation_dir_key.ReadObj().GetListOfKeys():
                    available_plots.add(plot_key.GetName())
        self._available_plots = available_plots
        self._available_variations = available_variations
        self._available_datasets = available_datasets

    def _initialize_filtered_plots(self):
        self._filtered_plots = filter(lambda plot: re.match(
            self._filter_plot, plot), self._available_plots)

    def _get_single_plot(self, dataset, variation, plot):
        path_in_tfile = str(os.path.join(dataset.shortname, variation, plot))
        histogram_in_file = self._tfile.Get(path_in_tfile)
        if not histogram_in_file:
            return None
        # histogram = histogram_in_file.Clone()
        # histogram.SetDirectory(0)
        # histogram.SetName("_".join([dataset.shortname, histogram.GetName(), variation]))
        return histogram_in_file

    def _get_plot_inputs(self, wanted_datasets, variation, plot):
        histograms = {}
        for dataset in wanted_datasets:
            histogram = self._get_single_plot(dataset, variation, plot)
            if not histogram:
                continue
            histograms[dataset.shortname] = histogram
        return PlotInputs(histogram_dict=histograms)

    def do_plot(self):
        wanted_plots = filter(lambda plot: re.match(
            self._filter_plot, plot), self._available_plots)
        wanted_variations = filter(lambda var: re.match(
            self._filter_variation, var), self._available_variations)
        wanted_datasets = self.get_datasets()

        # Remove missing datasets and issue warning
        for ds in reversed(wanted_datasets):
            if ds.shortname not in self._available_datasets:
                log.warning(
                    "Dataset '{}' not available in input file.".format(ds.shortname))
                wanted_datasets.remove(ds)

        # Plotting
        c1 = r.TCanvas()
        c1.SetLogy()
        outdir = "./plotting/output"
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        for plot in wanted_plots:
            for variation in wanted_variations:
                pinp = self._get_plot_inputs(wanted_datasets, variation, plot)

                leg = r.TLegend()
                
                # pinp.mc_stack.Draw("")
                pinp.mc_sum.Draw("HIST")
                pinp.data_sum.Draw("PE,SAME")

                pinp.data_sum.SetMarkerStyle(20)
                pinp.data_sum.SetMarkerSize(0.5)
                # pinp.data_stack.Draw("")
                leg.Draw()
                c1.SaveAs(os.path.join(
                    outdir, "{}_{}.pdf".format(plot, variation)))


def main():
    args = parse_cli()
    plotter = Plotter(args.input_file, filter_plot=args.plot_filter_plot,
                      filter_variation=args.plot_filter_variation, args=args)
    plotter.do_plot()


if __name__ == "__main__":
    main()
