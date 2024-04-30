#!/bin/bash
#
#SBATCH --mail-user=romain.cloux@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Dispa-SET-reference_MILP
#SBATCH --time=0-4:55:00 # days-hh:mm:ss
#
#SBATCH --output=simulations/simu_cloux_slurm/ref_1y_MILP_16CPU_%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1  # python is not parallel
#SBATCH --mem-per-cpu=10000 # megabytes
#SBATCH --partition=batch


# Usage: sbatch Cloux.sh

F_HOME="$HOME/Test_Cloux"

srun python Cloux_tests/build_and_run_LP_CLX-UCM.py

# Run the GAMS simulation
echo "File prepared, starting simulation..."

# make sure the 'threads' option set in input file will not take precedence...
sed -i "/^Option threads=/d" UCM_h.gms

# timeout: 2h20
GAMSLOGFILE="$F_HOME/Copy_Straet_THESIS/data-generation/simulations/simu_cloux_slurm/gamsrun_$SLURM_ARRAY_TASK_ID.log"
srun --time=02:20:00 $GAMSPATH/gams UCM_h.gms threads=1 workSpace=9000 > $GAMSLOGFILE
status=$?
