import argparse
from complexcgr import FCGRKmc
import numpy as np
import os
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt  # Import Matplotlib (will be used as a fallback)

def process_file(input_file, output_dir, kmer_size, img):
    """Processes a single k-mer counts file."""
    try:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_prefix = os.path.join(output_dir, base_name)

        print(f"Processing file: {input_file} (PID: {os.getpid()})")
        fcgr = FCGRKmc(kmer_size)
        arr = fcgr(input_file)

        # Generate the plot
        #plot_data = fcgr.plot(arr)  # Capture the plot data (if it returns anything)

        # Save the numpy array
        filename = f"{output_prefix}_k{kmer_size}.npy"
        np.save(filename,arr)
        print(f"  FCGR array saved to {filename} (PID: {os.getpid()})")

        # Try to save the image using fcgr.save_img
        if img:
            try:
                plot_filename_jpg = f"{output_prefix}_k{kmer_size}.jpg"
                fcgr.save_img(arr, path=plot_filename_jpg)
                print(f"  FCGR plot saved to {plot_filename_jpg} (PID: {os.getpid()})")
            except AttributeError:
                # If save_img doesn't exist, use Matplotlib as a fallback
                print(f"  Warning: fcgr.save_img() not found. Using Matplotlib to save plot.")
                plt.figure()
                fcgr.plot(arr)
                plot_filename_png = f"{output_prefix}_k{kmer_size}.png"
                plt.savefig(plot_filename_png)
                plt.close()
                print(f"  FCGR plot saved to {plot_filename_png} (PID: {os.getpid()})")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found. (PID: {os.getpid()})")
    except Exception as e:
        print(f"An error occurred while processing '{input_file}': {e} (PID: {os.getpid()})")

def main():
    parser = argparse.ArgumentParser(description="Generate FCGR from a list of k-mer counts files in parallel.")
    parser.add_argument("input_list_file", help="Path to a file containing a list of input k-mer counts files (one per line).")
    parser.add_argument("output_dir", help="Directory to save the output files.")
    parser.add_argument("-k", "--kmer_size", type=int, default=6, help="Size of the k-mer (default: 6).")
    parser.add_argument("-t", "--threads", type=int, default=4, help="Number of parallel threads/processes to use (default: 4).")
    parser.add_argument("-s","--save_img",type=bool,help="Save FCGRs as JPG images")
    args = parser.parse_args()

    kmer_size = args.kmer_size
    output_dir = args.output_dir
    num_threads = args.threads
    img = args.save_img

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(args.input_list_file, 'r') as f:
            input_files = [line.strip() for line in f if line.strip()]  # Read non-empty lines

        if not input_files:
            print(f"Warning: Input list file '{args.input_list_file}' is empty.")
            return

        with ProcessPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(process_file, file, output_dir, kmer_size, img) for file in input_files]
            for future in futures:
                future.result()  # Wait for all processes to complete

        print("All files processed.")

    except FileNotFoundError:
        print(f"Error: Input list file '{args.input_list_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
