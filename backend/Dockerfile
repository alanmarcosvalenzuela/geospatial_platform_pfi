FROM ghcr.io/osgeo/gdal:ubuntu-small-3.6.4

#ENV VARIABLES

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# INSTALL GIT

RUN apt update && apt install -y git python3-pip ffmpeg libsm6 libxext6

# Clone the GitHub repository
RUN git  clone https://github.com/alanmarcosvalenzuela/geospatial_platform_pfi.git .

# Change the working directory to "backend"
WORKDIR /app/backend
COPY entrypoint.sh .

# Installing python libraries
RUN pip3 install GDAL==3.6.4

RUN pip3 install -r requirements.txt

RUN pip3 install psycopg2-binary

# Add Baselayer
RUN sed -i 's|https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}|https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}|g' /usr/local/lib/python3.10/dist-packages/samgeo/common.py

# Expose port 8000 for the Django development server
EXPOSE 8000