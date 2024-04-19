#!/bin/bash
#
#SBATCH --mail-user=romain.cloux@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Dispa-SET-reference_MILP
#SBATCH --time=1-23:55:00 # days-hh:mm:ss
#
#SBATCH --output=simulations/simu_cloux_slurm/ref_1y_MILP_16CPU_%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16  # python is not parallel
#SBATCH --mem-per-cpu=8000 # megabytes
#SBATCH --partition=batch


# Usage: sbatch Cloux.sh



srun python Cloux_tests/build_and_run_CLX.py
