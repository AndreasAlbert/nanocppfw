IDIR=.
CC=g++
CFLAGS=-I$(IDIR) -std=c++11 `root-config --cflags --glibs`

PYBIND=`python -m pybind11 --includes` -fPIC --shared

PYBINDIR=pybind
BINDIR=bin
ODIR=obj
SRCDIR=src
LIBS=-lm

_OBJ = Analyzer.o HInvAnalyzer.o SelectionManager.o
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))

# Set up output directories
$(shell   mkdir -p $(BINDIR))
$(shell   mkdir -p $(ODIR))
$(shell   mkdir -p $(PYBINDIR))

$(ODIR)/%.o: $(SRCDIR)/%.cc
	$(CC) -c -o $@ $< $(CFLAGS) -fPIC

py: $(OBJ)
	$(CC) src/PyBindings.cc -o $(PYBINDIR)/nanocppfw.so $^ $(CFLAGS) $(LIBS) $(PYBIND)


.PHONY: clean

clean:
	rm -f $(ODIR)/*.o *~ core $(INCDIR)/*~ $(PYBINDIR)/*.so PyBindings.so $(BINDIR)/*

