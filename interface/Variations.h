#ifndef VARIATIONS_H
#define VARIATIONS_H

#include <iostream>
#include<TFile.h>
#include<TTree.h>
#include<TTreeReader.h>
#include<TTreeReaderArray.h>
#include<TH1D.h>
#include <math.h>
#include <TROOT.h>
#include <ROOT/RDataFrame.hxx>
#include <set>
#include <algorithm>    // std::find

#include "RDFUtil.h"

/// Convenience definitions
using namespace ROOT::VecOps;
using doubles = RVec<double>;
using floats = RVec<float>;
using bools = RVec<Bool_t>;
using ints = RVec<int>;
using RDF = ROOT::RDataFrame;
using RNode = ROOT::RDF::RNode;
// using string = std::string;
// using vector = std::vector;
using namespace std;


RNode apply_variation(RNode rnode, string variation) {
    auto ret = rnode.Define("Muon_ptv","Muon_pt");
    ret = ret.Define("Electron_ptv","Electron_pt");
    ret = ret.Define("MET_ptv","MET_pt");

    if(variation == "nominal") {
        ret = ret.Define("Jet_ptv","1.0f*Jet_pt");
    } else if(variation == "jesup") {
        ret = ret.Define("Jet_ptv", "2.0f*Jet_pt");
    } else if(variation == "jesdown") {
        ret = ret.Define("Jet_ptv", "0.5f*Jet_pt");
    } else {
        throw std::invalid_argument("Encountered unknown variation: " + variation);
    }
    return ret;
}
#endif