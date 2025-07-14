'''fastANI shared genome fraction vs ANI correlation.

This script reads fastANI output (modified to accept custom format) and builds
a scatter plot with the mean, median and correlation. The y-axis is the
shared genome fraction and the x-axis is the ANI. The shared genome fraction
is taken directly from the 'AF' column (converted to a 0-1 ratio if it's a percentage).

mean, median and correlation of ANI values (x-axis) and Shared / Total
Fragments (y-axis). Returns a scatter plot of the data as a PDF file
or displays it in Jupyter Notebook.

This script requires python 3.6+ and the following modules:

    * matplotlib
    * numpy
    * pandas
    * seaborn
    * scipy
    * pygam - https://pygam.readthedocs.io/
    * datashader (for density scatter plot if > 10000 genome pairs)

-------------------------------------------
Author :: Roth Conrad (Original)
Modified :: Gemini (for custom input format)
Email :: rotheconrad@gatech.edu
GitHub :: https://github.com/rotheconrad
Date Created :: April 2022
License :: GNU GPLv3
Copyright 2022 Roth Conrad
All rights reserved
-------------------------------------------
'''

import argparse, sys, random
from collections import defaultdict
import matplotlib
import matplotlib.pyplot as plt
import numpy as np, pandas as pd; np.random.seed(0)
import seaborn as sns; sns.set(style="white", color_codes=True)
from scipy.stats import pearsonr as corr
from pygam import LinearGAM

# Attempt to import datashader for large datasets, handle if not installed
try:
    import datashader as ds
    from datashader.mpl_ext import dsshow
    _DATASHADER_AVAILABLE = True
except ImportError:
    _DATASHADER_AVAILABLE = False
    print("Warning: datashader not found. For large datasets (>10000 points), "
          "consider installing it for better performance and visualization. "
          "(`pip install datashader bokeh holoviews`)")


class TickRedrawer(matplotlib.artist.Artist):
    """Artist to redraw ticks."""
    __name__ = "ticks"
    zorder = 10

    @matplotlib.artist.allow_rasterization
    def draw(self, renderer: matplotlib.backend_bases.RendererBase) -> None:
        """Draw the ticks."""
        if not self.get_visible():
            self.stale = False
            return

        renderer.open_group(self.__name__, gid=self.get_gid())

        for axis in (self.axes.xaxis, self.axes.yaxis):
            loc_min, loc_max = axis.get_view_interval()

            for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                if tick.get_visible() and loc_min <= tick.get_loc() <= loc_max:
                    for artist in (tick.tick1line, tick.tick2line):
                        artist.draw(renderer)

        renderer.close_group(self.__name__)
        self.stale = False


def read_input_file_as_df(ani_file):
    """Reads the input file into a pandas DataFrame."""
    print(f"\nReading data from file: {ani_file}")
    try:
        # Using sep='\s+' for robust whitespace separation
        # header=None and names=['genome1', 'genome2', 'ANI', 'AF'] assumes no header row
        df = pd.read_csv(ani_file, sep='\s+', header=None,
                         names=['genome1', 'genome2', 'ANI', 'AF'])

        # Explicitly convert 'ANI' and 'AF' columns to numeric
        # 'errors='coerce' will turn non-numeric values into NaN
        df['ANI'] = pd.to_numeric(df['ANI'], errors='coerce')
        df['AF'] = pd.to_numeric(df['AF'], errors='coerce')

        # Drop rows where ANI or AF became NaN due to coercion
        original_rows = len(df)
        df.dropna(subset=['ANI', 'AF'], inplace=True)
        dropped_rows = original_rows - len(df)
        if dropped_rows > 0:
            print(f"Warning: Dropped {dropped_rows} rows due to non-numeric 'ANI' or 'AF' values.")

        print(f"Successfully loaded {len(df)} rows.")
        return df
    except Exception as e:
        print(f"Error reading file: {e}")
        print("Please ensure the file is correctly formatted with columns: genome1, genome2, ANI, AF")
        sys.exit(1)


