#ifndef ANALYZER_H
#define ANALYZER_H

#include <vector>
#include <string>

#include<TFile.h>
#include<TDirectory.h>
#include <ROOT/RDataFrame.hxx>

using RNode = ROOT::RDF::RNode;
using namespace std;
using RDF = ROOT::RDataFrame;

typedef std::vector<ROOT::RDF::RResultPtr<TH1D>> HVec1D;

class Analyzer{
    public:
        Analyzer(vector<string> infiles);
        Analyzer(vector<TString> infiles);
        void run();
    protected:
        void analyze_file_(TString file);
        virtual void analyze_variation_(RNode rnode, TString variation);
        void finish_file_(TString file);
        void manage_dataset_(TString file);
        void switch_to_folder_(TString dataset, TString variation);
        void write_histograms_();

        HVec1D histograms_;
        vector<TString> files_;
        vector<TString> variations_;

        TString current_dataset_;
        TString ofpath_; // Path to output file
        TFile * ofile_; // Output TFile

        TDirectory * current_dir_;
};
#endif // ANALYZER_H