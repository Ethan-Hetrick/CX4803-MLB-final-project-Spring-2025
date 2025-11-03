#!/bin/bash

source /etc/profile

#$ -N mlst_job_aa # Unique name for this job
#$ -pe smp 1
#$ -l h_rt=72:00:00
#$ -l h_vmem=4G
#$ -q all.q
#$ -j y
#$ -o mlst_job_aa.log # Unique log file
#$ -wd $HOME/PROJECTS/GaTech/FCGR_classifier

# Define the input file for this specific job
genomes_list_part='$HOME/PROJECTS/GaTech/FCGR_classifier/genomes_part_aa'
# Define the output file for this specific job
output_results_file='$HOME/PROJECTS/GaTech/FCGR_classifier/mlst_results_aa.tsv'

echo "Starting MLST processing for genomes in: $genomes_list_part"

# Ensure the output file is empty/created before starting
rm -f "$output_results_file"

# Loop through each genome path listed in genomes_part_aa
while IFS= read -r genome_fasta_path; do
    singularity run mlst:2.23.0--hdfd78af_1 mlst \
        --scheme 'senterica_achtman_2' \
        "$genome_fasta_path" >> "$output_results_file"
done < "$genomes_list_part"