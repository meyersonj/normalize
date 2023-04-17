
.PHONY: test
test: python3 -m unittest convert_test.TestFileConversion

.PHONY: get-droid
get-droid:
	wget https://cdn.nationalarchives.gov.uk/documents/droid-binary-6.5.2-bin.zip
	unzip droid-binary-6.5.2-bin.zip
	wget https://cdn.nationalarchives.gov.uk/documents/DROID_SignatureFile_V111.xml


.PHONY: macos-reqs
macos-reqs:
	brew install ffmpeg
	brew install inkscape
	brew install ffmpeg

.PHONY: build
build:
	docker build -t convert:local ./  


.PHONY: docker-test
docker-test:
	docker run -it -v $(PWD):/app convert:local /bin/bash