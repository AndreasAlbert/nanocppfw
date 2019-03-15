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
using string = std::string;


ints CleanJet_indices(floats &ele_phi, floats &ele_eta, floats &jet_phi, floats &jet_eta ){
    /// If there are no leptons, all jet indices are good
    if(ele_phi.size()==0) {
        ints ret;
        for(int i = 0; i < jet_phi.size(); i++){
            ret.push_back(i);
        }
        return ret;
    }

    /// Check all combinations
    auto indices = Combinations(ele_phi,jet_phi);
    
    /// Calculate distance
    auto dphi = Take(ele_phi, indices[0]) - Take(jet_phi, indices[1]);
    auto deta = Take(ele_eta, indices[0]) - Take(jet_eta, indices[1]);
    auto dr = sqrt(dphi * dphi + deta * deta);

    /// Return unique list of good indices
    auto CleanJet_indices = UniqueItems(indices[1][dr>0.4]);
    
    return CleanJet_indices;
};

// struct PartInfoNames {
//     public:
//         string const tag;
//         string const pt_name;
//         string const eta_name;
//         string const phi_name;
//         PartInfoNames(string itag, string ipt_name, string ieta_name, string iphi_name) :
//         tag(itag),
//         pt_name(ipt_name),
//         eta_name(ieta_name),
//         phi_name(iphi_name)
//         {}
// };

class JetCleaner{
    public:
        JetCleaner(float delta_R_min) :
        delta_R_min_(delta_R_min)
        {
            jet_collection_ = "Jet";
        }

        RNode clean(RNode rdf){
            auto cleaned_rdf = rdf;
            std::vector<string> var_names;

            // Derive non-overlapping jet indices individually
            // for each of the collections to clean against.
            for( string const collection : clean_against_ ) {
                string name = "tmp_CleanJet_indices_" + collection;
                var_names.push_back(name);
                cleaned_rdf = cleaned_rdf.Define(name,
                            CleanJet_indices,
                            {
                                collection + "_phi", 
                                collection + "_eta", 
                                jet_collection_ + "_phi", 
                                jet_collection_ + "_eta", 
                            }
                            );
            }
            int n_collections = var_names.size();
            if(n_collections == 0) {
                cleaned_rdf = cleaned_rdf.Alias("CleanJet_pt", "Jet_pt");
                cleaned_rdf = cleaned_rdf.Alias("CleanJet_phi", "Jet_phi");
                cleaned_rdf = cleaned_rdf.Alias("CleanJet_eta", "Jet_eta");
                return cleaned_rdf;
            } else {
                cleaned_rdf = cleaned_rdf.Alias("tmp_CleanJet_indices_intersect", var_names.at(0));
                for( auto const name : var_names){
                    cleaned_rdf = cleaned_rdf.Define("tmp_CleanJet_indices_intersect", rdf_intersect_i, {"tmp_CleanJet_indices_intersect", name});
                }
            }
            // The intersection of the individuals
            cleaned_rdf = cleaned_rdf.Define("tmp_CleanJet_indices_intersect", rdf_intersect_i, var_names);
            cleaned_rdf = cleaned_rdf.Define("CleanJet_pt",rdf_take_f, {jet_collection_ + "_pt", "tmp_CleanJet_indices_intersect"} );
            cleaned_rdf = cleaned_rdf.Define("CleanJet_phi",rdf_take_f, {jet_collection_ + "_phi", "tmp_CleanJet_indices_intersect"});
            cleaned_rdf = cleaned_rdf.Define("CleanJet_eta",rdf_take_f, {jet_collection_ + "_eta", "tmp_CleanJet_indices_intersect"});
            cleaned_rdf = cleaned_rdf.Define("nCleanjet",rdf_count_f, {"CleanJet_pt"});

            return cleaned_rdf;
        }
        void set_jet_collection(string jet_collection) {
            jet_collection_ = jet_collection;
        }
        void add_clean_against(string collection){
            clean_against_.push_back(collection);
        }
    private:
        float const delta_R_min_;
        std::vector<string> clean_against_;
        string jet_collection_;
};