def process_df_for_plotting(df, xmin, xmax):
    """Processes the DataFrame to prepare it for plotting."""
    # Convert AF (percentage) to a ratio (0-1)
    # Check if AF is already a ratio or percentage
    if df['AF'].max() > 1.0:
        df['AF_ratio'] = df['AF'] / 100.0
    else:
        df['AF_ratio'] = df['AF'] # Assume it's already a ratio

    data_dict = {'gpair': [], 'species': [], 'xs': [], 'ys': []}

    # Use a set to track unique genome pairs to avoid duplicates if present in input
    processed_pairs = set()

    for index, row in df.iterrows():
        qry_genome = str(row['genome1'])
        ref_genome = str(row['genome2'])

        # Sort genome names to ensure consistent pair identification (genomeA-genomeB vs genomeB-genomeA)
        names = sorted([qry_genome, ref_genome])
        gname = '-'.join(names)

        # Skip self-matches or duplicate pairs if they exist
        if qry_genome == ref_genome or gname in processed_pairs:
            continue
        processed_pairs.add(gname)

        ani = float(row['ANI'])
        ratio = float(row['AF_ratio'])

        # Attempt to extract species from genome1, fallback to a generic name
        # This assumes format like GCF_000005845.2_ASM584v2_genomic
        try:
            # Extract part after second underscore and before first dot
            species = qry_genome.split('_')[2].split('.')[0]
        except IndexError:
            species = "Unknown_Species" # Fallback if format doesn't match

        data_dict['gpair'].append(gname)
        data_dict['species'].append(species)
        data_dict['xs'].append(ani)
        data_dict['ys'].append(ratio)

    df_plot = pd.DataFrame(data_dict)
    df_plot = df_plot[df_plot['xs'] <= xmax]
    df_plot = df_plot[df_plot['xs'] >= xmin]
    n = len(df_plot)

    # Compute and print some things
    total_species = set(data_dict['species'])
    filtered_species = set(df_plot['species'].unique())
    diff_species = total_species - filtered_species
    print(f'\nTotal species in file: {len(total_species)}')
    print(f'Species between {xmin}-{xmax}% ANI: {len(filtered_species)}')
    print(f'Species not included: {diff_species}')

    # The original count_genomes and get_ratios functions relied on fastANI's specific
    # fragment counts (columns 3 and 4) which are not directly available in your format.
    # We will skip printing these specific metrics unless you provide a way to derive them.
    # total_genomes = count_genomes(df_plot)
    # ratios = get_ratios(df_plot)
    # print(f'\n\nGenome pairs between {xmin}-{xmax}% ANI: {total_genomes}')
    # print(f'Genome pair ratio 100%/remaining: {ratios[0]}')
    # print(f'Genome pair ratio >99.5%/remaining: {ratios[1]}')
    # print(f'Genome pair ratio >99%/remaining: {ratios[2]}')

    return df_plot, n


def gather_stats(df):
    """Computes correlation, mean, and median on df columns xs and ys """

    # Compute Pearson Correlation Coefficient
    print("\nCalculating statistics.")
    pcorr = corr(df['xs'], df['ys'])

    # Compute ANI mean and median
    ani_mean = np.mean(df['xs'])
    ani_median = np.median(df['xs'])
    frag_mean = np.mean(df['ys'])
    frag_median = np.median(df['ys'])

    # Compile dictionary
    df_stats = {
        'pcorr': pcorr,
        'ani_mean': ani_mean,
        'ani_median': ani_median,
        'frag_mean': frag_mean,
        'frag_median': frag_median
        }

    print(f"\nANI mean: {ani_mean:.2f}\nANI median: {ani_median:.2f}")
    print(f"\nFrag mean: {frag_mean:.2f}\nFrag median: {frag_median:.2f}")

    return df_stats


