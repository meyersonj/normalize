# Convert

This is a small script created on the basis of an older `convert_all.py` and with help from ChatGPT.

## Current status

- [x] test_identify_file
- [x] test_convert_to_mp4
- [x] test_convert_to_doc
- [ ] test_convert_to_svg (Inkscape stalls? not sure why)
- [ ] test_convert_file
- [ ] test w/ some real reference data

## (non-python) Requirements

### Install
you will need
* java runtime
* libreoffice
* ffmpeg
* inkscape
* and probably some other stuff

Ideally eventually we version freeze all these os-level reqs. into a docker image, the current set is slow and generally non-repeatable.

### Adjust

**Please adjust the path to .jar and libreoffice binary in convert_all_chatgpt.py**

### Verify java runtime
you will need java runtime - verify with `java --version`

## Quick start

Once the above (non-python) reqs are satisfied - try this

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```




