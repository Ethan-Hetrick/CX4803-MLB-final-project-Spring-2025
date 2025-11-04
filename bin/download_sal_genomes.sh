#!/bin/bash

conda activate $HOME/my_conda_envs/ncbi

cd /scratch/salmonella

# Download dehydrated dataset
datasets download genome taxon "Salmonella" \
    --dehydrated \
    --filename ./salmonella_dataset.zip \
    --no-progressbar \
    --assembly-version 'latest' \
    --api-key "${API_KEY}"

# Unzip and rehydrate
unzip ./salmonella_dataset.zip

datasets rehydrate \
    --directory ./ \
    --no-progressbar \
    --api-key "${API_KEY}"

# Download genome summary and convert to csv
datasets summary genome taxon "Salmonella" > salmonella_dataset.json

bin/datasets_summary2csv.py --json_file_path salmonella_dataset.json csv_file_path salmonella_dataset.csv
