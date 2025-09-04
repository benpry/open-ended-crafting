#!/bin/zsh
#SBATCH --job-name=oracle_mcts
#SBATCH --account=cocoflops
#SBATCH --partition=cocoflops
#SBATCH --nodelist cocoflops2
#SBATCH --output=slurm-output/oracle-mcts-%j.out
#SBATCH --error=slurm-output/oracle-mcts-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=256G
#SBATCH --time=24:00:00

source ~/.zshrc
conda activate oecraft
cd ~/open-ended-crafting

python -m scripts.run_oracle_mcts_agent --domain cooking --n_runs 100 --n_steps 15 --n_simulations 3000 --exploration_c 1.25 --discount_factor 0.98 &
python -m scripts.run_oracle_mcts_agent --domain decorations --n_runs 100 --n_steps 15 --n_simulations 3000 --exploration_c 1.25 --discount_factor 0.98 &
python -m scripts.run_oracle_mcts_agent --domain animals --n_runs 100 --n_steps 15 --n_simulations 3000 --exploration_c 1.25 --discount_factor 0.98 &
python -m scripts.run_oracle_mcts_agent --domain potions --n_runs 100 --n_steps 15 --n_simulations 3000 --exploration_c 1.25 --discount_factor 0.98 &
wait