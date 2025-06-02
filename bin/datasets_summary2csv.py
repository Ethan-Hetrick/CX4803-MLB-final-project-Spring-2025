import ijson
import itertools
import csv
import gc
import argparse

def json_to_csv_chunked_reduced(json_file_path, csv_file_path, chunk_size=1000):
    """
    Converts a JSON file containing 'reports.item' data into a CSV file,
    processing it in chunks to manage memory usage.
    
    Args:
        json_file_path (str): The path to the input JSON file.
        csv_file_path (str): The path to the output CSV file.
        chunk_size (int): The number of JSON items to process at a time.
    """
    with open(json_file_path, 'rb') as j, open(csv_file_path, 'w', newline='', encoding='utf-8') as c:
        items = ijson.items(j, 'reports.item')
        
        # Process the first chunk to write headers
        first_chunk = list(itertools.islice(items, chunk_size))
        if not first_chunk:
            print(f"No data found in '{json_file_path}' under 'reports.item'. CSV file will be empty.")
            return
        
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
        
        csv_writer = csv.writer(c)
        csv_writer.writerow(headers)
        
        # Write the first chunk's data
        for item in first_chunk:
            write_reduced_row(item, headers, csv_writer)
            
        # Process remaining chunks
        for chunk in iter(lambda: list(itertools.islice(items, chunk_size)), []):
            for item in chunk:
                write_reduced_row(item, headers, csv_writer)
            gc.collect() # Manually trigger garbage collection after each chunk

def write_reduced_row(item, headers, csv_writer):
    """
    Extracts specific data points from a JSON item and writes them as a row
    to the CSV file. Handles missing keys gracefully.
    
    Args:
        item (dict): The JSON item (dictionary) to process.
        headers (list): A list of headers to determine the order of data in the row.
        csv_writer (csv.writer): The CSV writer object to write the row.
    """
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
    csv_writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a JSON file with 'reports.item' structure to a CSV file."
    )
    parser.add_argument(
        "--in",
        dest="json_file_path",
        type=str,
        required=True,
        help="Path to the input JSON file.",
    )
    parser.add_argument(
        "--out",
        dest="csv_file_path",
        type=str,
        required=True,
        help="Path to the output CSV file.",
    )
    parser.add_argument(
        "--chunk_size",
        type=int,
        default=1000,
        help="Number of JSON items to process per chunk (default: 1000).",
    )

    args = parser.parse_args()

    json_to_csv_chunked_reduced(
        args.json_file_path,
        args.csv_file_path,
        args.chunk_size,
    )
    print(f"Successfully converted '{args.json_file_path}' to '{args.csv_file_path}'.")