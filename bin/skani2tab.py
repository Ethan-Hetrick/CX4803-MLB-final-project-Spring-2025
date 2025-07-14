#!/usr/bin/env python

import argparse
import sys
import os.path
import pandas as pd

def skani2tab(ani_file: str, af_file: str, out: str) -> str:
    """
    Replace this with your actual function logic.
    """
    
    c=0
    ani_table = {'genome1': [], 'genome2': [], 'ANI': []}
    genomes_list = list()

    #ani_df = Dataframe.pd()

    # Open matrix file
    with open(ani_file, "r") as ani_matrix:
        for i, line in enumerate(ani_matrix):
            # Skip first line
            if c == 0:
                c +=1
                continue
            
            row = line.strip().split("\t")
            name = os.path.basename(row[0]).strip(".fasta")
            
            genomes_list.append(name)
            
            for i2, ani_val in enumerate(row[1:]):
                # skip ANI = 0
                if ani_val != '0.00':
                    ani_table['genome1'].append(min(name, genomes_list[i2]))
                    ani_table['genome2'].append(max(name, genomes_list[i2]))
                    ani_table['ANI'].append(ani_val)

    #Make dataframe
    ani_df = pd.DataFrame(ani_table)
    
    genomes_list = list()
    af_table = {'genome1': [], 'genome2': [], 'AF': []}


    with open(af_file, "r") as af_matrix:
        for line_num, line in enumerate(af_matrix):
            
            row = line.strip().split("\t")
            
            if line_num == 0:
                
                for name in row:
                    genomes_list.append(name)
                    
            else:
                for i, af in enumerate(row):
                    af_table['genome1'].append(min(genomes_list[i], genomes_list[line_num-1]))
                    af_table['genome2'].append(max(genomes_list[i], genomes_list[line_num-1]))
                    af_table['AF'].append(af)
            

    #Make dataframe
    af_df = pd.DataFrame(af_table)
    
    df_merged = pd.merge(ani_df, af_df, on=['genome1', 'genome2'], how='left')
    
    df_merged.to_csv(out, sep='\t', index=False)
    

if __name__ == "__main__":
    # Argument parser
    parser = argparse.ArgumentParser(description="Description of your script")

    # Input file argument
    parser.add_argument("--ani_file", help="Input file path")
    
    # Input file argument
    parser.add_argument("--af_file", help="Input file path")

    # Output file argument
    parser.add_argument("--output", help="Output file path")

    # Parse arguments
    args = parser.parse_args()

    # Run the main function
    skani2tab(args.ani_file, args.af_file, args.output)