#include "interface/Analyzer.h"
#include "include/Util.h"
#include "TObject.h"
using namespace std;

// Constructor
Analyzer::Analyzer(vector<TString> infiles) {
    this->files_ = infiles;
    variations_ = {"nominal","jesu","jesd"};
    ofpath_ = "./output.root";
}

// Overloaded constructor to handle std::strings
Analyzer::Analyzer(vector<string> infiles) : Analyzer(string_to_tstrings(infiles)) {
}

void Analyzer::set_output_path(string output_path) {
    this->ofpath_ = TString(output_path);
}

void Analyzer::analyze_chain_(){
    vector<string> strings;
    for(auto const tstring : this->files_) {
        strings.push_back(string(tstring.Data()));
    }
    auto rdf = ROOT::RDataFrame("Events", strings);

    for(auto variation : variations_) {
        this->histograms_[variation] = HVec1D();
        analyze_variation_(rdf, variation);
    }
    write_histograms_();
};

// Saves the histograms to file
void Analyzer::write_histograms_(){

    // The output structure is
    // ofile:/dataset/variation/histogram
    auto dataset_dir = ofile_->GetDirectory(this->dataset_);
    if( not dataset_dir ){
        dataset_dir = this->ofile_->mkdir(this->dataset_);
    }
    for(auto const variation : this->variations_) {
        auto variation_dir = dataset_dir->mkdir(variation);
        variation_dir->cd();
        for(auto histogram : this->histograms_[variation]){
            histogram->SetDirectory(variation_dir);
            histogram->Write();
        }
        variation_dir->Write();
        variation_dir->Close();
    }
    dataset_dir->Close();
}
void Analyzer::analyze_variation_(RNode rnode, TString variation) {
    HVec1D new_histos;
    new_histos.push_back(rnode.Histo1D<float>({"Jet_pt",        "Jet_pt",      100,    0,      1000},  "Jet_pt"));
    this->histograms_[variation] = new_histos;
}

void Analyzer::set_fixed_dataset(string dataset) {
    this->fixed_dataset_ = true;
    this->dataset_ = dataset;
    this->is_data_ = TString(dataset).Contains("Run201");
    cout << "Analyzer: Use fixed dataset '" << dataset << "'." << endl;
}

void Analyzer::run() {
    this->ofile_ = new TFile(ofpath_, "RECREATE");
    if(this->is_data_) {
        this->variations_ = {"nominal"};
    }
    this->analyze_chain_();
    this->ofile_->Close();
}
