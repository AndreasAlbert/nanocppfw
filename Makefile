IDIR =.
CC=g++
CFLAGS=-I$(IDIR) -std=c++11 `root-config --cflags --glibs`

PYBIND=`python -m pybind11 --includes` -fPIC --shared

PYBINDIR=pybind
BINDIR=bin
ODIR=obj
SRCDIR=src
LIBS=-lm

# _DEPS = Analyzer
# DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

_OBJ = Analyzer.o HInvAnalyzer.o
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))


$(ODIR)/%.o: $(SRCDIR)/%.cc
	$(CC) -c -o $@ $< $(CFLAGS) -fPIC

run_analysis: $(OBJ)
	$(CC) src/$@.cc -o $(BINDIR)/$@ $^ $(CFLAGS) $(LIBS) 

run_hinv: $(OBJ)
	$(CC) src/$@.cc -o $(BINDIR)/$@ $^ $(CFLAGS) $(LIBS)

PyBindings: $(OBJ)
	$(CC) src/$@.cc -o $(PYBINDIR)/$@.so $^ $(CFLAGS) $(LIBS) $(PYBIND)


.PHONY: clean

clean:
	rm -f $(ODIR)/*.o *~ core $(INCDIR)/*~ $(PYBINDIR)/*.so PyBindings.so $(BINDIR)/*