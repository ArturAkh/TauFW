# PicoProducer

This setup run the [post-processors](https://github.com/cms-nanoAOD/nanoAOD-tools) on nanoAOD.
There are two modes:
1. **Skimming**: Skim nanoAOD by removing [unneeded branches](https://github.com/cms-tau-pog/TauFW/blob/master/PicoProducer/python/processors/keep_and_drop_skim.txt),
                 bad data events,
                 add things like JetMET corrections. Output is again nanoAOD.
2. **Analysis**: Main analysis code in [`python/analysis/`](python/analysis),
                 pre-selecting events and objects and constructing variables.
                 The output is a custom tree format we will refer to as _pico_.


## Installation

See [the README in the parent directory](../../../#taufw). Test the installation with
```
pico.py --help
```


## Configuration

The user configuration is saved in `config/config.json`.
You can manually edit the file, or set some variable with
```
pico.py set <variables> <value>
```
The configurable variables include
* `batch`: Batch system to use (e.g. `HTCondor`)
* `jobdir`: Directory to output job configuration and log files (e.g. `output/$ERA/$CHANNEL/$SAMPLE`)
* `nanodir`: Directory to store the output nanoAOD files from skimming jobs.
* `outdir`: Directory to copy the output pico files from analysis jobs.
* `picodir`: Directory to store the `hadd`'ed pico file from analysis job output.
* `nfilesperjob`: Default number of files per job.
The directories can contain variables with `$` like
`$ERA`, `$CHANNEL`, `$CHANNEL`, `$TAG`, `$SAMPLE`, `$GROUP` and `$PATH`.

### Skimming
Channels with `skim` in the name are reserved for skimming.
Link your skimming channel with a post-processor in [`python/processors/`](python/processors) with
```
pico.py channel mutau ModuleMuTau.py
```
An example is given in [`skimjob.py`](python/processors/skimjob.py).

### Analysis
To link a channel short name (e.g. `mutau`) to an analysis module
in [`python/analysis/`](python/analysis), do
```
pico.py channel mutau ModuleMuTau.py
```
An simple example of an analysis is given in [`ModuleMuTauSimple.py`](python/analysis/ModuleMuTauSimple.py).

### Era & Sample list
To link an era to your favorite sample list in [`samples/`](samples/), do
```
pico.py era 2016 sample_2016.py
```


## Plug-ins

To plug in your own batch system, make a subclass [`BatchSystem`](python/batch/BatchSystem.py)
overriding the abstract methods (e.g. `submit`).
Your subclass has to be saved in separate python module in [`python/batch`](python/batch),
and the module's filename should be the same as the class. See for example [`HTCondor.py`](python/batch/HTCondor.py).

Similarly for a storage element, subclass [`StorageSystem`](python/storage/StorageSystem.py).


## Samples

Specify the samples with a python file in [`samples/`](samples).
The file must include a python list `samples`, containing `Sample` objects
(or those from the derived `MC` and `Data` classes). For example,
```
samples = [
  Sample('DY','DYJetsToLL_M-50',
    "/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    dtype='mc',store=None
  )
]
```
The first string to `Sample` is to group samples together (e.g. `DY`),
the second is a short name for the sample  (e.g. `DYJetsToLL_M-50`),
and all arguments after that are the full DAS paths of the sample.

To run on nanoAOD you skimmed, or files stored elsewhere than on DAS, use the keyword `store`.
The path can contain variables like `$PATH` for the full DAS path, `$GROUP` for the group, `SAMPLE` for the sample short name.


## Local run
A local run can be done as
```
pico.py run -y 2016 -c mutau
```
You can specify a sample that is available in [`samples/`](samples), by passing the `-s` flag a pattern as
```
pico.py run -y 2016 -c mutau -s 'DYJets*M-50'
pico.py run -y 2016 -c mutau -s 'SingleMuon'
```


## Batch submission

### Submission
Once configured, submit with
```
pico.py submit -y 2016 -c mutau
```
This will create the the necessary output directories for job out put.
A JSON file is created to keep track of the job input and output.

You can specify a sample by a pattern to `-s`, or exclude one with `-x`. Glob patterns like `*` wildcards are allowed.
To give the output files a specific tag, use `-t`.

### Status
Check the job status with
```
pico.py status -y 2016 -c mutau
```

### Resubmission
If jobs failed, you can resubmit with
```
pico.py resubmit -y 2016 -c mutau
```

### Finalize
ROOT files from analysis output can be `hadd`'ed into one pico file:
```
pico.py hadd -y 2016 -c mutau
```
This will not work for channels with `skim` in the name,
as it is preferred to keep skimmed nanoAOD files split for batch submission.
