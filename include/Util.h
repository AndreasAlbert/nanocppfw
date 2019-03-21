#include <string>
#include <vector>
#include <algorithm>

#include <TString.h>

/// Taken from https://stackoverflow.com/a/12468109
std::string random_string( size_t length )
{
    auto randchar = []() -> char
    {
        const char charset[] =
        "0123456789"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz";
        const size_t max_index = (sizeof(charset) - 1);
        return charset[ rand() % max_index ];
    };
    std::string str(length,0);
    std::generate_n( str.begin(), length, randchar );
    return str;
}


vector<TString> string_to_tstrings(vector<string> strings) {
    vector <TString> tstrings;
    for(auto const istring : strings) {
        tstrings.push_back(TString(istring));
    }
    return tstrings;
}