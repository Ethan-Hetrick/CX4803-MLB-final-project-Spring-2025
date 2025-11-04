#!/bin/bash

mkdir /tmp/kmc_tmp

#################################################
# Same script applied to other genome list splits
#################################################

# Define the input file for this specific job
genomes_list_part='$HOME/PROJECTS/GaTech/FCGR_classifier/genomes_part_aa'
# Define the output file for this specific job
results_dir='$HOME/PROJECTS/GaTech/FCGR_classifier/kmc_results'

# Loop through each genome path listed in genomes_part_aa
while IFS= read -r genome_fasta_path; do
    filename=$(basename "$genome_fasta_path")
    genome="${filename%.*}"
    singularity run $HOME/PROJECTS/GaTech/FCGR_classifier/images/kmc\:3.2.4--haf24da9_3 \
    	kmc \
        -k7 \
        -m16 \
        -sm \
        -fm \
        -ci0 \
        -cs1000000000 \
        -t4 \
        $genome_fasta_path \
        $results_dir/${genome}_k7 \
        /tmp/kmc_tmp
done < "$genomes_list_part"
