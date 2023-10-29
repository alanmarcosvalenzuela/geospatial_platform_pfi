FROM ghcr.io/osgeo/gdal:ubuntu-small-3.6.4

#ENV VARIABLES

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# INSTALL GIT

RUN apt update && apt install -y git python3-pip ffmpeg libsm6 libxext6

# Clone the GitHub repository
RUN git  clone https://github.com/alanmarcosvalenzuela/geospatial_platform_pfi.git -b develop-postgres .

# Change the working directory to "backend"
WORKDIR /app/backend


# Installing python libraries
RUN pip3 install GDAL==3.6.4

RUN pip3 install -r requirements.txt

RUN pip3 install psycopg2-binary

# Expose port 8000 for the Django development server
EXPOSE 8000