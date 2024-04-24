#!/bin/bash
#
#SBATCH --mail-user=romain.cloux@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Dispa-SET-adj_test_LP
#SBATCH --time=0-2:00:00 # days-hh:mm:ss
#
#SBATCH --output=simulations/simu_cloux_slurm/adj_VRES_1001-1030_LP_%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16  # python is not parallel
#SBATCH --mem-per-cpu=8000 # megabytes
#SBATCH --partition=batch

# Starts the reference job on the cluster.
#
# Separating this run from the main.sh script allow to optimize resource usage, as
# main.sh doesn't need to carry out heavy computations.
#
# Usage: sbatch Cloux_LP.sh



srun python Cloux_tests/build_and_run_LP_CLX.py