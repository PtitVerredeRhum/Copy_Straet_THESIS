# Data generation notes


## Files

- `Database/` folder containing all the Dispa-SET input data
- `Database/rescale.py` rescale some variable in the database
- `ConfigFiles/` folder containing the different Dispa-SET configuration files
- `simulations/` folder containing the simulations outputs

Dispa-SET is expected to be found under the `$HOME` directory.

### Python code
- `config.py` holds the data about the simulation to be set up and run, most importantly:
    - the number of simulations (points on the LHS)
    - the output folder for the simulations
    - and the names of other files

    The other files make reference to this one (`python -c "import x; print(x)"`) to set their variables.
- `reference.py` runs the reference simulation and writes necessary info to `$SIMULATION_FOLDER/reference-info.json`
- `sampling.py` runs the LHS, and scales it to the input ranges, and prepares the GAMS file for the simulation
- `read_results.py` fetches the outputs of the GAMS run. If called with no arguments, fetches all the results from each simulation, if called with `--single folder` only fetches the results in that folder.

In Dispa-SET, the `dispaset/__init__.py` file has been edited so that the logging only uses the console output (further redirected through a file via SLURM). The log file is named based on time, and therefore mutliple runs may try to write to the same file at once.

### Scripts
- `main.sh` sbatch-able script that prepares terrain for running simulations, configured in `config.py`. After executing it, you have to submit the actual simulation jobs with `launch-job-series.sh`
- `launch-job-series.sh` shell script. Adds a series of job to the queue, as it is not large enough to hold all the  jobs at once. Also prepares the submission of the next series, so that `./launch-job-series.sh 0` will run them all.
- `launch-simulation-jobs.sh` slurm script, starts jobs to do the simulations. 
    1. Prepares the file (`sampling.py --prepare-one $i`), where `$i` refers to an index in [0, $N_SAMPLES-1]
    1. Run the simulation (call to GAMS)
    1. to be run, then one to call `read_results.py --single` to fetch its results. Finally, removes large simulations files to avoid exceeding the storage limit.

    NB: Limits GAMS solver to 4 CPUs.
- `launch-reference-job.sh` slurm script. For resource efficiency reasons, to avoid having `main.sh` requiring significant resources on the cluster. Runs `reference.py`.
