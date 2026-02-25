#!/bin/zsh
#SBATCH --job-name=potions_variant_evaluation
#SBATCH --account=cocoflops
#SBATCH --partition=cocoflops
#SBATCH --nodelist cocoflops1
#SBATCH --output=slurm-output/potions-variant-evaluation-%j.out
#SBATCH --error=slurm-output/potions-variant-evaluation-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=12:00:00

source ~/.zshrc
conda activate oecraft
cd ~/open-ended-crafting

# run the chain simulations
python -m scripts.run_models_on_potions_variants --naming_model openai/gpt-oss-20b --agent_model gemini-2.5-flash --num-rounds 10 --num-chains 20 --chain-length 4 --output-dir data/simulations --verbose False
