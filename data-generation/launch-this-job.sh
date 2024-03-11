#!/bin/bash
#
#SBATCH --mail-user=f.straet@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Dispa-SET-data-generation
#SBATCH --time=0-05:00:00 # days-hh:mm:ss
#
#SBATCH --output=slurm-outputs/Job-singlesim_%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=9000 # megabytes 
#SBATCH --partition=batch
#
# called via main.sh with
# sbatch --array=1-$N_SAMPLES
# disable SBATCH --array=0-1

# Adapted from LaunchParallelJobs_carla.sh
#
# Runs the jobs to make a complete simulation:
# - preparing the files, 
# - running GAMS
# - reading the output and writing it to the dataset file.
#
# This script will usually not be submitted manually, but rather through the use of 
# launch-job-series.sh.
#
# The index of the sample to be used for the simulation is computed based on the series index given
# as argument, and the SLURM $SLURM_ARRAY_TASK_ID environment variable. Therefore, it will not work
# properly if not submitted with --array=$min-$max to the cluster.
#
# Usage: sbatch --array=0-$n launch-simulation-jobs.sh <series_idx>

LAUNCH_DIR=$(pwd)
F_HOME="$HOME/Test_Cloux"
export GAMSPATH=$F_HOME/gams42.5_linux_x64_64_sfx

BASE_DIR=$(python -c "from config import SIMULATIONS_DIR; print(SIMULATIONS_DIR)")
DATASET_NAME=$(python -c "from config import DATASET_NAME; print(DATASET_NAME)")

# Load Python 3.9 and environment
module load Python/3.9.6-GCCcore-11.2.0
source $F_HOME/Dispa-SET/.env/bin/activate

echo "Job ID: $SLURM_JOBID"
echo "Job dir: $SLURM_SUBMIT_DIR"
echo "Running simulation serie $serie_idx - $SLURM_ARRAY_TASK_ID, $simulation_idx"


simulation_idx=24
DIRS=($BASE_DIR/sim-${simulation_idx}_*)
CUR_DIR=${DIRS[0]}
cd $CUR_DIR

# Run the GAMS simulation
echo "File prepared, starting simulation..."

# make sure the 'threads' option set in input file will not take precedence...
sed -i "/^Option threads=/d" UCM_h.gms

GAMSLOGFILE="$LAUNCH_DIR/slurm-outputs/$BASE_DIR/gamsrun-single_$simulation_idx.log"
srun --time=03:00:00 $GAMSPATH/gams UCM_h.gms threads=1 workSpace=9000 > $GAMSLOGFILE
status=$?

GAMSSTATUS=$(grep "*** Status:" $GAMSLOGFILE)
gamserror="0"
if [[ $GAMSSTATUS == *"error"* ]]; then
    gamserror="1"
elif [[ $status != "0" ]]; then
    gamserror="2"
fi

cd $LAUNCH_DIR

# Fetch the results
echo "Simulation ran, reading results..."
srun python read_results.py --single $CUR_DIR $gamserror

# do some cleaning...
# tar -cvzf slurm-outputs/$BASE_DIR/lst_files/run-$serie_idx-$SLURM_ARRAY_TASK_ID.lst.tar.gz -C $CUR_DIR UCM_h.lst UCM_h.gms
# rm -rf $CUR_DIR/

echo "Simulation $simulation_idx is done (job id $SLURM_JOBID), GAMS error: $gamserror" >> slurm-outputs/$BASE_DIR/finished.txt
echo "Job ID $SLURM_JOBID n°$SLURM_ARRAY_TASK_ID is finished"

