#include<string>
#include<vector>
#include "interface/HInvAnalyzer.h"

int main() {
    ROOT::EnableImplicitMT();

    vector<std::string> files;
    files.push_back("/home/albert/repos/nanocppfw/data/007E0986-34E9-9741-A447-957FF2F1982C.root");
    files.push_back("/home/albert/repos/nanocppfw/data/78341E3C-F2BD-A64E-95D6-550FCA8DDAD4.root");
    files.push_back("/home/albert/repos/nanocppfw/data/E4D76467-890E-E811-8523-FA163E3D9AF7.root");
    HInvAnalyzer analyzer(files);
    analyzer.run();
    return(0);
}
