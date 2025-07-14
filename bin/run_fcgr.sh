#!/bin/bash
#$ -N fcgr
#$ -cwd
#$ -q all.q 
#$ -pe smp 8
#$ -j y
#$ -l h_vmem=50G

source /etc/profile

module load miniconda/24.11.1
eval "$(conda shell.bash hook)"

conda activate /scicomp/home-pure/rqu4/.conda/envs/fcgr

input_list='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/enterobacteraciae_data/kmc_k5_files.txt'
outdir='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/enterobacteraciae_data/FCGR_arrays'
kmer=5

pip install complexcgr

python3 /scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/FCGR_classifier/bin/fcgr.py \
    -k $kmer \
    -t $NSLOTS \
    $input_list \
    $outdir

