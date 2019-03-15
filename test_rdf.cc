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
#include "JetCleaning.h"
using doubles = ROOT::VecOps::RVec<double>;
using floats = ROOT::VecOps::RVec<float>;
using bools = ROOT::VecOps::RVec<Bool_t>;
using ints = ROOT::VecOps::RVec<int>;
using RDF = ROOT::RDataFrame;


void analyze(std::string const input_file){
    ROOT::RDataFrame rdf("Events", input_file, {"nElectron"});
    std::vector<ROOT::RDF::RResultPtr<TH1D>> histograms;


    histograms.push_back(rdf.Histo1D({"nElectron", "nElectron", 10, -0.5, 9.5},"nElectron"));
    histograms.push_back(rdf.Histo1D({"nJet", "nJet", 10, -0.5, 9.5},"nJet"));

    JetCleaner jclean(0.4);
    jclean.add_clean_against("Muon");
    jclean.add_clean_against("Electron");
    auto rdfclean = jclean.clean(rdf);
    // auto rdf2 = rdf.Define("CleanJet_indices", CleanJet_indices, {"Electron_phi","Electron_eta","Jet_phi","Jet_eta"})
    //                 .Define("CleanJet_pt",take_indices, {"Jet_pt", "CleanJet_indices"} )
    //                 .Define("CleanJet_phi",take_indices, {"Jet_phi", "CleanJet_indices"})
    //                 .Define("CleanJet_eta",take_indices, {"Jet_eta", "CleanJet_indices"});


    // histograms.push_back(rdf2.Histo1D({"Jet_pt", "Jet_pt", 100, 0, 1000},"Jet_pt"));
    // histograms.push_back(rdf2.Histo1D({"Jet_phi", "Jet_phi", 100, 0, 1000},"Jet_phi"));
    // histograms.push_back(rdf2.Histo1D({"Jet_eta", "Jet_eta", 100, 0, 1000},"Jet_eta"));
    // histograms.push_back(rdf2.Histo1D({"CleanJet_pt", "CleanJet_pt", 100, 0, 1000},"CleanJet_pt"));
    // histograms.push_back(rdf2.Histo1D({"CleanJet_phi", "CleanJet_phi", 100, 0, 1000},"CleanJet_phi"));
    // histograms.push_back(rdf2.Histo1D({"CleanJet_eta", "CleanJet_eta", 100, 0, 1000},"CleanJet_eta"));

    // // Write output to file
    // TFile tfile_out("out.root", "RECREATE");
    // for( auto &h : histograms ){
    //     h->Write();
    // }
    // tfile_out.Close();
    // auto r = rdf2.Display({"nElectron","nJet"},5);
    // std::cout << r->AsString() << std::endl;
    rdfclean.Snapshot("Events","snap.root",{
        "nElectron",
        "nJet", 
        "tmp_CleanJet_indices_Muon",
        "tmp_CleanJet_indices_Electron",
        "tmp_CleanJet_indices_intersect",
        "Electron_pt","Electron_eta","Electron_phi",
        "Jet_pt","Jet_eta","Jet_phi",
        "CleanJet_pt","CleanJet_eta","CleanJet_phi"
        });
}


int main(int argc, char *argv[]){
    gROOT->SetBatch(true);

    /// Get location of input file from command line
    if(argc != 2) {
        throw std::invalid_argument("Please provide exactly one input argument: The path to the input file.");
    }
    std::string input_file(argv[1]);

    /// Run the analysis
    analyze(input_file);

    return 0;
}