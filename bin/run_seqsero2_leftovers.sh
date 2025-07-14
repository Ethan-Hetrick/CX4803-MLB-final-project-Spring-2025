#!/bin/bash

source /etc/profile

#$ -N seqsero2_leftovers
#$ -pe smp 4
#$ -l h_vmem=8G
#$ -q extralong.q
#$ -l h_rt=7:00:00:00
#$ -j y
#$ -o seqsero2_leftovers.log # Unique log file
#$ -wd /scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier

# Define the input file for this specific job
genomes_list='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/seqsero2_leftovers.txt'

# Define the *absolute base path* that contains the GCA_* directories.
# This variable should reflect '/scicomp/scratch/rqu4/salmonella/ncbi_dataset/data/'
GENOME_BASE_PATH="/scicomp/scratch/rqu4/salmonella/ncbi_dataset/data/"

# Change into working directory
cd /scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/seqsero2_results_leftovers

# Load module
module load seqsero2/1.3.1

set -x
# Loop through each genome filename (e.g., GCA_001441225.1_ASM144122v1_genomic.fna)
while IFS= read -r genome_filename; do
    # Ensure the filename is not empty
    [[ -z "$genome_filename" ]] && continue

    # Extract the GCA accession number (which is the directory name) from the filename.
    # This assumes the GCA_XXXXXXX.X part is always at the beginning and ends at the first underscore or after the .X
    # For GCA_001441225.1_ASM144122v1_genomic.fna, we want GCA_001441225.1
    accession_dir_name=$(echo "$genome_filename" | cut -d'_' -f1-2) # Gets GCA_001441225.1 (assuming this pattern consistently gives the directory name)

    # Construct the full absolute path to the .fna file
    genome_fasta_path="${GENOME_BASE_PATH}${accession_dir_name}/${genome_filename}"

    # Verify the file actually exists before proceeding
    if [[ ! -f "$genome_fasta_path" ]]; then
        echo "Error: File not found at ${genome_fasta_path}. Skipping."
        continue
    fi

    # Extract genome name without extensions for output directory
    genome_name_no_ext=$(basename "${genome_filename}" .fna | sed 's/\.fasta$//' | sed 's/\.fastq$//')

    # Execute SeqSero2_package.py with the full path
    SeqSero2_package.py \
        -i "${genome_fasta_path}" \
        -t 4 \
        -p 4 \
        -d "./${genome_name_no_ext}" \
        -s \
        -m k
done < "$genomes_list"
