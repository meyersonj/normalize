import os
import tempfile
import shutil
import subprocess

import pytest

from convert_all_chatgpt import convert_to_mp4, convert_to_mp3, convert_to_svg, convert_file, convert_to_doc, build_droid_profile, identify_file, batch_convert,construct_output_path, no_convert, replace_suffix, convert_to_pdf

@pytest.fixture(scope='class')
def setup_and_teardown(request):
    temp_dir = tempfile.mkdtemp()
    output_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, 'testfile.txt')
    with open(temp_file, 'w') as f:
        f.write('test data')

    video_file = os.path.join(temp_dir, 'test_video.avi')
    subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'testsrc=size=320x240:rate=30', '-t', '5', video_file], check=True)
    
    wav_file = os.path.join(temp_dir, 'test_audio.wav')
    subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=5', '-ar', '44100', '-ac', '2', wav_file], check=True)

    odt_file = os.path.join(temp_dir, 'test_doc.odt')
    with open(odt_file, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        # Your additional writes to the file...

    eps_file = os.path.join(temp_dir, 'testfile.eps')
    with open(eps_file, 'w') as f:
        f.write('%!PS-Adobe-3.0 EPSF-3.0\n')
        # Your additional writes to the file...

    print(temp_dir)
    profile = build_droid_profile(temp_dir)

    # Add your attributes to the class
    request.cls.temp_dir = temp_dir
    request.cls.output_dir = output_dir
    request.cls.temp_file = temp_file
    request.cls.video_file = video_file
    request.cls.wav_file = wav_file
    request.cls.odt_file = odt_file
    request.cls.eps_file = eps_file
    request.cls.profile = profile

    yield

    shutil.rmtree(temp_dir)

@pytest.mark.usefixtures("setup_and_teardown")
class TestFileConversion:
    def test_droid_profile(self):
        droid_profile =  self.profile
        expected_results = [
            {'FILE_PATH': self.temp_file, 'MIME_TYPE': 'text/plain', 'PUID': 'x-fmt/111'},
            {'FILE_PATH':self.eps_file, 'MIME_TYPE': 'application/postscript',  'PUID': 'fmt/124'},
            {'FILE_PATH': self.wav_file,  'MIME_TYPE': 'audio/x-wav','PUID':'fmt/141'},
            {'FILE_PATH': self.video_file, 'MIME_TYPE':'video/x-msvideo', 'PUID':'fmt/5'},
            {'FILE_PATH': self.odt_file, 'MIME_TYPE':'application/xml, text/xml','PUID':'fmt/101'},
        ]

        for expected_dict in expected_results:
            matching_dicts = [p for p in droid_profile if p['FILE_PATH'] == expected_dict['FILE_PATH']]
            assert len(matching_dicts) == 1, f"No or multiple dictionaries found in profile for FILE_PATH {expected_dict['FILE_PATH']}"
            
            matching_dict = matching_dicts[0]
            
            for key, value in expected_dict.items():
                if key == 'FILE_PATH':
                    continue  
                assert key in matching_dict, f"Key '{key}' not found in dictionary with FILE_PATH {matching_dict['FILE_PATH']}"
                assert matching_dict[key] == value, f"Value for key '{key}' does not match expected value for FILE_PATH {matching_dict['FILE_PATH']}"
        
    def test_no_convert_with_output_dir(self):
        output_file_path = no_convert(self.temp_file, output_dir = self.output_dir)
        assert os.path.isfile(output_file_path)
        with open(output_file_path, 'r') as f:
            assert f.read() == 'test data'

    def test_construct_output_path(self):
        # Test with output_dir provided
        filepath = '/path/to/input/file.txt'
        suffix = '.mp4'
        output_dir = '/path/to/output'
        expected_output_path = '/path/to/output/file.mp4'
        assert construct_output_path(filepath, suffix, output_dir) == expected_output_path

        # Test without output_dir provided
        filepath = '/path/to/input/file.txt'
        suffix = '.doc'
        expected_output_path = '/path/to/input/file.doc'
        assert construct_output_path(filepath, suffix) == expected_output_path

        # Test with empty string as suffix
        filepath = '/path/to/input/file.txt'
        suffix = ''
        expected_output_path = '/path/to/input/file'
        assert construct_output_path(filepath, suffix) == expected_output_path

        # Test with dot in basename of filepath
        filepath = '/path/to/input/file.v1.txt'
        suffix = '.doc'
        expected_output_path = '/path/to/input/file.v1.doc'
        assert construct_output_path(filepath, suffix) == expected_output_path

        # Test with relative paths
        filepath = 'input/file.txt'
        suffix = '.mp4'
        output_dir = 'output'
        expected_output_path = 'output/file.mp4'
        assert construct_output_path(filepath, suffix, output_dir) == expected_output_path

        # Test with dot in output_dir path
        filepath = '/path/to/input/file.txt'
        suffix = '.mp4'
        output_dir = '/path/to/output./files'
        expected_output_path = '/path/to/output./files/file.mp4'
        assert construct_output_path(filepath, suffix, output_dir) == expected_output_path

    def test_convert_to_mp4(self):
        mp4_path = convert_to_mp4(self.video_file)
        assert os.path.exists(self.video_file)
        assert os.path.splitext(mp4_path)[1] == '.mp4'
        metadata = identify_file(mp4_path)
        assert metadata['PUID'] == 'fmt/199'
        os.remove(mp4_path)

    def test_convert_to_mp3(self):
        mp3_path = convert_to_mp3(self.wav_file)
        assert os.path.exists(mp3_path)
        assert os.path.splitext(mp3_path)[1] == '.mp3'
        metadata = identify_file(mp3_path)
        assert metadata['PUID'] == 'fmt/134'  # 'fmt/134' is the PUID for MP3 
        os.remove(mp3_path)

    def test_convert_to_doc(self):
        doc_path = convert_to_doc(self.odt_file)
        assert os.path.exists(doc_path)
        assert os.path.splitext(doc_path)[1] == '.doc'
        os.remove(doc_path)

    def test_convert_to_pdf(self):
        # Input an existing file path in place of "input_file.odt"
        input_file = "input_file.odt" 
        pdf_path = convert_to_pdf(self.odt_file)
        
        # Check if the output file exists
        assert os.path.exists(pdf_path), "PDF file was not created."
        
        # Check if the output file has a .pdf extension
        assert os.path.splitext(pdf_path)[1] == '.pdf', "Output file is not a PDF."
        
        # Remove the output file
        os.remove(pdf_path)

    def test_convert_to_svg(self):
        svg_path = convert_to_svg(self.eps_file)
        assert os.path.exists(svg_path)
        assert os.path.splitext(svg_path)[1] == '.svg'
        os.remove(svg_path)

    def test_convert_file(self):

        audio_file = self.wav_file
        audio_metadata = [x for x in self.profile if x['FILE_PATH']==audio_file][0]
        mp3_path = convert_file(audio_file,audio_metadata)
        assert os.path.exists(mp3_path)
        assert os.path.splitext(mp3_path)[1] == '.mp3'
        os.remove(mp3_path)

        video_file = self.video_file 
        video_metadata = [x for x in self.profile if x['FILE_PATH']==video_file][0]
        mp4_path = convert_file(video_file, video_metadata)
        assert os.path.exists(mp4_path)
        assert os.path.splitext(mp4_path)[1] == '.mp4'
        os.remove(mp4_path)

        eps_metadata = [x for x in self.profile if x['FILE_PATH']==self.eps_file][0]
        svg_path = convert_file(self.eps_file, eps_metadata)
        assert os.path.exists(svg_path)
        assert os.path.splitext(svg_path)[1] == '.svg'
        os.remove(svg_path)
        #assert eps_file == svg_path

        doc_metadata = [x for x in self.profile if x['FILE_PATH']==self.odt_file][0]
        doc_path = convert_file(self.odt_file, doc_metadata)
        assert os.path.exists(doc_path)
        assert os.path.splitext(doc_path)[1] == '.doc'
        os.remove(doc_path)

        # plain text
        unknown_file = self.temp_file
        metadata = [x for x in self.profile if x['FILE_PATH']==self.temp_file][0]
        plain_text = convert_file(unknown_file, metadata)
        assert os.path.exists(plain_text)
    
    def test_batch_convert(self, tmp_path):
        target_dir = tmp_path / "target"
        target_dir.mkdir()
        batch_convert(self.profile, str(target_dir))

        expected_files = [
            os.path.join(target_dir, replace_suffix(self.temp_file, '.txt')),
            os.path.join(target_dir, replace_suffix(self.eps_file, '.svg')),
            os.path.join(target_dir, replace_suffix(self.wav_file, '.mp3')),
            os.path.join(target_dir, replace_suffix(self.video_file, '.mp4')),
            os.path.join(target_dir, replace_suffix(self.odt_file, '.doc')),
        ]
        for file in expected_files:
            assert os.path.exists(file), f"File {file} not found in target directory"


