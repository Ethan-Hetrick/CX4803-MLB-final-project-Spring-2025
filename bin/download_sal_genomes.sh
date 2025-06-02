#!/bin/bash

source /etc/profile

#$ -N qsub
#$ -pe smp 4
#$ -l h_vmem=16G
#$ -q long.q
#$ -j y
#$ -o download_sal_dataset.log
#$ -cwd

module load miniconda/24.11.1
eval "$(conda shell.bash hook)"

conda activate /scicomp/home-pure/rqu4/my_conda_envs/ncbi

cd /scicomp/scratch/rqu4/salmonella

# datasets download genome taxon "Salmonella" \
#     --dehydrated \
#     --filename ./salmonella_dataset.zip \
#     --no-progressbar \pwd
#     --assembly-version 'latest' \
#     --api-key 'd3a15334f0efb8e31c99564bd4e56499fd08'

# unzip ./salmonella_dataset.zip

datasets rehydrate \
    --directory ./ \
    --no-progressbar \
    --api-key 'd3a15334f0efb8e31c99564bd4e56499fd08'