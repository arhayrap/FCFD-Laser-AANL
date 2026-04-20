#CXX = $(shell root-config --cxx)
CXX = g++        # Use system g++ to avoid Conda libstdc++ conflicts
CC  = gcc
# LD = $(shell root-config --ld)
LD = g++         # Linker; we use system g++
INC = $(shell pwd)

# ROOT library flags for linking
LDFLAGS := $(shell root-config --libs)
# ROOT include flags for compilation
#CPPFLAGS := $(shell root-config --cflags) -I$(INC)/include
CPPFLAGS := -I$(INC)/include $(shell root-config --cflags)  # Correct header paths
#CPPFLAGS += -g -std=c++14
CPPFLAGS += -g
#CPPFLAGS += -g -fsanitize=address -Wall -Wextra -Wno-sign-compare

ifeq ($(shell uname), Darwin)
	CPPFLAGS += -rpath $(shell root-config --prefix)/lib
endif

TARGETS = VMEDat2Root DRSDat2Root DRSclDat2Root NetScopeDat2Root NetScopeStandaloneDat2Root ETL_ASIC_Dat2Root DT5742Dat2Root
SRC = src/Configuration.cc src/Interpolator.cc src/DatAnalyzer.cc 

all : $(TARGETS)

# Old build line using LD (commented)
# $(TARGETS) : %Dat2Root : $(SRC:.cc=.o) src/%Analyzer.o app/%Dat2Root.cc
# 	@echo Building $@
# 	$(LD) $(CPPFLAGS) -o $@ $^ $(LDFLAGS)

# New build line using system g++ and static linking
$(TARGETS): %Dat2Root: $(SRC:.cc=.o) src/%Analyzer.o app/%Dat2Root.cc
	@echo Building $@
	g++ -pthread -std=c++20 -m64 -fsized-deallocation -g -I$(INC)/include -I$(shell root-config --incdir) \
	-o $@ $^ $(LDFLAGS) -L/usr/lib/x86_64-linux-gnu -static-libstdc++ -static-libgcc -pthread -lm -ldl

# Compile individual object files
%.o : %.cc
	@echo $@
	$(CXX) $(CPPFLAGS) -o $@ -c $<

# Clean command
clean :
	rm -rf *.o app/*.o src/*.o $(TARGETS) *~ *.dSYM