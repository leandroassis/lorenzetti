#!/usr/bin/env python3

from GaugiKernel import LoggingLevel, Logger
from GaugiKernel import GeV
import argparse
import sys,os


mainLogger = Logger.getModuleLogger("zee")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

#
# Mandatory arguments
#

parser.add_argument('--nov','--numberOfEvents', action='store', dest='numberOfEvents', 
                    required = False, type=int, default=1,
                    help = "The number of events to be generated.")

parser.add_argument('--eventNumber', action='store', dest='eventNumber', 
                    required = False, default=[], type=int,
                    help = "The list of numbers per event.")

parser.add_argument('-o','--outputFile', action='store', dest='outputFile', required = True,
                    help = "The event file generated by pythia.")

#
# Pileup simulation arguments
#

parser.add_argument('--pileupAvg', action='store', dest='pileupAvg', required = False, type=int, default=0,
                    help = "The pileup average (default is zero).")

parser.add_argument('--bc_id_start', action='store', dest='bc_id_start', required = False, type=int, default=-21,
                    help = "The bunch crossing id start.")

parser.add_argument('--bc_id_end', action='store', dest='bc_id_end', required = False, type=int, default=4,
                    help = "The bunch crossing id end.")

parser.add_argument('--bc_duration', action='store', dest='bc_duration', required = False, type=int, default=25,
                    help = "The bunch crossing duration (in nanoseconds).")


#
# Extra parameters
#

parser.add_argument('--outputLevel', action='store', dest='outputLevel', required = False, type=int, default=0,
                    help = "The output level messenger.")

parser.add_argument('-s','--seed', action='store', dest='seed', required = False, type=int, default=0,
                    help = "The pythia seed (zero is the clock system)")


if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()

try:
  
  
  from guns import PythiaGun
  from filters import Zee
  from GenKernel import EventTape

  tape = EventTape( "EventTape", OutputFile = args.outputFile)
  
  main_file = os.environ['LZT_PATH']+'/generator/guns/data/zee_config.cmnd'

  zee = Zee( "Zee", 
            PythiaGun("MainGenerator", 
                      File=main_file, 
                      Seed=args.seed, 
                      EventNumber = args.eventNumber),
            EtaMax      = 3.2,
            MinPt       = 15*GeV,
            OutputLevel  = args.outputLevel
           )
  tape+=zee

  if args.pileupAvg > 0:

    mb_file   = os.environ['LZT_PATH']+'/generator/guns/data/minbias_config.cmnd'

    from filters import Pileup
    pileup = Pileup("Pileup",
                   PythiaGun("MBGenerator", File=mb_file, Seed=args.seed),
                   EtaMax         = 3.2,
                   Select         = 2,
                   PileupAvg      = args.pileupAvg,
                   BunchIdStart   = args.bc_id_start,
                   BunchIdEnd     = args.bc_id_end,
                   OutputLevel    = args.outputLevel,
                   DeltaEta       = 0.22,
                   DeltaPhi       = 0.22,
                  )

    tape+=pileup
  
  # Run!
  tape.run(args.numberOfEvents)

  sys.exit(0)
except  Exception as e:
  print(e)
  sys.exit(1)