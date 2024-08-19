#!/bin/bash
#
#SBATCH --mail-user=romain.cloux@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Test_MILP_1y_60euMWH
#SBATCH --time=1-5:55:00 # days-hh:mm:ss
#
#SBATCH --output=simulations/simu_cloux_slurm/Test_MILP_1y_60euMWH.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1  # python is not parallel
#SBATCH --mem-per-cpu=30000 # megabytes
#SBATCH --partition=batch


# Usage: sbatch Cloux.sh

F_HOME="$HOME/Test_Cloux"

srun  python Cloux_tests/build_and_run_CLX_1y.py

# Run the GAMS simulation
echo "File prepared, starting simulation..."

first_task_id=$SLURM_JOB_ID
#SBATCH --dependency=afterok:$first_task_id

MY_DIR="simulations/simu_cloux_slurm/Test_MILP_1y_60euMWH"
cd $MY_DIR


# make sure the 'threads' option set in input file will not take precedence...
sed -i "/^Option threads=/d" UCM_h.gms

# timeout: 2h20
GAMSLOGFILE="$F_HOME/Copy_Straet_THESIS/data-generation/simulations/simu_cloux_slurm/gamsrun_$SLURM_ARRAY_TASK_ID.log"
srun --time=1-2:55:00 $GAMSPATH/gams UCM_h.gms threads=1 workSpace=20000 > $GAMSLOGFILE
status=$?

GAMSSTATUS=$(grep "*** Status:" $GAMSLOGFILE)
gamserror="0"
if [[ $GAMSSTATUS == *"error"* ]]; then
    gamserror="1"
elif [[ $status != "0" ]]; then
    gamserror="2"
fi