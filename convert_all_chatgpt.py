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
    Identifies the MIME type and other metadata for a file using DROID.
    Targets a directory, creates a profile along the way
    """

    # create the profile
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

def convert_to_mp4(filepath, output_dir=None):
    """
    Converts a video file to MP4 format using FFmpeg.
    """
    #mp4_path = os.path.splitext(filepath)[0] + '.mp4'
    mp4_path = construct_output_path(filepath, '.mp4', output_dir)
    cmd = f'ffmpeg -i "{filepath}" "{mp4_path}"'
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f'Error converting {filepath} to MP4: {e}', file=sys.stderr)
        return
    return mp4_path

def convert_to_mp3(filepath, output_dir=None):
    """
    Converts an audio file to MP3 format using FFmpeg.
    """
    mp3_path = construct_output_path(filepath, '.mp3', output_dir)

    cmd = f'ffmpeg -i "{filepath}" -vn -ar 44100 -ac 2 -ab 192k -f mp3 "{mp3_path}"'
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f'Error converting {filepath} to MP3: {e}', file=sys.stderr)
        return
    return mp3_path

def convert_to_doc(filepath, output_dir=None):
    """
    Converts a document file to DOC format using LibreOffice.
    """
    doc_path = construct_output_path(filepath, '.doc', output_dir)
    cmd = [libreoffice_cmd, '--headless', '--convert-to', 'doc', filepath, '--outdir', os.path.dirname(doc_path)]
    try:
        subprocess.check_call(cmd, shell=False)
    except subprocess.CalledProcessError as e:
        print(f'Error converting {filepath} to DOC: {e}', file=sys.stderr)
        return
    return doc_path

def convert_to_pdf(filepath, output_dir=None):
    """
    Converts a document file to PDF format using LibreOffice.
    """
    pdf_path = construct_output_path(filepath, '.pdf', output_dir)
    cmd = [libreoffice_cmd, '--headless', '--convert-to', 'pdf', filepath, '--outdir', os.path.dirname(pdf_path)]
    try:
        subprocess.check_call(cmd, shell=False)
    except subprocess.CalledProcessError as e:
        print(f'Error converting {filepath} to PDF: {e}', file=sys.stderr)
        return
    return pdf_path

def convert_to_svg(filepath, output_dir=None):
    """
    Converts a vector image file to SVG format using Inkscape.
    """
    svg_path = construct_output_path(filepath, '.svg', output_dir)
    cmd = f'inkscape  --export-filename="{svg_path}" "{filepath}" 2>/dev/null'

    try:
        print(cmd)
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f'Error converting {filepath} to SVG: {e}', file=sys.stderr)
        return
    return svg_path

def no_convert(filepath, output_dir=None):
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

def convert_file(filepath,metadata):
    """
    Converts a file to a different format based on its MIME type.  
    Use batch convert if able
    """
    mime_type = metadata.get('MIME_TYPE', '').lower()

    if 'audio' in mime_type:
        sound = AudioSegment.from_file(filepath)
        mp3_path = os.path.splitext(filepath)[0] + '.mp3'
        sound.export(mp3_path, format='mp3')
        return mp3_path

    elif 'video' in mime_type:
        return convert_to_mp4(filepath)

    elif 'image/svg' in mime_type:
        return filepath
    
    elif 'postscript' in mime_type:
        return convert_to_svg(filepath)

    elif 'text/xml' in mime_type:
        return convert_to_doc(filepath)

    elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in mime_type:
        return convert_to_doc(filepath)
    
    elif mime_type == 'text/plain':
        return filepath # no convertion

    else:
        print(f'Unsupported file type: {mime_type}', file=sys.stderr)

def batch_convert(droid_profile, target_dir):
    mime_conversion_map = {
        'audio/mpeg': convert_to_mp3,
        'audio/x-wav': convert_to_mp3,
        'video/x-msvideo': convert_to_mp4,
        'application/postscript': convert_to_svg,
        'application/vnd.oasis.opendocument.text': convert_to_doc,
        'application/xml': convert_to_doc,
        'text/xml': convert_to_doc,
        'text/plain': no_convert,
        'image/svg+xml': no_convert,
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': no_convert,
        'video/mp4': no_convert,
        'application/xml, text/xml': convert_to_doc,
        'application/vnd.oasis.opendocument.text': convert_to_doc,
    }
    status_dict = {'success':[], 'fail':[], 'unconverted': {}, 'f_count':0}

    for item in droid_profile:
        # Check if it's a file
        #breakpoint()
        if item['TYPE'] == 'File':
            mime_type = item['MIME_TYPE']
            file_path = item['FILE_PATH']
            status_dict['f_count'] += 1

            conversion_function = mime_conversion_map.get(mime_type)
            if conversion_function:
                target_file_path = os.path.join(target_dir, os.path.basename(file_path))
                print(target_file_path)

                try:
                    # If the conversion function is not `no_convert`, we perform conversion
                    if conversion_function is not no_convert:
                        conversion_function(file_path, output_dir=target_dir)
                        status_dict['success'].append(file_path)
                    else:  # If it's `no_convert`, we simply copy the file
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
