#!/bin/zsh
#SBATCH --job-name=potions_sims
#SBATCH --account=cocoflops
#SBATCH --partition=cocoflops
#SBATCH --nodelist cocoflops1
#SBATCH --output=slurm-output/potions-sims-%j.out
#SBATCH --error=slurm-output/potions-sims-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=12:00:00

source ~/.zshrc
conda activate oecraft
cd ~/open-ended-crafting

# run the chain simulations
python -m scripts.run_simulations --domain potions --naming_model openai/gpt-oss-20b --agent_model gemini-2.5-flash --num-rounds 10 --num-chains 20 --chain-length 4 --output-dir data/simulations --verbose False &

# run the individual simulations
python -m scripts.run_simulations --domain potions --naming_model openai/gpt-oss-20b --agent_model gemini-2.5-flash --num-rounds 40 --num-chains 20 --chain-length 1 --output-dir data/simulations --verbose False &
wait