#include "interface/Analyzer.h"

#ifndef HINVANALYZER_H
#define HINVANALYZER_H


class HInvAnalyzer : public Analyzer {
    using Analyzer::Analyzer;
    private:
        void analyze_variation_(RNode rnode, TString variation) override;
};
#endif // HINVANALYZER_H