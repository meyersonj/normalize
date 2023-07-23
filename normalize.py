import os
import subprocess
import json
from typing import Dict
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import sys
import mimetypes
import shlex
import csv
import argparse
from shutil import copyfile, copy
import pprint


droid_cmd = 'java -jar droid-command-line-6.6.1.jar'
droid_sign_file = "DROID_SignatureFile_V111.xml"
libreoffice_cmd = 'soffice'


def build_droid_profile(dirpath):
    """
    This function uses DROID to identify the MIME type and other metadata for all files in a specified directory. 
    It creates a DROID profile for the directory, extracts the metadata into a CSV file, and then reads this CSV file into a list of dictionaries.

    Parameters:
    dirpath (str): The path to the directory to be profiled.

    Returns:
    list: A list of dictionaries, where each dictionary contains the metadata for a file in the directory.
    """
    md5_sum = 'temp'
    create_profile_cmd = f"{droid_cmd} -R {dirpath} -Ns {droid_sign_file} -p {md5_sum}.droid"
    args = shlex.split(create_profile_cmd)
    subprocess.call(args)

    # extract the metadata
    extract_metadata_cmd = f"{droid_cmd} -p {md5_sum}.droid -e {md5_sum}.droid_output"
    args = shlex.split(extract_metadata_cmd)
    subprocess.call(args)

    #dump to stdout
    file_to_stdout = f"cat {md5_sum}.droid_output"
    args = shlex.split(file_to_stdout)
    output = subprocess.check_output(args, universal_newlines=True)

    # cleanup
    cleanup_cmd = f"rm {md5_sum}.droid_output {md5_sum}.droid"
    args = shlex.split(cleanup_cmd)
    subprocess.call(args)

    #profile_dict = io.StringIO(output)
    csv_reader = csv.DictReader(output.splitlines())

    return list(csv_reader)


def identify_file(filepath):
    """
    Identifies the PUID for a file using DROID in no-profile mode
    """

    output = subprocess.check_output(" ".join([droid_cmd, '-Nr', filepath, '-Ns', droid_sign_file]), universal_newlines=True ,shell=True)

    lines = output.strip().split('\n')
    keys = lines[0].split(',')
    values = lines[1].split(',')

    metadata = {}
    for i, key in enumerate(keys):
        metadata[key] = values[i]

    return metadata

def construct_output_path(filepath, suffix, output_dir=None):
    """
    Constructs the path for the output file.

    Parameters:
    filepath (str): The input file path.
    suffix (str): The suffix for the output file (including the dot, like '.mp4', '.doc', etc.)
    output_dir (str, optional): The directory to place the output file. If not provided, 
                                the directory of the input file is used. 

    Returns:
    str: The constructed output file path.
    """
    basename = os.path.splitext(os.path.basename(filepath))[0] + suffix
    if output_dir:
        output_path = os.path.join(output_dir, basename)
    else:
        output_path = os.path.join(os.path.dirname(filepath), basename)
    
    return output_path

def replace_suffix(filename, new_suffix):
    base_name = os.path.splitext(os.path.basename(filename))[0]
    return base_name + new_suffix

def norm_to_mp4(filepath, output_dir=None):
    """
    Create a normalized video file to MP4 format using FFmpeg.
    """
    mp4_path = construct_output_path(filepath, '.mp4', output_dir)
    cmd = f'ffmpeg -i "{filepath}" "{mp4_path}"'
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f'Error creating a normalized derivative of {filepath} to MP4: {e}', file=sys.stderr)
        return
    return mp4_path

def norm_to_mp3(filepath, output_dir=None):
    """
    Create a normalized derivative from audio file to MP3 format using FFmpeg.
    """
    mp3_path = construct_output_path(filepath, '.mp3', output_dir)

    cmd = f'ffmpeg -i "{filepath}" -vn -ar 44100 -ac 2 -ab 192k -f mp3 "{mp3_path}"'
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f'Error creating a normalized derivative of {filepath} to MP3: {e}', file=sys.stderr)
        return
    return mp3_path

def norm_to_doc(filepath, output_dir=None):
    """
    Create a normalized derivative from a document file to DOC format using LibreOffice.
    """
    doc_path = construct_output_path(filepath, '.doc', output_dir)
    cmd = [libreoffice_cmd, '--headless', '--convert-to', 'doc', filepath, '--outdir', os.path.dirname(doc_path)]
    try:
        subprocess.check_call(cmd, shell=False)
    except subprocess.CalledProcessError as e:
        print(f'Error creating a normalized derivative of {filepath} to DOC: {e}', file=sys.stderr)
        return
    return doc_path

def norm_to_pdf(filepath, output_dir=None):
    """
    Create a normalized derivative from a document file to PDF format using LibreOffice.
    """
    pdf_path = construct_output_path(filepath, '.pdf', output_dir)
    cmd = [libreoffice_cmd, '--headless', '--convert-to', 'pdf', filepath, '--outdir', os.path.dirname(pdf_path)]
    try:
        subprocess.check_call(cmd, shell=False)
    except subprocess.CalledProcessError as e:
        print(f'Error creating a normalized derivative of {filepath} to PDF: {e}', file=sys.stderr)
        return
    return pdf_path

