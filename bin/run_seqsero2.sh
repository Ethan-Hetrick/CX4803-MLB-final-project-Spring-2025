#!/bin/bash

source /etc/profile

#$ -N seqsero2
#$ -pe smp 4
#$ -l h_vmem=8G
#$ -q extralong.q
#$ -l h_rt=7:00:00:00
#$ -j y
#$ -o seqsero2.log # Unique log file
#$ -wd $HOME/PROJECTS/GaTech/FCGR_classifier

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