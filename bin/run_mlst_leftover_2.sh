#!/bin/bash

source /etc/profile

#$ -N mlst_job_leftover_2 # Unique name for this job
#$ -pe smp 4
#$ -l h_rt=7:00:00:00
#$ -l h_vmem=8G
#$ -q extralong.q
#$ -j y
#$ -o mlst_job_leftover_2.log # Unique log file
#$ -wd /scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier

# Define the input file for this specific job
genomes_list_part='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/mlst_leftovers.txt'
# Define the output file for this specific job
output_results_file='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/mlst_leftovers_mlst_results.tsv'

# Ensure the output file is empty/created before starting
rm -f "$output_results_file"

# Loop through each genome path listed in genomes_part_aa
while IFS= read -r genome_fasta_path; do
    singularity run images/mlst:2.23.0--hdfd78af_1 mlst --threads $NSLOTS \
        --scheme 'senterica_achtman_2' \
        "$genome_fasta_path" >> "$output_results_file"
done < "$genomes_list_part"
