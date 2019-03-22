#ifndef VARIATIONS_H
#define VARIATIONS_H

#include <iostream>
#include<TFile.h>
#include<TTree.h>
#include<TTreeReader.h>
#include<TTreeReaderArray.h>
#include<TH1D.h>
#include<TString.h>
#include <math.h>
#include <TROOT.h>
#include <ROOT/RDataFrame.hxx>
#include <set>
#include <algorithm>    // std::find

#include "RDFUtil.h"

/// Convenience definitions
using RNode = ROOT::RDF::RNode;
using namespace std;

// Defines custom columns for a given variation
// By defining a given column in a variation-dependent way,
// the variations are separated from the analysis code
RNode apply_variation(RNode rnode, TString variation) {
    /// Variable variations
    auto ret = rnode.Define("Muon_ptv","Muon_pt");
    ret = ret.Define("Electron_ptv","Electron_pt");
    ret = ret.Define("MET_ptv","MET_pt");
    if(variation == "nominal") {
        ret = ret.Define("Jet_ptv","1.0f*Jet_pt");
    } else if(variation == "jesu") {
        ret = ret.Define("Jet_ptv", "2.0f*Jet_pt");
    } else if(variation == "jesd") {
        ret = ret.Define("Jet_ptv", "0.5f*Jet_pt");
    } else {
        string error = ("Encountered unknown variation: " + variation).Data();
        throw invalid_argument(error);
    }

    return ret;
}
#endif