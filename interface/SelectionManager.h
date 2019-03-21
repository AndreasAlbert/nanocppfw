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
    TString selection_string;
    bool blind;
    Selection(TString istring, bool iblind) {
        selection_string = istring;
        blind = iblind;
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
