#!/bin/bash

conda activate $HOME/my_conda_envs/ncbi

datasets summary genome taxon "Salmonella" > salmonella_dataset.json
