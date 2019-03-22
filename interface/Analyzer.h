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
        void set_output_path(string output_path);
        void set_fixed_dataset(string dataset);
    protected:
        void analyze_chain_();
        virtual void analyze_variation_(RNode rnode, TString variation);
        void write_histograms_();

        map<TString, HVec1D> histograms_;
        vector<TString> files_;
        vector<TString> variations_;

        TString dataset_;
        TString ofpath_; // Path to output file
        TFile * ofile_; // Output TFile

        TDirectory * current_dir_;

        bool fixed_dataset_;
};
#endif // ANALYZER_H