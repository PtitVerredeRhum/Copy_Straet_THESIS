#!/bin/bash
#
#SBATCH --mail-user=romain.cloux@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=adjSTO_300_1001_1030_LP
#SBATCH --time=0-1:55:00 # days-hh:mm:ss
#
#SBATCH --output=simulations/simu_cloux_slurm/adjSTO_300_1001_1030_LP.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1  # python is not parallel
#SBATCH --mem-per-cpu=14000 # megabytes
#SBATCH --partition=batch


# Usage: sbatch Cloux.sh

F_HOME="$HOME/Test_Cloux"

srun  python Cloux_tests/build_and_run_LP_CLX-UCM.py

# Run the GAMS simulation
echo "File prepared, starting simulation..."

first_task_id=$SLURM_JOB_ID
#SBATCH --dependency=afterok:$first_task_id

MY_DIR="simulations/simu_cloux_slurm/adjSTO_300_1001_1030_LP"
cd $MY_DIR


# make sure the 'threads' option set in input file will not take precedence...
sed -i "/^Option threads=/d" UCM_h.gms

# timeout: 2h20
GAMSLOGFILE="$F_HOME/Copy_Straet_THESIS/data-generation/simulations/simu_cloux_slurm/gamsrun_$SLURM_ARRAY_TASK_ID.log"
srun --time=02:20:00 $GAMSPATH/gams UCM_h.gms threads=1 workSpace=9000 > $GAMSLOGFILE
status=$?
