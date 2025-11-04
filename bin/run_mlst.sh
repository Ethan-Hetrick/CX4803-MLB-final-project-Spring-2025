#!/bin/bash

#################################################
# Same script applied to other genome list splits
#################################################

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
