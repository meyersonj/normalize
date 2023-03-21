import os
import subprocess
import json
from typing import Dict
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import sys
import mimetypes

droid_cmd = 'java -jar droid-command-line-6.5.2.jar'
droid_sign_file = "DROID_SignatureFile_V111.xml"
libreoffice_cmd = '/Applications/LibreOffice.app/Contents/MacOS/soffice'

#java -jar droid-command-line-6.5.2.jar -Nr  -Ns 

def identify_file(filepath):
    """
    Identifies the MIME type and other metadata for a file using DROID.
    """
    output = subprocess.check_output(" ".join([droid_cmd, '-Nr', filepath, '-Ns', droid_sign_file]), universal_newlines=True ,shell=True)
    metadata = {}
    for line in output.split('\n'):
        print(line)
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
    
    print(metadata)
    mime_type = output.split('\n')[-2].replace(metadata['Selected folder or file'],'').replace(',','')
    if mime_type=='Unknown':
        # Guess the MIME type of a file based on its filename
        mime_type, encoding = mimetypes.guess_type(filepath)
    metadata['MIME Type'] = mime_type
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
    cmd = f'inkscape --export-filename="{svg_path}" "{filepath}"'
    try:
        print(cmd)
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f'Error converting {filepath} to SVG: {e}', file=sys.stderr)
        return
    return svg_path

def convert_file(filepath):
    """
    Converts a file to a different format based on its MIME type.
    """
    metadata = identify_file(filepath)
    mime_type = metadata.get('MIME Type', '').lower()

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