def fastANI_scatter_plot(
        df, n, species_name, outfile, xmin, xmax, xstep, p , a, z, g, c,
        display_plot=True # New parameter for Jupyter display
        ):
    """Takes the data and builds the plot"""

    # Gather Stats
    df_stats = gather_stats(df)

    stats_line = (
        f"Pearson r: {round(df_stats['pcorr'][0], 2)}\n"
        f"p value: {round(df_stats['pcorr'][1], 2)}"
        )

    # Set Colors and markers
    grid_color = '#d9d9d9'
    main_color = '#933b41'
    second_color = '#737373'
    vline_color = '#000000'
    color = '#252525'
    marker = '.' #'o'

    # build plot
    gg = sns.JointGrid(x="xs", y="ys", data=df)

    # x margin hist plot
    sns.histplot(
            x=df["xs"],
            ax=gg.ax_marg_x,
            legend=False,
            color=color,
            stat='probability'
            )
    # y margin hist plot
    sns.histplot(
            y=df["ys"],
            ax=gg.ax_marg_y,
            legend=False,
            color=color,
            stat='probability'
            )
    # main panel scatter plot
    if z and _DATASHADER_AVAILABLE: # density scatter plot with datashader
        print('\nComputing plot densities.')
        # Datashader expects unscaled data, so we pass df directly
        # and specify the column names.
        dsartist = dsshow(
                            df,
                            ds.Point("xs", "ys"),
                            ds.count(),
                            norm="log",
                            aspect="auto",
                            ax=gg.ax_joint,
                            width_scale=10.,
                            height_scale=10.
                            )
        dsartist.zorder = 2.5

    else: # regular scatter plot or datashader not available
        print('\nPlotting data.')
        gg.ax_joint.plot(
                df["xs"],
                df["ys"],
                marker,
                ms=p,
                alpha=a,
                color=color,
                )

    if g:
        # Trendline with pyGAM
        print('\nCalculating trendline with pyGAM.')
        X = df["xs"].to_numpy()
        X = X[:, np.newaxis]
        y = df["ys"].to_list()

        gam = LinearGAM().gridsearch(X, y)
        XX = gam.generate_X_grid(term=0, n=500)

        gg.ax_joint.plot(
                            XX,
                            gam.predict(XX),
                            color='#FCEE21',
                            linestyle='--',
                            linewidth=1.0,
                            zorder=2.8
                            )
        gg.ax_joint.plot(
                            XX,
                            gam.prediction_intervals(XX, width=0.95),
                            color='#CBCB2C',
                            linestyle='--',
                            linewidth=1.0,
                            zorder=2.8
                            )
        r2 = gam.statistics_['pseudo_r2']['explained_deviance']
        GAM_line = f"GAM Pseudo R-Squared: {r2:.4f}"
        gg.ax_joint.text(
            0.75, 0.1, GAM_line,
            fontsize=10, color=second_color,
            verticalalignment='top', horizontalalignment='right',
            transform=gg.ax_joint.transAxes
            )


    # plot title, labels, text
    species_name_formatted = ' '.join(species_name.split('_'))
    ptitle = f'{species_name_formatted} (n={n})'
    gg.ax_marg_x.set_title(ptitle, fontsize=18, y=1.02)

    gg.ax_joint.set_xlabel(
        'Average nucleotide identity (%)',
        fontsize=12, y=-0.02
        )
    gg.ax_joint.set_ylabel(
        'Shared genome fraction', # 'Shared / total fragments'
        fontsize=12, x=-0.02
        )
    gg.ax_joint.text(
        0.25, 0.99, stats_line,
        fontsize=10, color=second_color,
        verticalalignment='top', horizontalalignment='right',
        transform=gg.ax_joint.transAxes
        )

    # set the axis parameters / style
    hstep = xstep/10
    gg.ax_joint.set_xticks(np.arange(xmin, xmax+hstep, xstep))
    gg.ax_joint.set_xlim(left=xmin-hstep, right=xmax+hstep)

    # Y-axis limits are now 0-1 for ratio
    gg.ax_joint.set_yticks(np.arange(0.6, 1.1, 0.1))
    gg.ax_joint.set_ylim(bottom=0.58, top=1.02)
    gg.ax_joint.tick_params(axis='both', labelsize=12)
    gg.ax_joint.tick_params(
        axis='both', which='major', direction='inout', color='k',
        width=2, length=6, bottom=True, left=True, zorder=3
        )

    # set grid style
    gg.ax_joint.yaxis.grid(
        which="major", color='#d9d9d9', linestyle='--', linewidth=1
        )
    gg.ax_joint.xaxis.grid(
        which="major", color='#d9d9d9', linestyle='--', linewidth=1
        )
    gg.ax_joint.set_axisbelow(True)
    gg.ax_joint.add_artist(TickRedrawer())

    if c:
        # Plot mean and median
        _ = gg.ax_joint.axvline(
            x=df_stats['ani_mean'], ymin=0, ymax=1,
            color=vline_color, linewidth=2, linestyle='--',
            label='Mean'
            )
        _ = gg.ax_joint.axhline(
            y=df_stats['frag_mean'], xmin=0, xmax=1,
            color=vline_color, linewidth=2, linestyle='--',
            )
        _ = gg.ax_joint.axvline(
            x=df_stats['ani_median'], ymin=0, ymax=1,
            color=vline_color, linewidth=2, linestyle=':',
            label='Median'
            )
        _ = gg.ax_joint.axhline(
            y=df_stats['frag_median'], xmin=0, xmax=1,
            color=vline_color, linewidth=2, linestyle=':',
            )

        # Build legend for mean and median
        gg.ax_joint.legend(
            loc='lower left',
            fontsize=12,
            markerscale=1.5,
            numpoints=1,
            frameon=False,
            ncol=2
            )

    # adjust layout, save, and close
    gg.fig.set_figwidth(7)
    gg.fig.set_figheight(5)

    if display_plot:
        plt.show()
        plt.close(gg.fig) # Close the figure associated with JointGrid
    else:
        gg.savefig(f'{outfile}_{species_name}.pdf')
        plt.close(gg.fig)


