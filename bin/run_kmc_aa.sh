#!/bin/bash

source /etc/profile

#$ -N kmc_job_aa # Unique name for this job
#$ -pe smp 4
#$ -l h_rt=72:00:00
#$ -l h_vmem=16G
#$ -q all.q
#$ -j y
#$ -o mlst_job_aa.log # Unique log file
#$ -wd /scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier

mkdir /tmp/kmc_tmp

# Define the input file for this specific job
genomes_list_part='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/genomes_part_aa'
# Define the output file for this specific job
results_dir='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/kmc_results'

# Loop through each genome path listed in genomes_part_aa
while IFS= read -r genome_fasta_path; do
    filename=$(basename "$genome_fasta_path")
    genome="${filename%.*}"
    singularity run /scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/images/kmc\:3.2.4--haf24da9_3 \
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
