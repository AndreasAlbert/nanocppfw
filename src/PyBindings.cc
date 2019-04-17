
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "interface/Analyzer.h"
#include "interface/HInvAnalyzer.h"


namespace py = pybind11;

PYBIND11_MODULE(nanocppfw, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring

    py::class_<Analyzer>(m, "Analyzer")
        .def(py::init<const std::vector<std::string> &>())
        .def("run", &Analyzer::run);

    py::class_<HInvAnalyzer>(m, "HInvAnalyzer")
        .def(py::init<const std::vector<std::string> &>())
        .def("run", &Analyzer::run)
        .def("set_fixed_dataset", &Analyzer::set_fixed_dataset)
        .def("set_output_path", &Analyzer::set_output_path);
}
