#ifndef ANALYZER_H
#define ANALYZER_H

#include <vector>
#include <string>

using namespace std;

class Analyzer{
    public:
        Analyzer(vector<string> infiles);
        void analyze();
    private:
        vector<string> files_;
};
#endif // ANALYZER_H