#ifndef SELECTIONMANAGER_H
#define SELECTIONMANAGER_H

#include <vector>
#include <string>
#include <TString.h>
#include <ROOT/RDataFrame.hxx>

using RNode = ROOT::RDF::RNode;
using namespace std;


//// Wrapper for a single defined selection
// The selection has a defining string, e.g:
//      "(pt_jet > 5) && (pt_mu < 5)"
// Additionally, a selection stage can be blind or not
// Blinded selection stages can selectively not be filled
struct Selection {
    TString tag;
    TString selection_string;
    bool blind;

    // Default constructor
    Selection() {
        this->tag = "";
        this->selection_string = "";
        this->blind = false;
    }

    // Constructor for combination of selections
    Selection(vector<Selection> selections) : Selection("","",false) {
        for(auto const sel : selections){
            *this+= sel;
        }
    }

    // Constructor for combination of selections with custom tag
    Selection(TString tag, vector<Selection> selections, bool blind) : Selection(selections){
        this->tag = tag;
        this->blind = blind;
    }

    // Constructor for fully manual definition
    Selection(TString tag, TString istring, bool blind) {
        this->tag = tag;
        this->selection_string = istring;
        this->blind = blind;
    }

    // Sum operator simply combines selectors and tags
    Selection operator+=(const Selection & rhs) {
        this -> selection_string = "(" + this->selection_string + ") && (" + rhs.selection_string + ")";
        this -> tag = "(" + this->tag + ") && (" + rhs.tag + ")";
        this -> blind = (this->blind or rhs.blind);
        return *this;
    }
    friend Selection operator+(Selection lhs, const Selection rhs){
        lhs += rhs;
        return lhs;
    }


};

//// Class to implement event selection on an RDF
// The SelectionManager holds a list of individual selections
// It will 
class SelectionManager {
    public:
        SelectionManager();
        SelectionManager(bool blind);
    
        // Setters, getters
        void add_selection(Selection selection);
        void set_blind(bool blind);
        TString get_selection_tag(int position);

        // Applying the selection
        RNode select(RNode rnode);

    private:
        // Functions
        TString get_full_string() const;

        // Data
        vector<Selection> selections_;
        bool blind_;
};

#endif /* SELECTIONMANAGER_H */
