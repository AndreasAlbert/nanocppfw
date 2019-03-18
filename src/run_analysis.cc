#include<string>
#include<vector>
#include "interface/Analyzer.h"

int main() {
    vector<string> files;
    files.push_back("/path/to/file");
    Analyzer analyzer(files);
    return(0);
}
