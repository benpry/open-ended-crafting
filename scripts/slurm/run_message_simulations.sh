#!/bin/zsh
#SBATCH --job-name=eval_messages
#SBATCH --account=cocoflops
#SBATCH --partition=cocoflops
#SBATCH --nodelist cocoflops1
#SBATCH --output=slurm-output/message-eval-%j.out
#SBATCH --error=slurm-output/message-eval-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00

source ~/.zshrc
conda activate oecraft
cd ~/open-ended-crafting

python -m scripts.simulate_message_effects --naming_model openai/gpt-oss-20b --agent_model gemini-2.5-flash --num-rounds 5 --num-chains 10 --chain-length 1 --output-dir data/simulations --verbose False
