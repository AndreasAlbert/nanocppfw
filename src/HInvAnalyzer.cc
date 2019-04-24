#include <math.h>

#include "interface/HInvAnalyzer.h"
#include "interface/SelectionManager.h"

#include "include/JetSelection.h"
#include "include/LepSelection.h"
#include "include/Variations.h"

#include "include/RDFUtil.h"

HInvAnalyzer::HInvAnalyzer(vector<string> infiles) : Analyzer::Analyzer(infiles) {
    this->selection_manager_ = this->initialize_selections_();
}

SelectionManager HInvAnalyzer::initialize_selections_() {
    SelectionManager sman;

    // Inclusive
    sman.add_selection(Selection("INCLUSIVE","true", false));

    // Signal
    sman.add_selection(Selection("SR_VBF","(nGoodJet>1) && (GoodJet_eta[0]*GoodJet_eta[1]) < 0 && (MET_ptv > 100) && (nGoodElectron+nGoodMuon==0)", true));

    // CR: single lep
    sman.add_selection(Selection("CR_W_EL","HLT_Ele32_WPTight_Gsf && (nGoodElectron==1) && (MET_ptv > 50) && (GoodElectron_ptv[0] > 35)", false));
    sman.add_selection(Selection("CR_W_MU","HLT_IsoMu27 && (nGoodMuon==1) && (MET_ptv > 50) && (GoodMuon_ptv[0] > 35)", false));

    // CR: dilep
    sman.add_selection(Selection("CR_Z_EL","HLT_Ele32_WPTight_Gsf && (nGoodElectron==2) && (nGoodMuon==0) && (GoodElectron_ptv[0] > 35)", false));
    sman.add_selection(Selection("CR_Z_MU","HLT_IsoMu27 && (HLT_IsoMu27) && (nGoodElectron==0) && (nGoodMuon==2) && (GoodMuon_ptv[0] > 35)", false));

    return sman;
}
void HInvAnalyzer::book_histograms(RNode rnode,  HVec1D & histograms) {
    // Loop over selections and create histograms for each selection type
    for(int isel = 0; isel < 5;isel++) {
        auto tag = this->selection_manager_.get_selection_tag(isel);

        // Helper function, creates histogram and adds to vector
        auto easy_book_1d = [&histograms, &tag](RNode rnode, TString name, int nbinsx, double xlow, double xup) {
            TString title = tag+"_"+name;
            auto model = ROOT::RDF::TH1DModel(title.Data(), title.Data(), nbinsx, xlow, xup);
            histograms.push_back(rnode.Histo1D<float>(model, name.Data(), "vweight"));
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

        //// At least one muon
        auto r1mu = rsel.Filter("nGoodMuon>0");
        r1mu = r1mu.Define("mu0_pt", "GoodMuon_ptv[0]");
        r1mu = r1mu.Define("mu0_eta", "GoodMuon_eta[0]");
        r1mu = r1mu.Define("mu0_phi", "GoodMuon_phi[0]");

        easy_book_1d(r1mu, "mu0_pt",             100,    0,      1000);
        easy_book_1d(r1mu, "mu0_phi",            50,     -M_PI,  M_PI);
        easy_book_1d(r1mu, "mu0_eta",            100,    -5,     5  );

        //// At least one electron
        auto r1el = rsel.Filter("nGoodElectron>0");
        r1el = r1el.Define("el0_pt", "GoodElectron_ptv[0]");
        r1el = r1el.Define("el0_eta", "GoodElectron_eta[0]");
        r1el = r1el.Define("el0_phi", "GoodElectron_phi[0]");

        easy_book_1d(r1el, "el0_pt",             100,    0,      1000);
        easy_book_1d(r1el, "el0_phi",            50,     -M_PI,  M_PI);
        easy_book_1d(r1el, "el0_eta",            100,    -5,     5  );

        //// Two muons
        auto r2mu = rsel.Filter("nGoodMuon==2");
        r2mu = r2mu.Define("mu1_pt", "GoodMuon_ptv[1]");
        r2mu = r2mu.Define("mu1_eta", "GoodMuon_eta[1]");
        r2mu = r2mu.Define("mu1_phi", "GoodMuon_phi[1]");
        r2mu = r2mu.Define("dimuon_mass", inv_mass_leading_two, {"GoodMuon_ptv","GoodMuon_eta","GoodMuon_phi"} );

        easy_book_1d(r2mu, "mu1_pt",             100,    0,      1000);
        easy_book_1d(r2mu, "mu1_phi",            50,     -M_PI,  M_PI);
        easy_book_1d(r2mu, "mu1_eta",            100,    -5,     5  );
        easy_book_1d(r2mu, "dimuon_mass",            100,    50, 150  );

        //// Two electrons
        auto r2el = rsel.Filter("nGoodElectron==2");
        r2el = r2el.Define("el1_pt", "GoodElectron_ptv[1]");
        r2el = r2el.Define("el1_eta", "GoodElectron_eta[1]");
        r2el = r2el.Define("el1_phi", "GoodElectron_phi[1]");
        r2el = r2el.Define("dielectron_mass", inv_mass_leading_two, {"GoodElectron_ptv","GoodElectron_eta","GoodElectron_phi"} );

        easy_book_1d(r2el, "el1_pt",             100,    0,      1000);
        easy_book_1d(r2el, "el1_phi",            50,     -M_PI,  M_PI);
        easy_book_1d(r2el, "el1_eta",            100,    -5,     5  );
        easy_book_1d(r2el, "dielectron_mass",            100,    50, 150  );


    }
}

void HInvAnalyzer::analyze_variation_(RNode rnode, TString variation){
    cout << "Analyzing variation: " << variation << endl;

    // Define varied variables
    rnode = apply_variation(rnode, variation);

    // Object selection
    rnode = define_good_jets(rnode);
    rnode = define_good_electrons(rnode);
    rnode = define_good_muons(rnode);

    // Event selection
    selection_manager_.set_blind(this->is_data_);
    rnode = selection_manager_.select(rnode);

    if(this->is_data_) {
        rnode = rnode.Define("vweight","1");
    } else {
        rnode = rnode.Define("vweight","genWeight");
    }


    // Create histograms
    HVec1D histos;
    book_histograms(rnode, histos);
    this->histograms_[variation] = histos;
}
