#!/bin/bash

source /etc/profile

#$ -N quast_job_ad
#$ -pe smp 8
#$ -l h_vmem=4G
#$ -q extralong.q
#$ -j y
#$ -o quast_job_ad.log # Unique log file
#$ -wd /scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier

# Define the input file for this specific job
genomes_list_part='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/genomes_part_ad'

# Change into working directory
cd /scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/quast_results

# Loop through each genome path listed in genomes_part_ad
while IFS= read -r genome_fasta_path; do
    genome_name_no_ext=$(basename "${genome_fasta_path%.fna}" | sed 's/\.fasta$//' | sed 's/\.fastq$//')

    singularity run /scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/quast\:5.3.0--py313pl5321h5ca1c30_2 quast \
        --fast \
        --space-efficient \
        --memory-efficient \
        --threads 8 \
        --output-dir ./$genome_name_no_ext \
        "$genome_fasta_path"
done < "$genomes_list_part"