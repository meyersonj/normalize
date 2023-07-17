import os
import tempfile
import shutil
import subprocess

import pytest

from convert_all_chatgpt import convert_to_mp4, convert_to_svg, convert_file, convert_to_doc, build_droid_profile, identify_file

@pytest.fixture(scope='class')
def setup_and_teardown(request):
    temp_dir = tempfile.mkdtemp()
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

    def test_convert_to_mp4(self):
        mp4_path = convert_to_mp4(self.video_file)
        assert os.path.exists(self.video_file)
        assert os.path.splitext(mp4_path)[1] == '.mp4'
        metadata = identify_file(mp4_path)
        assert metadata['PUID'] == 'fmt/199'
        os.remove(mp4_path)

    def test_convert_to_doc(self):
        doc_path = convert_to_doc(self.odt_file)
        assert os.path.exists(doc_path)
        assert os.path.splitext(doc_path)[1] == '.doc'
        os.remove(doc_path)

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


