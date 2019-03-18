#ifndef LEPSELECTION_H
#define LEPSELECTION_H

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
// using Take = );

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

RNode define_good_electrons(RNode rdf) {
    vector<string> properties = {"_ptv","_phi","_eta"};
    for( auto const prop : properties ){
        string selection = "Electron"+prop+"[(Electron_cutBased==3) && (Electron_eta < 2.5) && (Electron_ptv > 20)]";
        rdf = rdf.Define("GoodElectron" + prop, selection);
    }
    rdf = rdf.Define("nGoodElectron",rdf_count_f, {"GoodElectron_ptv"});
    return rdf;
}
RNode define_good_muons(RNode rdf) {
    vector<string> properties = {"_ptv","_phi","_eta"};
    for( auto const prop : properties ){
        string selection = "Muon"+prop+"[(Muon_mediumId==1) && (Muon_eta < 2.5) && (Muon_ptv > 20)]";
        rdf = rdf.Define("GoodMuon" + prop, selection);
    }
    rdf = rdf.Define("nGoodMuon",rdf_count_f, {"GoodMuon_ptv"});
    return rdf;
}

#endif