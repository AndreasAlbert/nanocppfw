#include "interface/HInvAnalyzer.h"
#include "include/JetSelection.h"
#include "include/LepSelection.h"
#include "include/Variations.h"


void book_histograms(RNode rnode,  HVec1D & histograms) {
    // Helper function, creates histogram and adds to vector
    auto easy_book_1d = [&histograms, &rnode](ROOT::RDF::TH1DModel const model, std::string_view vName) { 
        histograms.push_back(rnode.Histo1D(model,vName));
    };

    easy_book_1d({"nGoodElectron",      "nGoodElectron",    10,     -0.5,   9.5},   "nGoodElectron");
    easy_book_1d({"nGoodMuon",          "nGoodMuon",        10,     -0.5,   9.5},   "nGoodMuon");
    easy_book_1d({"nGoodJet",           "nGoodJet",         10,     -0.5,   9.5},   "nGoodJet");

    easy_book_1d({"GoodJet_ptv",        "GoodJet_ptv",      100,    0,      1000},  "GoodJet_ptv");
    easy_book_1d({"GoodElectron_ptv",   "GoodElectron_ptv", 10,     -0.5,   9.5},   "GoodElectron_ptv");
}

void HInvAnalyzer::analyze_variation_(RNode rnode, TString variation){
    rnode = apply_variation(rnode, variation);
    rnode = define_good_jets(rnode);
    rnode = define_good_electrons(rnode);
    rnode = define_good_muons(rnode);

    rnode = rnode.Define("selection","1 * ((nGoodJet>1) && (GoodJet_eta[0]*GoodJet_eta[1]) < 0 && (MET_ptv > 100) && (nGoodElectron+nGoodMuon==0))" \
    "+ 2 * ((nGoodElectron==1) && (MET_ptv > 50))" \
    "+ 4 * ((nGoodMuon==1) && (MET_ptv > 50))" \
    "+ 8 * (nGoodElectron==2)" \
    "+ 16 * (nGoodMuon==2)");

    rnode = rnode.Filter("selection > 0");

    HVec1D histos;
    book_histograms(rnode, histos);

    for(auto h : histos) {
        h->SetDirectory(current_dir_);
        histograms_.push_back(h);
    }
}
