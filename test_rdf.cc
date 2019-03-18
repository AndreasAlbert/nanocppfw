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

#include "interface/JetSelection.h"
#include "interface/LepSelection.h"

using doubles = ROOT::VecOps::RVec<double>;
using floats = ROOT::VecOps::RVec<float>;
using bools = ROOT::VecOps::RVec<Bool_t>;
using ints = ROOT::VecOps::RVec<int>;
using RDF = ROOT::RDataFrame;

void analyze(std::string const input_file){
    ROOT::RDataFrame rdf("Events", input_file);
    string dataset = "some_dataset";
    TFile output_file("outfile.root","RECREATE");
    auto dataset_dir = output_file.mkdir(dataset.data());

    vector<string> variations = {"nominal","jesup","jesdown"};
    for( auto const variation : variations ) {
        std::vector<ROOT::RDF::RResultPtr<TH1D>> histograms;
        auto output_dir = dataset_dir->mkdir(variation.data());
        output_dir->cd();

        auto rnode = apply_variation(rdf, variation);

        rnode = define_good_jets(rnode);
        rnode = define_good_electrons(rnode);
        rnode = define_good_muons(rnode);

        rnode = rnode.Define("selection","1 * ((nGoodJet>1) && (GoodJet_eta[0]*GoodJet_eta[1]) < 0 && (MET_ptv > 100) && (nGoodElectron+nGoodMuon==0))" \
        "+ 2 * ((nGoodElectron==1) && (MET_ptv > 50))" \
        "+ 4 * ((nGoodMuon==1) && (MET_ptv > 50))" \
        "+ 8 * (nGoodElectron==2)" \
        "+ 16 * (nGoodMuon==2)");

        // rnode = rnode.Filter("selection > 0");
        
        histograms.push_back(rnode.Histo1D({"nGoodElectron", "nGoodElectron", 10, -0.5, 9.5},"nGoodElectron"));
        histograms.push_back(rnode.Histo1D({"nGoodMuon", "nGoodMuon", 10, -0.5, 9.5},"nGoodMuon"));
        histograms.push_back(rnode.Histo1D({"nGoodJet", "nGoodJet", 10, -0.5, 9.5},"nGoodJet"));
        histograms.push_back(rnode.Histo1D({ (variation + "GoodJet_ptv").data(), (variation + "GoodJet_ptv").data(), 100, 0, 1000},"GoodJet_ptv"));
        histograms.push_back(rnode.Histo1D({ (variation + "Jet_ptv").data(), (variation + "Jet_ptv").data(), 100, 0, 1000},"Jet_ptv"));
        histograms.push_back(rnode.Histo1D({"GoodElectron_ptv", "GoodElectron_ptv", 10, -0.5, 9.5},"GoodElectron_ptv"));
        // rnode.Snapshot("Events","snap"+variation+".root",{"nJet","Jet_ptv","Jet_pt"});


        for(auto h : histograms) {
            h->Write();
        }
        histograms.clear();
        output_dir->Close();
        output_file.cd();
    }
}


int main(int argc, char *argv[]){
    ROOT::EnableImplicitMT(4);
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

    // jclean.add_clean_against("Muon");
    // jclean.add_clean_against("Electron");
    // auto rdfclean = jclean.clean(rdf);

    // vector<string> jet_properties = {"_pt","_phi","_eta"};
    // for( auto const prop : jet_properties ){}
    //     rdf = rdf.Define

  


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

        // rnode.Snapshot("Events","snap.root",{
        //     "selection",
        //     "nElectron",
        //     "nMuon",
        //     "nJet", 
        //     "nGoodJet", 
        //     // "tmp_CleanJet_indices_Muon",
        //     // "tmp_CleanJet_indices_Electron",
        //     // "tmp_CleanJet_indices_intersect",
        //     "Electron_pt","Electron_eta","Electron_phi",
        //     "Muon_pt","Muon_eta","Muon_phi",
        //     "Jet_pt","Jet_eta","Jet_phi",
        //     "GoodJet_pt","GoodJet_eta","GoodJet_phi"
        //     });

        // rnode.Report()->Print();


