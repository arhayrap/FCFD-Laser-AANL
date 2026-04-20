#!/bin/bash
# eos root://cmseos.fnal.gov rm -r /store/group/cmstestbeam/2020_02_CMSTiming/condor
# eos root://cmseos.fnal.gov mkdir /store/group/cmstestbeam/2020_02_CMSTiming/condor
# eos root://cmseos.fnal.gov mkdir /store/group/cmstestbeam/2020_02_CMSTiming/condor/config
xrdcp -f NetScopeStandaloneDat2Root root://cmseos.fnal.gov//store/group/cmstestbeam/2021_CMSTiming_ETL/condor/
xrdcp -rf config root://cmseos.fnal.gov//store/group/cmstestbeam/2021_CMSTiming_ETL/condor/config
xrdcp -f /uscms/home/rheller/work/TestBeamReco/ETL_Agilent_MSO-X-92004A/Reconstruction/conversion_bin_fast.py root://cmseos.fnal.gov//store/group/cmstestbeam/2021_CMSTiming_ETL/condor/
