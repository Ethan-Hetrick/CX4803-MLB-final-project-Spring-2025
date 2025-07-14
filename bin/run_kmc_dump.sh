#!/bin/bash

source /etc/profile

#$ -N kmc_job_dump # Unique name for this job
#$ -pe smp 8
#$ -l h_rt=72:00:00
#$ -l h_vmem=32G
#$ -q all.q
#$ -j y
#$ -o kmc_dump.log # Unique log file
#$ -wd /scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier

set -e

results_dir='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/kmc_dump'
files_dir='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/kmc_results'
singularity_image='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/images/kmc:3.2.4--haf24da9_3'

find "$files_dir" -maxdepth 1 -name "*.kmc_pre" -print0 | xargs -0 -P ${NSLOTS} -I {} bash -c '
    file="$1"
    results_dir="$2"
    files_dir="$3"
    singularity_image="$4"

    filename=$(basename "$file")
    file_base="${filename%.*}"
    echo "Decompressing ${file} to ${results_dir}/${file_base}.txt"
    singularity run "$singularity_image" \
        kmc_dump \
        "${files_dir}/${file_base}" \
        "${results_dir}/${file_base}.txt"
' _ {} "$results_dir" "$files_dir" "$singularity_image"