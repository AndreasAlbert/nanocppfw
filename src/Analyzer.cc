#include "interface/Analyzer.h"
#include "include/Util.h"
#include "TObject.h"
using namespace std;
Analyzer::Analyzer(vector<TString> infiles) {
    files_ = infiles;
    variations_ = {"nominal","jesu","jesd"};
    ofpath_ = "./output.root";
}

void Analyzer::analyze_file_(TString file){
    manage_dataset_(file);
    rdf_ = new ROOT::RDataFrame("Events", file.Data());

    for(auto variation : variations_) {
        analyze_variation_(variation);
        write_histograms_();
        histograms_.clear();
    }

    finish_file_(file);
};

void Analyzer::write_histograms_(){
    for( auto h : histograms_ ) {
            auto dir = h->GetDirectory();
            auto name = h->GetName();

            auto existing_key = dir->GetKey(name);
            if(existing_key){
                h->Add((TH1D*)existing_key->ReadObj());
            }

            h->Write(name, TObject::kOverwrite);
    }
}
void Analyzer::analyze_variation_(TString variation){
    HVec1D new_histos;
    switch_to_folder_(current_dataset_, variation);
    new_histos.push_back(rdf_->Histo1D({"Jet_pt",        "Jet_pt",      100,    0,      1000},  "Jet_pt"));
    for(auto h : new_histos) {
        h->SetDirectory(current_dir_);
        histograms_.push_back(h);
    }
}

void Analyzer::finish_file_(TString file){

}

void Analyzer::manage_dataset_(TString file){
    // TODO: Deduce dataset name
    TString dataset;
    if(file.Contains("E4D76467") or file.Contains("007E0986")) {
        dataset = "dataset1";
    } else {
        dataset = "dataset2";
    }

    if(current_dataset_.CompareTo(dataset)==0) {
        // Already have correct dataset, nothing to do
        return;
    } else {
        current_dataset_ = dataset;
    }
}
void Analyzer::switch_to_folder_(TString dataset, TString variation) {
    auto dataset_dir = ofile_->GetDirectory(dataset);
    if(not dataset_dir) {
        dataset_dir = ofile_->mkdir(dataset);
    }

    auto variation_dir = dataset_dir->GetDirectory(variation);
    if( not variation_dir ){
        variation_dir = dataset_dir->mkdir(variation);
    }
    variation_dir->cd();
    current_dir_= variation_dir;
    current_dir_->cd();
}


void Analyzer::run() {
    ofile_ = new TFile(ofpath_, "RECREATE");
    for(auto const file : files_) {
        analyze_file_(file);
    }
    ofile_->Close();
}