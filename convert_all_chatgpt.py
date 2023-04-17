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

    #file_path, puid = output.strip().split(',')
    lines = output.strip().split('\n')
    keys = lines[0].split(',')
    values = lines[1].split(',')

    metadata = {}
    for i, key in enumerate(keys):
        metadata[key] = values[i]

    return metadata


def convert_to_mp4(filepath):
    """
    Converts a video file to MP4 format using FFmpeg.
    """
    mp4_path = os.path.splitext(filepath)[0] + '.mp4'
    cmd = f'ffmpeg -i "{filepath}" "{mp4_path}"'
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f'Error converting {filepath} to MP4: {e}', file=sys.stderr)
        return
    return mp4_path

def convert_to_mp3(filepath):
    """
    Converts an audio file to MP3 format using FFmpeg.
    """
    mp3_path = os.path.splitext(filepath)[0] + '.mp3'
    cmd = f'ffmpeg -i "{filepath}" -vn -ar 44100 -ac 2 -ab 192k -f mp3 "{mp3_path}"'
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f'Error converting {filepath} to MP3: {e}', file=sys.stderr)
        return
    return mp3_path

def convert_to_doc(filepath):
    """
    Converts a document file to DOC format using LibreOffice.
    """
    doc_path = os.path.splitext(filepath)[0] + '.doc'
    cmd = [libreoffice_cmd, '--headless', '--convert-to', 'doc', filepath, '--outdir', os.path.dirname(filepath)]
    try:
        subprocess.check_call(cmd, shell=False)
    except subprocess.CalledProcessError as e:
        print(f'Error converting {filepath} to DOC: {e}', file=sys.stderr)
        return
    return doc_path


def convert_to_svg(filepath):
    """
    Converts a vector image file to SVG format using Inkscape.
    """
    svg_path = os.path.splitext(filepath)[0] + '.svg'
    cmd = f'inkscape  --export-filename="{svg_path}" "{filepath}" 2>/dev/null'

    try:
        print(cmd)
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f'Error converting {filepath} to SVG: {e}', file=sys.stderr)
        return
    return svg_path


def convert_file(filepath,metadata):
    """
    Converts a file to a different format based on its MIME type.
    """
    mime_type = metadata.get('MIME_Type', '').lower()

    if 'audio' in mime_type:
        sound = AudioSegment.from_file(filepath)
        mp3_path = os.path.splitext(filepath)[0] + '.mp3'
        sound.export(mp3_path, format='mp3')
        return mp3_path

    elif 'video' in mime_type:
        return convert_to_mp4(filepath)

    elif 'image/svg' in mime_type:
        return filepath

    elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in mime_type:
        return convert_to_doc(filepath)

    else:
        print(f'Unsupported file type: {mime_type}', file=sys.stderr)


def normalization_map():

    

    {
    ".aac": "audio/aac",
    ".ac3": "audio/ac3",
    ".avi": "video/x-msvideo",
    ".csv": "text/csv",
    ".epub": "application/epub+zip",
    ".flac": "audio/flac",
    ".gif": "image/gif",
    ".html": "text/html",
    ".ico": "image/x-icon",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".m4a": "audio/mp4",
    ".mp3": "audio/mpeg",
    ".mp4": "video/mp4",
    ".odt": "application/vnd.oasis.opendocument.text",
    ".oga": "audio/ogg",
    ".ogv": "video/ogg",
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".rtf": "application/rtf",
    ".svg": "image/svg+xml",
    ".txt": "text/plain",
    ".webm": "video/webm",
    ".wav": "audio/wav",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xml": "application/xml"
}

