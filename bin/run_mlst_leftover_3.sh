#!/bin/bash

source /etc/profile

#$ -N mlst_job_leftover_3
#$ -pe smp 12
#$ -l h_rt=3:00:00:00
#$ -l h_vmem=32G
#$ -q all.q
#$ -j y
#$ -o mlst_job_leftover_3.log
#$ -wd /scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier

genomes_list='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/mlst_leftovers_list.txt'
output_results_file='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/mlst_leftovers_mlst_results.tsv'

cat "$genomes_list" | xargs -P $NSLOTS -I {} bash -c \
    "singularity run images/mlst:2.23.0--hdfd78af_1 mlst --scheme \"senterica_achtman_2\" --threads 1 --quiet \"\$1\" >> \"$output_results_file\"" _ {}