def main():

    # Configure Argument Parser
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    parser.add_argument(
        '-i', '--input_file',
        help='Please specify the input file (e.g., fastANI_output.txt)!',
        metavar='',
        type=str,
        required=True
        )
    parser.add_argument(
        '-o', '--output_file_prefix',
        help='Please specify the output file prefix (e.g., my_plots)!',
        metavar='',
        type=str,
        default='fastANI_plot', # Default for convenience
        required=False
        )
    parser.add_argument(
        '-xmin', '--xaxis_minimum',
        help='OPTIONAL: Minimum value to plot on x-axis. (Default=95.0)',
        metavar='',
        type=float,
        default=95.0,
        required=False
        )
    parser.add_argument(
        '-xmax', '--xaxis_maximum',
        help='OPTIONAL: Maximum value to plot on x-axis. (Default=100.0)',
        metavar='',
        type=float,
        default=100.0,
        required=False
        )
    parser.add_argument(
        '-t', '--xaxis_step_size',
        help='OPTIONAL: X-axis ticks step increment. (Default=1.0)',
        metavar='',
        type=float,
        default=1.0,
        required=False
        )
    parser.add_argument(
        '-p', '--point_size',
        help='OPTIONAL: Size of the plotted points (Default=4.0). Ignored if datashader is used.',
        metavar='',
        type=float,
        default=4.0,
        required=False
        )
    parser.add_argument(
        '-a', '--point_alpha',
        help='OPTIONAL: Alpha value of the plotted points (Default=0.10). Ignored if datashader is used.',
        metavar='',
        type=float,
        default=0.10,
        required=False
        )
    parser.add_argument(
        '-c', '--add_cross_hairs',
        help='OPTIONAL: Add mean/median cross hairs (Set to True). (Default=None).',
        metavar='',
        type=str,
        default=None,
        required=False
        )
    parser.add_argument(
        '-g', '--generate_GAM_trendline',
        help='OPTIONAL: Add trendline with GAM (Set to True). (Default=None).',
        metavar='',
        type=str,
        default=None,
        required=False
        )
    parser.add_argument(
        '-r', '--random_subsample',
        help='OPTIONAL: Set > 1 to plot subsample of r genomes per species. (Default=1, no subsampling).',
        metavar='',
        type=int,
        default=1,
        required=False
        )
    parser.add_argument(
        '-e', '--repeat_subsamples',
        help='OPTIONAL: Repeat subsampling this many times (Default=100). Only applies if -r > 1.',
        metavar='',
        type=int,
        default=100,
        required=False
        )
    parser.add_argument(
        '-s', '--single_species',
        help='OPTIONAL: Set to True for single species plots (Default=None).',
        metavar='',
        type=str,
        default=None,
        required=False
        )
    parser.add_argument(
        '-l', '--all_species',
        help='OPTIONAL: Set to True for all species one plot (Default=None).',
        metavar='',
        type=str,
        default=None,
        required=False
        )
    parser.add_argument(
        '--display',
        help='OPTIONAL: Set to True to display plot in interactive environment (e.g., Jupyter). (Default=False).',
        action='store_true', # This makes it a boolean flag
        required=False
        )
    args=vars(parser.parse_args())

    # Do what you came here to do:
    print('\n\nRunning Script...\n')

    # define parameters
    infile = args['input_file']
    outfile = args['output_file_prefix']
    single_species = args['single_species']
    all_species = args['all_species']
    xmin = args['xaxis_minimum']
    xmax = args['xaxis_maximum']
    xstep = args['xaxis_step_size']
    p = args['point_size']
    a = args['point_alpha']
    z = None # datashader flag will be set based on data size
    c = True if args['add_cross_hairs'] and args['add_cross_hairs'].lower() == 'true' else False
    g = True if args['generate_GAM_trendline'] and args['generate_GAM_trendline'].lower() == 'true' else False
    r = args['random_subsample']
    e = args['repeat_subsamples']
    display_plot = args['display'] # Use the new display argument

    # test params
    if not all_species and not single_species:
        print(
            '\nNo option specified. Please set -s True, -l True or both to True.\n\n'
            )
        sys.exit(1)

    # Read the data using pandas
    raw_df = read_input_file_as_df(infile)

    # Process the data for plotting
    df_plot, n = process_df_for_plotting(raw_df, xmin, xmax)

    # build the plot
    if all_species:
        # Use datashader if available and data is large
        if n > 10000 and _DATASHADER_AVAILABLE: z = True
        else: z = False # Force False if datashader not available
        fastANI_scatter_plot(
            df_plot, n, 'All_species', outfile, xmin, xmax, xstep, p, a, z, g, c,
            display_plot=display_plot
            )
    if single_species:
        for species in df_plot['species'].unique():
            print(f'\tPlotting {species} ...')
            dfx = df_plot[df_plot['species'] == species]
            n_species = len(dfx)
            
            # Use datashader if available and data is large for individual species
            if n_species > 10000 and _DATASHADER_AVAILABLE: z = True
            else: z = False # Force False if datashader not available

            if n_species >= 20: # Minimum points for plotting
                fastANI_scatter_plot(
                    dfx, n_species, species, outfile, xmin, xmax, xstep, p, a, z, g, c,
                    display_plot=display_plot
                    )
            else:
                print(f"Skipping {species}: Not enough data points ({n_species} < 20).")
                                        
    print(f'\n\nComplete success space cadet!! Finished without errors.\n\n')

if __name__ == "__main__":
    main()