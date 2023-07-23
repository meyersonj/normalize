# README

## Project Overview

This project is a Python-based file normalization tool that uses DROID, FFmpeg, LibreOffice, and Inkscape to create "normalized derivatives" of files in different formats based on their MIME type. The tool is designed to be run in a Docker container, which ensures that all dependencies are correctly installed and configured.

The Python script takes two arguments: a working directory and a target directory. It scans the working directory for files, identifies their MIME type using DROID, and then creates a normalized derivative in a different format if necessary. The original files are left untouched, and the normalized derivatives are moved to the target directory.

## Current test coverage

- [x] test_identify_file
- [x] test_norm_to_mp4
- [x] test_norm_to_doc
- [x] test_norm_to_svg
- [x] test_norm_file 
- [ ] test w/ some real reference data

## Prerequisites

- Docker
- Make

## Usage

1. Clone this repository to your local machine.

2. Build the Docker image:

   ```bash
   make build
   ```

3. To normalize the files in a directory, use the `run-normalization-debug` target in the Makefile. You need to provide the paths to your working directory and target directory as environment variables `WORKING_DIR` and `TARGET_DIR`:

   ```bash
   make run-normalization-debug WORKING_DIR=/path/to/your/working/dir TARGET_DIR=/path/to/your/target/dir
   ```

   This command will run the Docker container, mount your working directory to `/app/input` and your target directory to `/app/output`, and then run the normalization script. The script will process the files in the working directory and write the output to the target directory.

The `run-normalization-debug` target in the Makefile is named as such because it's designed to be used during the development and debugging process. It mounts your local directories to the Docker container, which allows you to see the changes in real-time and makes it easier to debug any issues.

In a production environment, you would likely use a different setup. For example, you might have a separate Docker volume for the input and output directories, or you might use a cloud storage service to store your files. The Docker container could be run on a server or a cloud-based compute instance, and you might use a job scheduler or a queueing system to manage the normalization tasks.

## Dependencies

The Docker container is configured to handle all dependencies required for the file conversion process. Here is a brief overview of the dependencies and their roles:

- DROID: Used to identify the MIME type of files.
- FFmpeg: Used to normalize audio and video files to MP3 and MP4 format, respectively.
- LibreOffice: Used to normalize document files to DOC and PDF format.
- Inkscape: Used to normalize vector image files to SVG format.

These dependencies are **automatically installed** and configured when you build the Docker image, which is why we recommend using Docker to run the script. This ensures a consistent environment and reduces the risk of conflicts or other issues.

## Troubleshooting and Advanced Usage

If you encounter issues while running the normalization process, you can use the `docker-shell` and `docker-test` targets in the Makefile to debug:

- `make docker-shell`: This command runs a shell in the Docker container, allowing you to interactively run commands and inspect the state of the container.

- `make docker-test`: This command runs the tests in the Docker container. If the tests fail, the output should provide clues about what went wrong.

## Limitations and Next Steps

This tool currently creates normalized derivatives of audio, video, document, and vector image files. Other file types will be copied to the target directory without being converted. If you need to create normalized derivatives of a different/additional file types, you will need to modify the script and Dockerfile to include the necessary normalization pathways. This may require installing additional software.

It's important to note that the tool does not modify the original files. Instead, it creates "normalized derivatives" - new files that have been converted to a different format. This ensures that the original files are preserved, reducing the risk of data loss.

While the current implementation is functional, there are several areas where it could be improved:

- **Name Collisions**: One potential limitation to be aware of is the possibility of name collisions. For example, if you have two files named `file.eps` and `file.svg`, they would both be normalized to file.svg, potentially overwriting one another. This issue can be resolved by customizing the normalization pathways and implementing specific naming conventions that suit your needs. For instance, you could append a timestamp or a unique identifier to the filename, or you could include the original file extension in the new filename (e.g., `file_eps.svg`). Alternatively, you could organize the output files into subdirectories based on their original format or MIME type. The exact solution will depend on your specific use case and requirements.
- **Scaling**: The current implementation processes files in a single-threaded manner. If you need to process a large number of files or very large files, this could become a bottleneck. Consider parallelizing the file processing to take advantage of multiple cores or distributed systems.
- **Deployment**: The current setup requires manual deployment. In a production environment, you might want to automate this process using a CI/CD pipeline. This would also make it easier to roll out updates to the script.
- **Configuration**: The script currently requires the user to manually specify the working and target directories as command-line arguments. It might be more user-friendly to allow these settings to be configured via a configuration file or environment variables.
- **Testing**: The script includes comprehensive unit tests, but it would be beneficial to add more types of tests, including integration tests and end-to-end tests. This would help to catch any bugs or regressions in the code.
- **Logging**: Currently, the tool does not capture or log the output from the various software used in the normalization process. This means that valuable information about the normalization process, such as error messages or other diagnostic information, is not being recorded. Improving the logging capabilities of the tool could make it easier to troubleshoot issues and understand the normalization process.

