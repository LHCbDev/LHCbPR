
# Example 2011 collisions options for Brunel

# Syntax is:
#   gaudirun.py COLLISION11-Beam3500GeV-VeloClosed-MagDown.py
#
from Gaudi.Configuration import FileCatalog, EventSelector
from Configurables import Brunel

#-- File catalogs. First one is read-write
FileCatalog().Catalogs = [ "xmlcatalog_file:MyCatalog.xml" ]

#-- Use latest 2011 database tags for real data
Brunel().DataType = "2011"

EventSelector().Input = [
  "DATAFILE='mdf:///scratch/z5/perftest/data/097120_0000000003.raw' SVC='LHCb::MDFSelector'"
    ]
###############################################################################
# File for running Brunel with default options (2008 real data,.mdf in,.dst out)
###############################################################################
# Syntax is:
#   gaudirun.py Brunel-Default.py <someDataFiles>.py
###############################################################################

from Configurables import Brunel

###############################################################################
# Set here any steering options.
# Available steering options and defaults are documented in
# $BRUNELROOT/python/Brunel/Configuration.py
###############################################################################

# Just instantiate the configurable...
theApp = Brunel()

###############################################################################
# I/O datasets are defined in a separate file, see examples in 2008-TED-Data.py
###############################################################################
from Brunel.Configuration import *;
Brunel().EvtMax=10;
#Brunel.SkipEvents = 134
#Brunel().Monitors=["SC","FPE"];
#Brunel().OutputType="SDST";
Brunel().OutputType="NONE";
Brunel().PackType="MDF";
MessageSvc().countInactive=True;

LHCbApp().XMLSummary = "summary.xml";
