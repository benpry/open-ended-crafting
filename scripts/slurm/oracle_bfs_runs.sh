#!/bin/zsh
#SBATCH --job-name=oracle_bfs
#SBATCH --account=cocoflops
#SBATCH --partition=cocoflops
#SBATCH --nodelist cocoflops2
#SBATCH --output=slurm-output/oracle-bfs-%j.out
#SBATCH --error=slurm-output/oracle-bfs-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=256G
#SBATCH --time=24:00:00

source ~/.zshrc
conda activate oecraft
cd ~/open-ended-crafting

python -m scripts.run_oracle_bfs_agent --domain cooking --n_runs 10 --n_steps 8 &
python -m scripts.run_oracle_bfs_agent --domain decorations --n_runs 10 --n_steps 8 &
python -m scripts.run_oracle_bfs_agent --domain animals --n_runs 10 --n_steps 8 &
python -m scripts.run_oracle_bfs_agent --domain potions --n_runs 10 --n_steps 8 &
wait
