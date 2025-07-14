# FCGR PROJECT NOTES

## Study design

We will evaluate various ML algorithms that use Chaos Game Representation for taxonomic ID of bacteria. Specifically, we are interested in whether or not these techniques can accurately classify strains of bacteria. We have two datasets from NCBI: Enterobacteriacae (~10K genomes), Salmonella (~500K genomes) 

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

Using kmc v3.2.4

### Step 1: Generate K-mer counts

```bash
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
#### Option 2

```bash
# Generate k-mer counts
singularity run kmc\:3.2.4--haf24da9_3 kmc \
    -v \
    -k6 \
    -m16 \
    -sm \
    -ci0 \
    -cs100000 \
    -b -t4 \
    -fm /scicomp/scratch/rqu4/salmonella/ncbi_dataset/data/GCA_000006945.2/GCA_000006945.2_ASM694v2_genomic.fna kmc-test.txt /tmp/kmc-tmp

#### Convert kmc indexes to readable format

```bash
# Convert them to readable format
singularity run kmc\:3.2.4--haf24da9_3 kmc_tools transform kmc-test.txt dump kmc-test.txt
```

### Step 2: Generate FCGRs

Using the python package [complexCGR](https://github.com/AlgoLab/complexCGR/tree/master?tab=readme-ov-file)

```python
# Install complexcgr
!pip install complexcgr

from complexcgr import FCGR
from complexcgr import FCGRKmc
import numpy as np

kmer = 6
fcgr = FCGRKmc(kmer)

arr = fcgr("/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/kmc-test.txt") # k-mer counts ordered in a matrix of 2^k x 2^k

# to visualize the distribution of k-mers. 
# Frequencies are scaled between [min, max] values. 
# White color corresponds to the minimum value of frequency
# Black color corresponds to the maximum value of frequency
fcgr.plot(arr)

# Save as a numpy array
np.save("/scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/test-fcgr.npy",arr)
```

### Parallelized version available in bin

```
python3 bin/fcgr.py \
    -k $kmer \
    -t $NSLOTS \
    $input_list \
    $outdir
```

## QC Genomes

Using QUAST v5.3.0

```bash
# Loop through each genome path listed in genomes_part_aa
while IFS= read -r genome_fasta_path; do
    genome_name_no_ext=$(basename "${genome_fasta_path%.fna}" | sed 's/\.fasta$//' | sed 's/\.fastq$//')

    singularity run /scicomp/home-pure/rqu4/PROJECTS/GaTech/FCGR_classifier/quast\:5.3.0--py313pl5321h5ca1c30_2 quast \
        --fast \
        --space-efficient \
        --memory-efficient \
        --threads 8 \
        --output-dir ./$genome_name_no_ext \
        "$genome_fasta_path"
done < "$genomes_list_part"
```

## Cull genomes

- Remove poor quality genomes (define what that is)
- Remove dumplicate genomes

## Batch genomes by subtype

- Keep strains/species with >=12 reps
- Split data into training, validation, and test datasets 80:20:20

## Train models

We will train 5 models for the class project trained on the FCGR representations made from assemblies. We will test it on 3 tasks: Genus and species (Enterobacteriaecea dataset), and strain level (Salmonella dataset)

1. A classic image classifier: resnet50, resNext101, etc.
    - Paper [here](https://ecoevorxiv.org/repository/view/6567/) describes methods
2. Unsupervised clustering approach: DeLUCS
    - https://github.com/millanp95/DeLUCS
3. PanSpace FCGR architecture
    - Publication: https://doi.org/10.1101/2025.03.19.644115
    - GitHub: https://github.com/pg-space/panspace
4. Vision transformer (ViT)
    - Paper [here](https://ecoevorxiv.org/repository/view/6567/) describes methods
5. Simple model: smashallow MLP, shallow 1D CNN, etc.
    - Paper above also has examples of this

## Benchmark comparison

- Use ANI with best cutoff (skani)

## Model Validation
 - Cross-entropy loss
- AUROC