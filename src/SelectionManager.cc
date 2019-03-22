#include "interface/SelectionManager.h"

using namespace std;

SelectionManager::SelectionManager() : SelectionManager(false) {};
SelectionManager::SelectionManager(bool blind){
    this->blind_ = blind;
}

void SelectionManager::add_selection(Selection selection) {
    this->selections_.push_back(selection);
}

void SelectionManager::set_blind(bool blind) {
    this->blind_ = blind;
}
// Constructs a string representing the sum of all selections
// The individual selections are encoded as bits by adding powers of two.
// If 'blind' is specified, blinded selections are not included
// 
//  Example:
//      bool blind = false;
//      SelectionManager sman(blind);
//      sman.add_selection(Selection("pt > 5", false));
//      sman.add_selection(Selection("|eta| > 2", true));
//      sman.add_selection(Selection("MET > 100", false));
//      sman.get_full_string();
//          -> "1 * (pt>5) + 2 * (|eta| > 2) + 4 > (MET>100)"
//      sman.set_blind(true);
//      sman.get_full_string();
//          -> "1 * (pt>5) + 4 > (MET>100)"
//
TString SelectionManager::get_full_string() const {
    TString ret = "";
    for(unsigned int i=0; i < selections_.size(); i++){
        auto const sel = this->selections_.at(i);

        // Possibly skip blinded selections
        if(this->blind_ != sel.blind){
            continue;
        }
        // Plus sign for all but the first selection
        if ( i > 0) {
            ret += "+";
        }
        // Append string for this selection to total
        string power_of_two = to_string(int(pow(2,i)));
        ret += power_of_two + "*(" + sel.selection_string + ")";
    }
    return ret;
}

// Defines the "selection" Variable on the RNode
RNode SelectionManager::select(RNode rnode) {
    auto selection_string = get_full_string();
    auto ret = rnode.Define("selection", selection_string.Data());
    return ret;
}