### Customizing Normalization Pathways

The current normalization pathways are defined in the `batch_norm` function within the `normalize_all.py` script. These pathways are represented as a static dictionary that maps MIME types to corresponding normalization functions.
```python
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
```

For reference here a table with _likely_ file extensions associated with the MIME types we currently look for.  Please note that this is a simplified representation and the actual mapping in the code is based on MIME types, **not** file extensions. For instance, the `.xml` extension is mapped to both `convert_to_doc` and `no_convert` functions because XML files can have different structures and uses, and the appropriate function would depend on the specific use case.

| Droid detected MIME Type | Likely File Extensions |
| --- | --- |
| `audio/mpeg` | .mp3 |
| `audio/x-wav` | .wav |
| `video/x-msvideo` | .avi |
| `application/postscript` | .ps |
| `application/vnd.oasis.opendocument.text` | .odt |
| `application/xml` | .xml |
| `text/xml` | .xml |
| `text/plain` | .txt |
| `image/svg+xml` | .svg |
| `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | .docx |
| `video/mp4` | .mp4 |
| `application/xml, text/xml` | .xml |




This design is intended to provide a **starting point** for file normalization, but it's important to note that these pathways may not suit every use case.  Depending on your specific requirements, you might need to define additional or altering existing normalization pathways to fit your needs. For example, while the current pathways normalizes `.odt` files to `.doc` format, you might prefer to have your normalization pathway to generate `.pdf` derivatives instead.

As an open-source tool, you're encouraged to modify these normalization pathways to better suit your needs. You can do this by editing the dictionary in the `batch_norm` function. Each key-value pair in the dictionary represents a normalization pathway, with the key being the MIME type of the input files, and the value being the function that converts files of this type to the desired format.

These improvements would require significant changes to the script, but they could make the tool more flexible and useful for a wider range of use cases. As always, contributions are welcome!

### On Building DROID Profiles

The `build_droid_profile` function is used to identify the MIME type and other metadata for all files in a specified directory. This function uses DROID, a software tool developed by [The National Archives of the United Kingdom](https://www.nationalarchives.gov.uk/) to perform format identification.

The function works by creating a DROID profile for the directory, which is a process that involves scanning all files in the directory and identifying their MIME type and other metadata. This metadata is then extracted into a CSV file.

The CSV file is read into a list of dictionaries, where each dictionary contains the metadata for a file in the directory. This list is returned by the function and can be used to determine how each file should be converted.

Here's an example of how to use the function:

```python
profile = build_droid_profile('/path/to/your/directory')
```

This will return a list of dictionaries, where each dictionary contains the metadata for a file in the directory. You can then iterate over this list to process each file based on its metadata.

Please note that this function is designed to be run in a Docker container, where DROID and all other dependencies are correctly installed and configured. If you choose to run the function outside of a Docker container, you will need to manually install and configure DROID.

## Contributing

Contributions are welcome! Please submit a pull request or create an issue if you have any improvements or bug fixes.

## Usage and License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) License. This means you are free to share (copy and redistribute the material in any medium or format) and adapt (remix, transform, and build upon the material) under the following terms:

- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- **NonCommercial** — You may not use the material for commercial purposes.
- **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

Please credit the following contributors in any derivative works:

- Jessica Meyerson, [Educopia Institute](https://educopia.org/)
- [Dmitry Meyerson](http://meyerson.github.io//)
- Craig Steelman

For more details, please see the [LICENSE](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).

Please note that this license does not cover any third-party dependencies used in this project. These dependencies may be covered by other licenses. Please refer to the respective dependency documentation for more information.

## Note on Local Installation

While it is technically possible to run this script directly on your local machine, we strongly recommend using Docker. Docker ensures that all dependencies are correctly installed and configured, and it isolates the project from your local environment, reducing the risk of conflicts or other issues. If you choose to run the script locally, you will need to manually install and configure all dependencies, and we cannot guarantee that the script will work as expected.