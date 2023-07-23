from convert_all_chatgpt import build_droid_profile, batch_convert
import argparse

def main(working_dir, target_dir):
    """
    Main function to build the DROID profile for a directory and perform batch conversion.
    """

    # Build the DROID profile for the working directory
    droid_profile = build_droid_profile(working_dir)
    
    # Perform batch conversion on the files identified in the DROID profile
    batch_convert(droid_profile, target_dir)


if __name__ == '__main__':
    """
    Normalize Report script that searches for files in a given working directory and normalized them, writing the output to a specified target directory. This script 
    requires two positional arguments:
    
    - `working_dir`: The directory to search for files.
    - `target_dir`: The directory to move or copy files to.
    
    Usage:
    python normalize-report.py <working_dir> <target_dir>
    
    Example:
    python normalize-report.py /path/to/input /path/to/output
    Examine usage, note working-dir and target-dir are required args
    python normalize-report.py --working-dir my_project/input --target_dir my_project/output
    """
    # Define the command-line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--working_dir', help='The working directory to search for files', default='/app/input')
    parser.add_argument('--target_dir', help='The target directory to move or copy files to', default='/app/output')
    args = parser.parse_args()

    # Call the main function with the parsed arguments
    main(working_dir=args.working_dir, 
         target_dir=args.target_dir)