def norm_to_svg(filepath, output_dir=None):
    """
    Create a normalized derivative from a vector image file to SVG format using Inkscape.
    """
    svg_path = construct_output_path(filepath, '.svg', output_dir)
    cmd = f'inkscape  --export-filename="{svg_path}" "{filepath}" 2>/dev/null'

    try:
        print(cmd)
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f'Error creating a normalized derivative of {filepath} to SVG: {e}', file=sys.stderr)
        return
    return svg_path

def no_norm(filepath, output_dir=None):
    """
    Returns the same filepath if no output_dir is provided.
    If output_dir is provided, the file is copied to output_dir and the new filepath is returned.
    """
    if output_dir:
        # Use the construct_output_path function to generate the destination filepath
        destination_filepath = construct_output_path(filepath, '', output_dir)
        
        # Copy the file
        copy(filepath, destination_filepath)
        
        return destination_filepath
    else:
        return filepath

def norm_file(filepath,metadata):
    """
    Create a normalized derivative from a file to a different format based on its MIME type.  
    Use batch convert if able
    """
    mime_type = metadata.get('MIME_TYPE', '').lower()

    if 'audio' in mime_type:
        sound = AudioSegment.from_file(filepath)
        mp3_path = os.path.splitext(filepath)[0] + '.mp3'
        sound.export(mp3_path, format='mp3')
        return mp3_path

    elif 'video' in mime_type:
        return norm_to_mp4(filepath)

    elif 'image/svg' in mime_type:
        return filepath
    
    elif 'postscript' in mime_type:
        return norm_to_svg(filepath)

    elif 'text/xml' in mime_type:
        return norm_to_doc(filepath)

    elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in mime_type:
        return norm_to_doc(filepath)
    
    elif mime_type == 'text/plain':
        return filepath # no norm

    else:
        print(f'Unsupported file type: {mime_type}', file=sys.stderr)



def batch_norm(droid_profile, target_dir, working_dir='/app/input/'):
    mime_normalization_map = {
        'audio/mpeg': norm_to_mp3,
        'audio/x-wav': norm_to_mp3,
        'video/x-msvideo': norm_to_mp4,
        'application/postscript': norm_to_svg,
        'application/vnd.oasis.opendocument.text': norm_to_doc,
        'application/xml': norm_to_doc,
        'text/xml': norm_to_doc,
        'text/plain': no_norm,
        'image/svg+xml': no_norm,
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': norm_to_doc,
        'video/mp4': no_norm,
        'application/xml, text/xml': norm_to_doc
    }
    status_dict = {'success':[], 'fail':[], 'unconverted': {}, 'f_count':0}
    
    # Create all directories in the target directory, including empty ones
    for dirpath, dirnames, filenames in os.walk(working_dir):
        relative_dirpath = os.path.relpath(dirpath, working_dir)
        print(relative_dirpath)
        target_dirpath = os.path.join(target_dir, relative_dirpath)
    
        os.makedirs(target_dirpath, exist_ok=True)

    for item in droid_profile:
        # Check if it's a file
        if item['TYPE'] == 'File':
            mime_type = item['MIME_TYPE']
            file_path = item['FILE_PATH']
            status_dict['f_count'] += 1

            conversion_function = mime_normalization_map.get(mime_type, no_norm)
            if conversion_function:
                # Get the relative path of the file from the working directory
                relative_path = os.path.relpath(file_path, working_dir)
                # Create the target file path by joining the target directory with the relative path
                target_file_path = os.path.join(target_dir, relative_path)

                try:
                    # If the conversion function is not `no_norm`, we perform conversion
                    if conversion_function is not no_norm:
                        target_dir_path = os.path.dirname(target_file_path)
                        conversion_function(file_path, output_dir=target_dir_path)
                        status_dict['success'].append(file_path)
                    else:  # If it's `no_norm`, we simply copy the file
                        copyfile(file_path, target_file_path)
                        status_dict['success'].append(file_path)
                except Exception as e:
                    print(f'Error converting {file_path}: {e}', file=sys.stderr)
                    status_dict['fail'].append(file_path)
            else:
                if mime_type in status_dict['unconverted']:
                    status_dict['unconverted'][mime_type] += 1
                else:
                    status_dict['unconverted'].update({mime_type:1})

    print(f"USER REPORT ON SCRIPT RESULTS: {len(status_dict['success'])} files normalized out of {status_dict['f_count']} total files in the directory, and {len(status_dict['fail'])} failed normalizations. For the failed normalizations, please review the error messages printed to screen from the software used for normalizing those files. For files that were not failed normalizations, but remain unnormalized, make sure there is a normalization pathway for that file type currently defined in this script.\n\nPlease see the list of unique file types represented among the unnormalized files below, determine your preferred normalized output for those file type, identify & install software to complete the normalization tasks on those file types, and add those normalization paths to this script. Save and rerun to see if the script was able to successfully normalize additional files.\n\nIf you aren't sure which free, open source software will open and normalize the remaining extensions, try asking ChatGPT, or review the normalization paths defined in the Archivematica documentation.")

    pprint.pprint(status_dict['unconverted'])
