#import unittest
import pytest
import os
import tempfile
import shutil
import subprocess

from convert_all_chatgpt import convert_to_mp4, convert_to_svg, convert_file, convert_to_doc, build_droid_profile, identify_file

class TestFileConversion(unittest.TestCase):

    def setUp(self):
        # Create temporary directory and file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, 'testfile.txt')
        with open(self.temp_file, 'w') as f:
            f.write('test data')

        # Create a small video file for testing
        self.video_file = os.path.join(self.temp_dir, 'test_video.avi')
        subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'testsrc=size=320x240:rate=30', '-t', '5', self.video_file], check=True)
        
        self.wav_file = os.path.join(self.temp_dir, 'test_audio.wav')
        subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=5', '-ar', '44100', '-ac', '2', self.wav_file], check=True)

        # Create a temporary .odt file for testing
        self.odt_file = os.path.join(self.temp_dir, 'test_doc.odt')
        with open(self.odt_file, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" office:version="1.2">\n')
            f.write('<office:body>\n')
            f.write('<office:text>\n')
            f.write('This is a test document for the convert_to_doc unit test.\n')
            f.write('It contains some sample text for testing purposes.\n')
            f.write('</office:text>\n')
            f.write('</office:body>\n')
            f.write('</office:document-content>\n')

        # Create a temporary EPS file for testing
        self.eps_file = os.path.join(self.temp_dir, 'testfile.eps')
        with open(self.eps_file, 'w') as f:
            f.write('%!PS-Adobe-3.0 EPSF-3.0\n')
            f.write('%%BoundingBox: 0 0 100 100\n')
            f.write('/Times-Roman findfont\n')
            f.write('12 scalefont\n')
            f.write('setfont\n')
            f.write('50 50 moveto\n')
            f.write('(test) show\n')
            f.write('showpage\n')

        print(self.temp_dir)

    def tearDown(self):
        # Remove temporary directory and file
        shutil.rmtree(self.temp_dir)

    def test_droid_profile(self):
        # Test identifying MIME type of a text file

        droid_profile = build_droid_profile(self.temp_dir)

        #note we only test a subset of kv pairs
        expected_results = [
            {'FILE_PATH': self.temp_file, 'MIME_TYPE': 'text/plain', 'PUID': 'x-fmt/111'},
            {'FILE_PATH':self.eps_file, 'MIME_TYPE': 'application/postscript',  'PUID': 'fmt/124'},
            {'FILE_PATH': self.wav_file,  'MIME_TYPE': 'audio/x-wav','PUID':'fmt/141'},
            {'FILE_PATH': self.video_file, 'MIME_TYPE':'video/x-msvideo', 'PUID':'fmt/5'},
            {'FILE_PATH': self.odt_file, 'MIME_TYPE':'application/xml, text/xml','PUID':'fmt/101'},
        ]
        self.droid_profile = droid_profile
        # Iterate through each dictionary in `expected_results` and compare it with the corresponding dictionary in `profile`
        for expected_dict in expected_results:
            # Check if there exists a dictionary in `profile` that has the same `FILE_PATH` value as the current expected dictionary
            matching_dicts = [p for p in droid_profile if p['FILE_PATH'] == expected_dict['FILE_PATH']]
            self.assertEqual(len(matching_dicts),1,msg=f"No or multiple dictionaries found in profile for FILE_PATH {expected_dict['FILE_PATH']}")

            matching_dict = matching_dicts[0]
            
            # Compare the matching dictionary's keys and values with those of the expected dictionary
            for key, value in expected_dict.items():
                if key == 'FILE_PATH':
                    continue  # We've already checked this key, so skip it
                print(key)
                self.assertIn(key, matching_dict, msg=f"Key '{key}' not found in dictionary with FILE_PATH {matching_dict['FILE_PATH']}")
                print(matching_dict[key], value)
                self.assertEqual(matching_dict[key], value, msg=f"Value for key '{key}' does not match expected value for FILE_PATH {matching_dict['FILE_PATH']}")

    def test_convert_to_mp4(self):
        # Test converting a video file to MP4
        mp4_path = convert_to_mp4(self.video_file)
        self.assertTrue(os.path.exists(self.video_file))
        self.assertEqual(os.path.splitext(mp4_path)[1], '.mp4')
        metadata = identify_file(mp4_path)
        self.assertEqual(metadata['PUID'], 'fmt/199')
        os.remove(mp4_path)

    def test_convert_to_doc(self):
        # Test converting a document file to DOC
        doc_path = convert_to_doc(self.odt_file)
        self.assertTrue(os.path.exists(doc_path))
        self.assertEqual(os.path.splitext(doc_path)[1], '.doc')
        os.remove(doc_path)

    def test_convert_to_svg(self):
        # Test converting a vector image file to SVG
        svg_path = convert_to_svg(self.eps_file)
        self.assertTrue(os.path.exists(svg_path))
        self.assertEqual(os.path.splitext(svg_path)[1], '.svg')
        os.remove(svg_path)

    def test_convert_file(self):
        # Test converting a file to a different format based on its MIME typed

        droid_profile = build_droid_profile(self.temp_dir)

        normalization_mapping = {
            'image/jpeg': 'normalize_jpeg.py',
            'audio/wav': 'normalize_wav.py',
            'video/mp4': 'normalize_mp4.py'
        }

        #for elem in droid_profile:
            # 

        audio_file = self.wav_file
        mp3_path = convert_file(audio_file)
        self.assertTrue(os.path.exists(mp3_path))
        self.assertEqual(os.path.splitext(mp3_path)[1], '.mp3')
        os.remove(mp3_path)

        video_file = self.video_file 
        mp4_path = convert_file(video_file)
        self.assertTrue(os.path.exists(mp4_path))
        self.assertEqual(os.path.splitext(mp4_path)[1], '.mp4')
        os.remove(mp4_path)

        svg_file = 'test_image.svg'
        svg_path = convert_file(svg_file)
        self.assertEqual(svg_file, svg_path)

        doc_file = self.odt_file
        doc_path = convert_file(doc_file)
        self.assertTrue(os.path.exists(doc_path))
        self.assertEqual(os.path.splitext(doc_path)[1], '.doc')
        os.remove(doc_path)

        unknown_file = self.temp_file
        with self.assertRaises(Exception):
            convert_file(unknown_file)
