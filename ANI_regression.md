# ANI vs. FCGR similary regression analysis

## Data download

Performed on 12/16/2025

```bash
# Download enterobacteriacea reference genomes
datasets download genome taxon "Enterobacteriaceae" --dehydrated --filename enterobacteriaceae.zip --assembly-version 'latest' --api-key "${NCBI_API_KEY}" --mag "exclude" --exclude-atypical --assembly-source "RefSeq" --assembly-level "complete"

# Unzip
unzip enterobacteriaceae.zip

# Rehydrate
datasets rehydrate --api-key "${NCBI_API_KEY}" --directory ./ --max-workers 24

# Download genome summary
datasets summary genome taxon "Enterobacteriaceae" --assembly-version 'latest' --api-key "${NCBI_API_KEY}" --mag "exclude" --exclude-atypical --assembly-source "RefSeq" --assembly-level "complete" > enterobacteriaceae_summary.json

# Generate summary using dataformat
dataformat tsv genome --package ./enterobacteriaceae.zip > enterobacteriaceae_summary.tsv

# Create sample list
find $(realpath ncbi_dataset/) -name "*.fna" -type f > genome_list.txt
```

## Run fastANI

```bash
fastANI --threads 16 --refList genome_list.txt --queryList genome_list.txt --output fastANI_output --matrix
```

## Generate FCGRs

```bash
# Step 1: Count kmers
while IFS= read -r genome_fasta_path; do
    filename=$(basename "$genome_fasta_path")
    genome="${filename%.*}"
    singularity run ./images/kmc\:3.2.4--haf24da9_3 \
        kmc \
        -k7 \
        -m16 \
        -sm \
        -fm \
        -ci0 \
        -cs1000000000 \
        -t16 \
        $genome_fasta_path \
        $results_dir/${genome}_k7 \
        /tmp/kmc_tmp
done < "$genomes_list_part"

# Step 2: dump kmer counts
do singularity run ./images/kmc\:3.2.4--haf24da9_3 kmc_tools transform kmc/$(basename -s '.kmc_pre' -a $db) dump kmc/$(basename -s '.kmc_pre' -a $db).txt; done
```

## Downsampling for ANI

Decided to downsample since fastANI takes a long time to process

```bash
# Downsample
sort -R genome_list.txt | head -1000
```

Re-ran fastANI as shown above with downsampled. Running with skani for a comparison

```bash
skani triangle -s 75 -t 24 --no-learned-ani -E $(cat genome_list_1000.txt) > skani_results.txt
```