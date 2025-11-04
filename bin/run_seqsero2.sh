#!/bin/bash

#################################################
# Same script applied to other genome list splits
#################################################

# Define the input file for this specific job
genomes_list='$HOME/PROJECTS/GaTech/FCGR_classifier/genomes_list.txt'

# Change into working directory
cd $HOME/PROJECTS/GaTech/FCGR_classifier/seqsero2_results

# Load module
module load seqsero2/1.3.1

# Loop through each genome path listed in genomes_list
while IFS= read -r genome_fasta_path; do
    genome_name_no_ext=$(basename "${genome_fasta_path%.fna}" | sed 's/\.fasta$//' | sed 's/\.fastq$//')
    SeqSero2_package.py \
    -i $genome_fasta_path \
    -t 4 \
    -p 4 \
    -d ./$genome_name_no_ext \
    -s \
    -m k
done < "$genomes_list"
