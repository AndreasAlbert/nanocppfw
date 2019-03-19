#include <math.h>

#include "interface/HInvAnalyzer.h"
#include "include/JetSelection.h"
#include "include/LepSelection.h"
#include "include/Variations.h"


void book_histograms(RNode rnode,  HVec1D & histograms) {
    // Loop over selections and create histograms for each selection type
    for(int isel = 0; isel < 5;isel++) {
        auto tag = "sel" + to_string(isel) + "_";

        // Helper function, creates histogram and adds to vector
        auto easy_book_1d = [&histograms, &tag](RNode rnode, TString name, int nbinsx, double xlow, double xup) {
            TString title = tag+name;
            auto model = ROOT::RDF::TH1DModel(title.Data(), title.Data(), nbinsx, xlow, xup);
            histograms.push_back(rnode.Histo1D(model, name.Data(), "vweight"));
        };

        int sel_power = pow(2, isel);
        auto sel_power_string = to_string(sel_power);
        auto sel_string = "(selection | " + sel_power_string + ")==" + sel_power_string;

        auto rsel = rnode.Filter(sel_string);

        //// Inclusive
        easy_book_1d(rsel, "nGoodElectron",10,     -0.5,   9.5 );
        easy_book_1d(rsel, "nGoodMuon",    10,     -0.5,   9.5 );
        easy_book_1d(rsel, "nGoodJet",     10,     -0.5,   9.5 );
        easy_book_1d(rsel, "MET_ptv",      100,    0,      1000 );

        //// At least one jet
        auto r1jet = rsel.Filter("nGoodJet>0");
        r1jet = r1jet.Define("jet0_pt","GoodJet_ptv[0]");
        r1jet = r1jet.Define("jet0_eta","GoodJet_eta[0]");
        r1jet = r1jet.Define("jet0_phi","GoodJet_phi[0]");

        easy_book_1d(r1jet, "jet0_pt",  100,    0,      1000 );
        easy_book_1d(r1jet, "jet0_phi", 50,     -M_PI,  M_PI );
        easy_book_1d(r1jet, "jet0_eta", 100,    -5,     5    );

        //// At least two jets
        auto r2jet = rsel.Filter("nGoodJet>1");
        r2jet = r2jet.Define("jet1_pt","GoodJet_ptv[1]");
        r2jet = r2jet.Define("jet1_eta","GoodJet_eta[1]");
        r2jet = r2jet.Define("jet1_phi","GoodJet_phi[1]");
        r2jet = r2jet.Define("jets_etaproduct","GoodJet_eta[0]*GoodJet_eta[1]");

        easy_book_1d(r2jet, "jet1_pt",             100,    0,      1000);
        easy_book_1d(r2jet, "jet1_phi",            50,     -M_PI,  M_PI);
        easy_book_1d(r2jet, "jet1_eta",            100,    -5,     5  );
        easy_book_1d(r2jet, "jets_etaproduct",     100,    -25,      25);
    }
}

void HInvAnalyzer::analyze_variation_(RNode rnode, TString variation){
    rnode = apply_variation(rnode, variation);
    rnode = define_good_jets(rnode);
    rnode = define_good_electrons(rnode);
    rnode = define_good_muons(rnode);

    rnode = rnode.Define("selection","1 * ((nGoodJet>1) && (GoodJet_eta[0]*GoodJet_eta[1]) < 0 && (MET_ptv > 100) && (nGoodElectron+nGoodMuon==0))" \
    "+ 2 * ((nGoodElectron==1) && (MET_ptv > 50))" \
    "+ 4 * ((nGoodMuon==1) && (MET_ptv > 50))" \
    "+ 8 * ((nGoodElectron==2) && (nGoodMuon==0))" \
    "+ 16 * ((nGoodElectron==0) && (nGoodMuon==2))");

    rnode = rnode.Filter("selection > 0");


    HVec1D histos;
    book_histograms(rnode, histos);

    for(auto h : histos) {
        h->SetDirectory(current_dir_);
        histograms_.push_back(h);
    }
}
