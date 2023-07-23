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

### Customizing Normalization Pathways

The current normalization pathways are defined in the `batch_norm` function within the `normalize_all_.py` script. These pathways are represented as a static dictionary that maps MIME types to corresponding normalization functions.

This design is intended to provide a **starting point** for file normalization, but it's important to note that these pathways may not suit every use case.  Depending on your specific requirements, you might need to define additional or altering existing normalization pathways to fit your needs. For example, while the current pathways normalizes `.odt` files to `.doc` format, you might prefer to have your normalization pathway to generate `.pdf` derivatives instead.

As an open-source tool, you're encouraged to modify these normalization pathways to better suit your needs. You can do this by editing the dictionary in the `batch_norm` function. Each key-value pair in the dictionary represents a normalization pathway, with the key being the MIME type of the input files, and the value being the function that converts files of this type to the desired format.

Remember, the goal of this tool is to provide a flexible and customizable solution for file normalization. Don't hesitate to adjust the code to fit your specific use case.

Sure, here is the updated "Limitations and Next Steps" section with the new "Logging" bullet point:

## Limitations and Next Steps

This tool currently creates normalized derivatives of audio, video, document, and vector image files. Other file types will be copied to the target directory without being converted. If you need to create normalized derivatives of a different/additional file types, you will need to modify the script and Dockerfile to include the necessary normalization pathways. This may require installing additional software.

It's important to note that the tool does not modify the original files. Instead, it creates "normalized derivatives" - new files that have been converted to a different format. This ensures that the original files are preserved, reducing the risk of data loss.

While the current implementation is functional, there are several areas where it could be improved:

- **Scaling**: The current implementation processes files in a single-threaded manner. If you need to process a large number of files or very large files, this could become a bottleneck. Consider parallelizing the file processing to take advantage of multiple cores or distributed systems.
- **Deployment**: The current setup requires manual deployment. In a production environment, you might want to automate this process using a CI/CD pipeline. This would also make it easier to roll out updates to the script.
- **Configuration**: The script currently requires the user to manually specify the working and target directories as command-line arguments. It might be more user-friendly to allow these settings to be configured via a configuration file or environment variables.
- **Testing**: The script includes comprehensive unit tests, but it would be beneficial to add more types of tests, including integration tests and end-to-end tests. This would help to catch any bugs or regressions in the code.
- **Logging**: Currently, the tool does not capture or log the output from the various software used in the normalization process. This means that valuable information about the normalization process, such as error messages or other diagnostic information, is not being recorded. Improving the logging capabilities of the tool could make it easier to troubleshoot issues and understand the normalization process.

### Customizing Normalization Pathways

The current implementation of the tool uses a static dictionary to define normalization pathways. While this approach provides a good starting point, it may not be flexible enough for all use cases. Here are a few potential improvements:

- **Custom Pathways**: Allow users to define their own normalization pathways. This could be done by accepting a document that defines custom pathways, or by providing a user interface where users can create and manage their pathways.
- **Targeted Normalization**: Add the ability to target specific MIME types for normalization. This would allow users to focus on the file types that are most relevant to their needs, potentially improving performance.
- **Dynamic Pathways**: Instead of defining all pathways upfront, consider a dynamic approach where pathways are created on-the-fly based on the files being processed. This could make the tool more adaptable to different types of files and data sets.

These improvements would require significant changes to the script, but they could make the tool more flexible and useful for a wider range of use cases. As always, contributions are welcome!

## Contributing

Contributions are welcome! Please submit a pull request or create an issue if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Note on Local Installation

While it is technically possible to run this script directly on your local machine, we strongly recommend using Docker. Docker ensures that all dependencies are correctly installed and configured, and it isolates the project from your local environment, reducing the risk of conflicts or other issues. If you choose to run the script locally, you will need to manually install and configure all dependencies, and we cannot guarantee that the script will work as expected.