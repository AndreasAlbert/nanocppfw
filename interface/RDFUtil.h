#ifndef RDFUTIL_H
#define RDFUTIL_H
#include <TROOT.h>
#include <ROOT/RDataFrame.hxx>
#include <set>
#include <algorithm>    // std::find

/// Convenience definitions
using namespace ROOT::VecOps;
using doubles = RVec<double>;
using floats = RVec<float>;
using bools = RVec<Bool_t>;
using ints = RVec<int>;

// Applies the  ROOT::VecOps::Take operation to vectors of floats
// This wrapping is necessary so that this function
// can be used in RDF Define statements, e.g.:
// RBF.Define("subset_of_pt", rdf_take_f, {"pt","good_indices"})
floats rdf_take_f(floats const vector, ints indices){
    return ROOT::VecOps::Take(vector, indices);
}

// Applies the ROOT::VecOps::Intersect operation to vectors of integers
// This wrapping is necessary so that this function
// can be used in RDF Define statements, e.g.:
// RBF.Define("indices_matching_A_and_B", rdf_intersect_i, {"indices_matching_A","indices_matching_B"})
ints rdf_intersect_i(ints const vec1, ints const vec2){
    return ROOT::VecOps::Intersect(vec1, vec2);
}

// Returns the length of an RVec
int rdf_count_f(floats const vector){
    return vector.size();
}


// Returns an RVec of unique entries in the input vector
template <typename T>
RVec<T> UniqueItems(RVec<T> const vector){
    RVec<T> ret;
    // Loop over entries, check if we already have this entry
    // If no, add it to output
    for(auto const value : vector) {
        bool found = find(ret.begin(), ret.end(), value) == vector.end();
        if (not found){
            ret.push_back(value);
        }
    }
    return ret;
}
#endif //RDFUTIL_H