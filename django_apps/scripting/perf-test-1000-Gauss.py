
# Example 2011 collisions options for Brunel

# Syntax is:
#   gaudirun.py COLLISION11-Beam3500GeV-VeloClosed-MagDown.py
#
from Gaudi.Configuration import *
from Configurables import Gauss

###############################################################################
# Set here any steering options.
# Available steering options and defaults are documented in
# $BRUNELROOT/python/Brunel/Configuration.py
###############################################################################

# Just instantiate the configurable...
theApp = Gauss()

###############################################################################
# I/O datasets are defined in a separate file, see examples in 2008-TED-Data.py
###############################################################################
importOptions("$APPCONFIGOPTS/Gauss/Beam3500GeV-md100-MC11-nu2.py")
importOptions("$APPCONFIGOPTS/Gauss/xgen.py")
importOptions("$DECFILESROOT/options/@[eventtype].py") #to be changed later 
##############################################################################
# Database tags must be set and are defined in a separate file
##############################################################################
from Configurables import LHCbApp
LHCbApp().DDDBtag   = "MC11-20111102"
LHCbApp().CondDBtag = "sim-20111111-vc-md100"
# Options specific for a given job
# ie. setting of random number seed and name of output files
#
from Gauss.Configuration import *

#--Generator phase, set random numbers
GaussGen = GenInit("GaussGen")
GaussGen.FirstEventNumber = 1
GaussGen.RunNumber        = 1082
#--Number of events
nEvts = 1000
LHCbApp().EvtMax = nEvts
MessageSvc().countInactive=True;
LHCbApp().XMLSummary = "summary.xml";
