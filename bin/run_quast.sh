#!/bin/bash

#################################################
# Same script applied to other genome list splits
#################################################

# Define the input file for this specific job
genomes_list_part='$HOME/PROJECTS/GaTech/FCGR_classifier/genomes_part_aa'

# Change into working directory
cd $HOME/PROJECTS/GaTech/FCGR_classifier/quast_results

# Loop through each genome path listed in genomes_part_aa
while IFS= read -r genome_fasta_path; do
    genome_name_no_ext=$(basename "${genome_fasta_path%.fna}" | sed 's/\.fasta$//' | sed 's/\.fastq$//')

    singularity run $HOME/PROJECTS/GaTech/FCGR_classifier/quast\:5.3.0--py313pl5321h5ca1c30_2 quast \
        --fast \
        --space-efficient \
        --memory-efficient \
        --threads 8 \
        --output-dir ./$genome_name_no_ext \
        "$genome_fasta_path"
done < "$genomes_list_part"
