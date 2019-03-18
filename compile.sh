# g++ JetCleaning.h  `root-config --cflags --glibs` -std=c++11 -o JetCleaning.o
# g++ JetCleaning.h  `root-config --cflags --glibs` -std=c++11 -o JetCleaning.o
g++ test_rdf.cc  `root-config --cflags --glibs` -ggdb -std=c++11 -o test_rdf.o -I .
