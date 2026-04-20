// C++ includes
#include <string>
#include <assert.h>

// ROOT includes
#include <TROOT.h>

//LOCAL INCLUDES
#include "NetScopeStandaloneAnalyzer.hh"

using namespace std;

int main(int argc, char **argv) {
  gROOT->SetBatch();

  NetScopeStandaloneAnalyzer analyzer;
  analyzer.GetCommandLineArgs(argc, argv);
  analyzer.InitOutput();
  analyzer.InitLoop();
  analyzer.RunEventsLoop();
  
  return 0;
}
