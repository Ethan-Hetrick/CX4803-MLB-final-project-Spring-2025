#!/bin/bash

source /etc/profile

#$ -N seqsero2_job_leftover_3
#$ -pe smp 12
#$ -l h_rt=3:00:00:00
#$ -l h_vmem=32G
#$ -q all.q
#$ -j y
#$ -o seqsero2_job_leftover_3.log
#$ -wd /scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier

module load seqsero2/1.3.1

genomes_list='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/seqsero2_leftovers.txt'

cd /scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/seqsero2_leftovers_3

cat "$genomes_list" | xargs -P "$NSLOTS" -I {} bash -c '
  genome_full_path="$1"

  genome_filename=$(basename "$genome_full_path")
  accession_dir_name=$(echo "$genome_filename" | cut -d'_' -f1-2)
  genome_name_no_ext=$(basename "${genome_filename}" .fna)

  mkdir -p "./${genome_name_no_ext}"

  SeqSero2_package.py \
    -i "${genome_full_path}" \
    -t 4 \
    -p 1 \
    -d "./${genome_name_no_ext}" \
    -s \
    -m k
' _ {}