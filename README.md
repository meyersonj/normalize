# README

## Project Overview

This project is a Python-based file normalization tool that uses DROID, FFmpeg, LibreOffice, and Inkscape to convert files to different formats based on their MIME type. The tool is designed to be run in a Docker container, which ensures that all dependencies are correctly installed and configured.

The Python script takes two arguments: a working directory and a target directory. It scans the working directory for files, identifies their MIME type using DROID, and then converts them to a different format if necessary. The converted files are then moved to the target directory.

## Current status

- [x] test_identify_file
- [x] test_convert_to_mp4
- [x] test_convert_to_doc
- [x] test_convert_to_svg
- [x] test_convert_file 
- [ ] test w/ some real reference data


## Prerequisites

- Docker
- Make

## How to Use

1. Clone this repository to your local machine.

2. Use the provided Makefile to simplify the build and run process. The Makefile includes targets for building the Docker image, running a shell in the Docker container, running tests in the Docker container, and running the normalization process.

   - To build the Docker image:

     ```
     make build
     ```

   - To run a shell in the Docker container:

     ```
     make docker-shell
     ```

   - To run tests in the Docker container:

     ```
     make docker-test
     ```

   - To run the normalization process, replacing `<working_dir>` and `<target_dir>` with the paths to your working and target directories:

     ```
     make run-normalization WORKING_DIR=<working_dir> TARGET_DIR=<target_dir>
     ```

   This command mounts your working and target directories to the `/app/input` and `/app/output` directories in the Docker container, and then runs the Python script with these directories as arguments.

## Dependencies

- DROID: Used to identify the MIME type of files.
- FFmpeg: Used to convert audio and video files to MP3 and MP4 format, respectively.
- LibreOffice: Used to convert document files to DOC and PDF format.
- Inkscape: Used to convert vector image files to SVG format.

## Dockerfile

The Dockerfile included in this repository sets up a Docker container with Python 3.12 and all the necessary dependencies for the script. It also downloads the DROID binary and signature file, which are used to identify the MIME type of files.

## Makefile

The Makefile included in this repository provides a convenient way to perform common tasks such as building the Docker image, running a shell in the Docker container, running tests, and running the normalization process.

## Limitations

This tool currently supports the conversion of audio, video, document, and vector image files. Other file types will be copied to the target directory without being converted. If you need to convert a different type of file, you may need to modify the script and Dockerfile to include the necessary conversion tools.

## Contributing

Contributions are welcome! Please submit a pull request or create an issue if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Note on Local Installation

While it is technically possible to run this script directly on your local machine, we strongly recommend using Docker. Docker ensures that all dependencies are correctly installed and configured, and it isolates the project from your local environment, reducing the risk of conflicts or other issues. If you choose to run the script locally, you will need to manually install and configure all dependencies, and we cannot guarantee that the script will work as expected.
