import ijson
import itertools
import csv
import gc

def json_to_csv_chunked_reduced(json_file_path, csv_file_path, chunk_size=1000):
    with open(json_file_path, 'rb') as j, open(csv_file_path, 'a', newline='', encoding='utf-8') as c:
        items = ijson.items(j, 'reports.item')
        first_chunk = list(itertools.islice(items, chunk_size))
        if not first_chunk: return
        headers = [
            "accession",
            "assembly_stats_contig_l50",
            "assembly_stats_contig_n50",
            "assembly_stats_gc_count",
            "assembly_stats_gc_percent",
            "assembly_stats_genome_coverage",
            "assembly_stats_number_of_component_sequences",
            "assembly_stats_number_of_contigs",
            "assembly_stats_number_of_scaffolds",
            "assembly_stats_scaffold_l50",
            "assembly_stats_scaffold_n50",
            "assembly_stats_total_number_of_chromosomes",
            "assembly_stats_total_sequence_length",
            "assembly_stats_total_ungapped_length",
            "organism_common_name",
            "organism_infraspecific_names_isolate",
            "organism_infraspecific_names_strain",
            "organism_organism_name",
            "organism_tax_id",
        ]
        csv.writer(c).writerow(headers)
        for item in first_chunk: write_reduced_row(item, headers, c)
        for chunk in iter(lambda: list(itertools.islice(items, chunk_size)), []):
            for item in chunk: write_reduced_row(item, headers, c)
            gc.collect()

def write_reduced_row(item, headers, csv_file):
    row = [
        item.get("accession"),
        item.get("assembly_stats", {}).get("contig_l50"),
        item.get("assembly_stats", {}).get("contig_n50"),
        item.get("assembly_stats", {}).get("gc_count"),
        item.get("assembly_stats", {}).get("gc_percent"),
        item.get("assembly_stats", {}).get("genome_coverage"),
        item.get("assembly_stats", {}).get("number_of_component_sequences"),
        item.get("assembly_stats", {}).get("number_of_contigs"),
        item.get("assembly_stats", {}).get("number_of_scaffolds"),
        item.get("assembly_stats", {}).get("scaffold_l50"),
        item.get("assembly_stats", {}).get("scaffold_n50"),
        item.get("assembly_stats", {}).get("total_number_of_chromosomes"),
        item.get("assembly_stats", {}).get("total_sequence_length"),
        item.get("assembly_stats", {}).get("total_ungapped_length"),
        item.get("organism", {}).get("common_name"),
        item.get("organism", {}).get("infraspecific_names", {}).get("isolate"),
        item.get("organism", {}).get("infraspecific_names", {}).get("strain"),
        item.get("organism", {}).get("organism_name"),
        item.get("organism", {}).get("tax_id"),
    ]
    csv.writer(csv_file).writerow(row)

json_to_csv_chunked_reduced(
    "salmonella_dataset.json",
    "salmonella_dataset.csv",
)
