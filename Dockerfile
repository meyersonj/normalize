FROM python:3.12-rc-bullseye

# Install Java runtime
RUN apt-get update && apt-get install -y default-jre=2:1.11-72

# Install LibreOffice
RUN apt-get install -y libreoffice=1:7.0.4-4+deb11u7

# Install FFmpeg
RUN apt-get install -y ffmpeg=7:4.3.6-0+deb11u1

# Install Inkscape
RUN apt-get install -y inkscape=1.0.2-4 wget unzip xvfb

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

RUN wget https://cdn.nationalarchives.gov.uk/documents/droid-binary-6.5.2-bin.zip  && unzip -o droid-binary-6.5.2-bin.zip

RUN wget https://cdn.nationalarchives.gov.uk/documents/droid-binary-6.6.1-bin.zip  && unzip -o droid-binary-6.6.1-bin.zip

RUN wget https://cdn.nationalarchives.gov.uk/documents/DROID_SignatureFile_V111.xml 
# Set the command to run the application
#CMD [ "python", "./app.py" ]