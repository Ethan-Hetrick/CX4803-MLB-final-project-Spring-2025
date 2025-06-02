# FCGR PROJECT NOTES

## Download Salmnoella dataset

### Download summary

```bash
# Download summary
datasets summary genome taxon "Salmonella" > salmonella_dataset.json

# Convert to CSV
new_json2csv.py # Had to change path. Note: will add args for this script

# Print out basic stats of genomes
$ head -1 ../salmonella_dataset.csv
accession,assembly_stats_contig_l50,assembly_stats_contig_n50,assembly_stats_gc_count,assembly_stats_gc_percent,assembly_stats_genome_coverage,assembly_stats_number_of_component_sequences,assembly_stats_number_of_contigs,assembly_stats_number_of_scaffolds,assembly_stats_scaffold_l50,assembly_stats_scaffold_n50,assembly_stats_total_number_of_chromosomes,assembly_stats_total_sequence_length,assembly_stats_total_ungapped_length,organism_common_name,organism_infraspecific_names_isolate,organism_infraspecific_names_strain,organism_organism_name,organism_tax_id
$ wc -l ../salmonella_dataset.csv # number of samples in full file
615873
$ grep 'bongori' ../salmonella_dataset.csv | wc -l # number of S. bongori
129
$ grep 'enterica' ../salmonella_dataset.csv | wc -l # number of S. enterica
613224
cut -d',' -f13 ../salmonella_dataset.csv | tail -n +2 | awk 'BEGIN{i = 0}{i+=$0}END{print i/1000000000 " GB"}' # Estimated storage req
2971.33 GB
$ grep -v 'bongori' ../salmonella_dataset.csv | cut -d',' -f13 | tail -n +2 | awk 'BEGIN{i = 0}{i+=$0}END{print i/1000000000 " GB"}' # without bongori
2970.74 GB
```

### Download genomes

Downloaded on 5/30/2025

```bash
datasets download genome taxon "Salmonella" \
    --dehydrated \
    --filename ./salmonella_dataset.zip \
    --no-progressbar \pwd
    --assembly-version 'latest' \
    --api-key 'd3a15334f0efb8e31c99564bd4e56499fd08'

unzip ./salmonella_dataset.zip

datasets rehydrate \
    --directory ./ \
    --no-progressbar \
    --api-key 'd3a15334f0efb8e31c99564bd4e56499fd08'
```

## Perform subtyping

### Run mlst

I split the inputs into 4 parts to run in parallel (`split -n l/4 genomes_list.txt genomes_part_`) and will concatenate at the end

```bash
# Define the input file for this specific job
genomes_list_part='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/genomes_part_ad'
# Define the output file for this specific job
output_results_file='/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/mlst_results_ad.tsv'

echo "Starting MLST processing for genomes in: $genomes_list_part"

# Ensure the output file is empty/created before starting
rm -f "$output_results_file"

# Loop through each genome path listed in genomes_part_ad
while IFS= read -r genome_fasta_path; do
    singularity run mlst:2.23.0--hdfd78af_1 mlst \
        --scheme 'senterica_achtman_2' \
        "$genome_fasta_path" >> "$output_results_file"
done < "$genomes_list_part"
```

## Generate FCGRs

### Step 1: Generate K-mer counts

```
while IFS= read -r line; do
    filename=$(basename "$line")
    genome="${filename%.*}"
    kmc \
        -k11 \
        -m256 \
        -sm \
        -fm \
        -ci0 \
        -cs10000 \
        -t16 \
        $line \
        ${genome}_k11 \
        ~/543/kmc11/
done < "assembly_list2.txt"
```

