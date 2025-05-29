#!/bin/bash

source /etc/profile

#$ -N qsub
#$ -pe smp 1
#$ -l h_vmem=8G
#$ -q all.q
#$ -j y
#$ -o download_sal_metadata.log
#$ -cwd

module load miniconda/24.11.1
eval "$(conda shell.bash hook)"

conda activate /scicomp/home-pure/rqu4/my_conda_envs/ncbi

datasets summary genome taxon "Salmonella" > salmonella_dataset.json
