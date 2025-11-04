#!/bin/bash

conda activate $HOME/my_conda_envs/ncbi

cd /scratch/salmonella

datasets download genome taxon "Salmonella" \
    --dehydrated \
    --filename ./salmonella_dataset.zip \
    --no-progressbar \pwd
    --assembly-version 'latest' \
    --api-key "${API_KEY}"

unzip ./salmonella_dataset.zip

datasets rehydrate \
    --directory ./ \
    --no-progressbar \
    --api-key "${API_KEY}"
