#include<vector>
#include<TString.h>
#include "interface/Analyzer.h"
#include "interface/SelectionManager.h"

#ifndef HINVANALYZER_H
#define HINVANALYZER_H

class HInvAnalyzer : public Analyzer {
    using Analyzer::Analyzer;
    HInvAnalyzer(vector<TString> infiles);
    private:
        void analyze_variation_(RNode rnode, TString variation) override;
        SelectionManager initialize_selections_();        
        SelectionManager selection_manager_;
};
#endif // HINVANALYZER_H