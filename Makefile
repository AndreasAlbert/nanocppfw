IDIR =.
CC=g++
CFLAGS=-I$(IDIR) -std=c++11 `root-config --cflags --glibs`

BINDIR=bin
ODIR=obj
SRCDIR=src
LIBS=-lm

# _DEPS = Analyzer
# DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

_OBJ = Analyzer.o HInvAnalyzer.o
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))


$(ODIR)/%.o: $(SRCDIR)/%.cc
	$(CC) -c -o $@ $< $(CFLAGS)

run_analysis: $(OBJ)
	$(CC) src/$@.cc -o $(BINDIR)/$@ $^ $(CFLAGS) $(LIBS)

run_hinv: $(OBJ)
	$(CC) src/$@.cc -o $(BINDIR)/$@ $^ $(CFLAGS) $(LIBS)

.PHONY: clean

clean:
	rm -f $(ODIR)/*.o *~ core $(INCDIR)/*~ 



# CC=g++
# CFLAGS=-I.
# DEPS = interface/Analyzer.h

# %.o: %.c $(DEPS)
# 	$(CC) -c -o $@ $< $(CFLAGS)

# Analyzer: src/Analyzer.cc
# 	$(CC) -o testmain testmain.cc src/Analyzer.cc -std=c++11 -I .