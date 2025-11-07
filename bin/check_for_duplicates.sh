#!bin/bash

echo "Finding dups..."

kmc_results_dir=$HOME/PROJECTS/GaTech/FCGR_classifier/salmonella_kmc5_arrays

find "$kmc_results_dir" -type f -exec md5sum {} + | sort | uniq -Dw32 > dups.txt

echo "complete!"
