#! /usr/bin/env python
# Author: Izaak Neutelings (May 2020)
# Description: Skim
import os
import time; time0 = time.time()
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from TauFW.PicoProducer.analysis.utils import getmodule
from TauFW.PicoProducer.processors import moddir
#from TauFW.PicoProducer.corrections.era_config import getjson, getera, getjmecalib
from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('-i', '--infiles',  dest='infiles',  type=str, default=[ ], nargs='+')
parser.add_argument('-o', '--outdir',   dest='outdir',   type=str, default='.')
parser.add_argument('-C', '--copydir',  dest='copydir',  type=str, default=None)
parser.add_argument('-m', '--maxevts',  dest='maxevts',  type=int, default=1000)
parser.add_argument('-t', '--tag',      dest='tag',      type=str, default="")
parser.add_argument('-d', '--dtype',    dest='dtype',    choices=['data','mc','embed'], default=None)
parser.add_argument('-y','-e','--era',  dest='era',      type=str, default="")
parser.add_argument('-M', '--module',   dest='module',   type=str, default=None)
parser.add_argument('-c', '--channel',  dest='channel',  type=str, default=None)
parser.add_argument('-p', '--prefetch', dest='prefetch', action='store_true', default=False)
args = parser.parse_args()


# SETTING
era       = args.era
modname   = args.module
channel   = args.channel
if channel:
  import TauFW.PicoProducer.tools.config as GLOB
  CONFIG  = GLOB.getconfig(verb=0)
  if not modname:
    assert channel in CONFIG.channels, "Did not find channel '%s' in configuration. Available channels: %s"%(channel,CONFIG.channels)
    modname = CONFIG.channels[args.channel]
else:
  if not modname:
    modname = "ModuleMuTauSimple"
  channel = modname
dtype     = args.dtype
outdir    = args.outdir
copydir   = args.copydir
maxevts   = args.maxevts if args.maxevts>0 else None
nfiles    = -1
tag       = args.tag
if tag:
  tag     = ('' if tag.startswith('_') else '_') + tag
fname     = os.path.join(outdir,"pico_%s%s.root"%(channel,tag))
director  = "root://cms-xrd-global.cern.ch/"
prefetch  = args.prefetch
presel    = None #"Muon_pt[0] > 50"
branchsel = os.path.join(moddir,"keep_and_drop_skim.txt")
json      = None
modules   = [ ]

# GET FILES
infiles   = args.infiles or [
  #"data/DYJetsToLL_M-50_NanoAODv6.root",
  #"/afs/cern.ch/user/i/ineuteli/analysis/CMSSW_10_3_3/src/TauFW/PicoProducer/data/DYJetsToLL_M-50_NanoAODv6.root",
  director+'/store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/67/myNanoProdMc2017_NANO_66.root',
  director+'/store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/68/myNanoProdMc2017_NANO_67.root',
  #director+'/store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/69/myNanoProdMc2017_NANO_68.root',
  #director+'/store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/70/myNanoProdMc2017_NANO_69.root',
  #director+'/store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/71/myNanoProdMc2017_NANO_70.root',
  #director+'/store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/72/myNanoProdMc2017_NANO_71.root',
  #director+'/store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/73/myNanoProdMc2017_NANO_72.root',
  #director+'/store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/74/myNanoProdMc2017_NANO_73.root',
  #director+'/store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/75/myNanoProdMc2017_NANO_74.root',
  #director+'/store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/76/myNanoProdMc2017_NANO_75.root',
]
if nfiles>0:
  infiles = infiles[:nfiles]
if dtype==None:
  dtype = 'mc'
if any(s in infiles[0] for s in ['SingleMuon',"/Tau/",'SingleElectron','EGamma']):
  dtype = 'data'

# GET MODULE
module  = getmodule(modname)(fname)
modules.append(module)

# PRINT
print '-'*80
print ">>> %-12s = %r"%('era',era)
print ">>> %-12s = %r"%('channel',channel)
print ">>> %-12s = %r"%('modname',modname)
print ">>> %-12s = %s"%('modules',modules)
print ">>> %-12s = %r"%('dtype',dtype)
print ">>> %-12s = %s"%('maxevts',maxevts)
print ">>> %-12s = %r"%('outdir',outdir)
print ">>> %-12s = %r"%('copydir',copydir)
print ">>> %-12s = %s"%('infiles',infiles)
print ">>> %-12s = %r"%('fname',fname)
print ">>> %-12s = %r"%('branchsel',branchsel)
print ">>> %-12s = %r"%('json',json)
print ">>> %-12s = %s"%('prefetch',prefetch)
print '-'*80

# RUN
p = PostProcessor(outdir,infiles,cut=None,branchsel=None,noOut=True,
                  modules=modules,jsonInput=json,maxEntries=maxevts,prefetch=prefetch)
p.run()

# COPY
if copydir:
  from TauFW.PicoProducer.storage.StorageSystem import getstorage
  store = getstorage(copydir,verb=2)
  outfiles = os.path.join(outdir,fname)
  store.cp(outfiles)

# DONE
print ">>> Done after %.1f seconds"%(time.time()-time0)