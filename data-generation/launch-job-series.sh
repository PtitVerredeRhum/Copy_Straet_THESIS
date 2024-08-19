#!/bin/bash
#
#SBATCH --mail-user=f.straet@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Job-launcher
#SBATCH --time=1-23:00:00 # days-hh:mm:ss
#
#SBATCH --output=slurm-outputs/series-launcher_%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1 # make sure it runs when all jobs are completed
#SBATCH --mem-per-cpu=40000 # megabytes
#SBATCH --partition=batch

# Starts a series of jobs given its index and prepares the submission of the following series.
# To do so, it submits the first series, and itself with the series just submitted as a 
# dependency, such that the queue size is not exceeded.
#
# Usage: ./launch-job-series.sh <idx>    or
#        sbacth launch-job-series.sh <idx>

if [[ -z "$1" ]]; then
    echo "No series index provided, stopping"
    echo "Usage: $0 <idx>"
    exit
fi

serie_idx=$1
N_SAMPLES=$(python -c "from config import N_SAMPLES; print(N_SAMPLES)")
SIM_NAME=$(python -c "from config import SIMULATIONS_NAME; print(SIMULATIONS_NAME)")
SIM_DIR=$(python -c "from config import SIMULATIONS_DIR; print(SIMULATIONS_DIR)")
DATASET_NAME=$(python -c "from config import DATASET_NAME; print(DATASET_NAME)")
LOG_FILE="slurm-outputs/$SIM_NAME/series-submitted.txt"

series_size=380

total=$(( $N_SAMPLES / $series_size ))
if (($N_SAMPLES > $total * $series_size)); then
    total=$(( $total+1 ))
fi

actual_start=$((serie_idx*series_size))
remaining=$(( $N_SAMPLES - $actual_start - 1))
max=$(( $remaining < $series_size ? $remaining : $series_size-1))

echo "max: $max"

if (($serie_idx >= $total)); then
    cp $SIM_DIR/$DATASET_NAME $SIM_NAME/$DATASET_NAME
    echo "Series number $serie_idx exceeds maximum, copied $DATASET_NAME and exitting"
    exit
fi

if (($serie_idx > 25)); then
    echo "Safeguard exit"
    exit
fi


echo "Starting jobs serie $serie_idx in [0-$((total-1))],  $((serie_idx*series_size)) to $((serie_idx*series_size+max))"
echo "Range [0-$max] submitted for series idx $serie_idx" >> $LOG_FILE
#                           v-- ensures max 128 jobs simultaneously (so that we don't exceed 128 * 333 MB per simulation = 42GB, max is 110GB)
#ID=$(sbatch --array=0-$max%128 --output=slurm-outputs/$SIM_NAME/simulation_$serie_idx-%a.log --parsable one-per-sim.sh $serie_idx)
#ID=$(sbatch --array=180-$max%150 --output=slurm-outputs/$SIM_NAME/simulation_$serie_idx-%a.log --parsable launch-simulation-jobs.sh $serie_idx)
#ID=$(sbatch --array=0-$max%150 --output=slurm-outputs/$SIM_NAME/simulation_$serie_idx-%a.log --parsable launch-simulation-jobs.sh $serie_idx)
ID=$(sbatch --array=0-$max%61 --output=slurm-outputs/$SIM_NAME/simulation_$serie_idx-%a.log --parsable launch-simulation-jobs.sh $serie_idx)

# echo "Submitting with ${ID%%;*} as dependency, launch-job-series.sh $((serie_idx+1))"
sbatch --dependency=afterok:${ID%%;*} launch-job-series.sh $((serie_idx+1))