import os
import threading
import time

from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.http import FileResponse
from django.urls import reverse
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from samgeo import tms_to_geotiff
from samgeo.text_sam import LangSAM
from user_api.models import AppUser
from gee.authenticate_gee import ee
import geemap
from datetime import date, timedelta


from .models import GeoProcess, Report


class UserReportsAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, email, format=None):
        try:
            user = AppUser.objects.get(email=email)
            reports = Report.objects.filter(geo_process__user=user)
            serialized_reports = [
                {
                    'id': report.id,
                    'title': report.title,
                    'description': report.description,
                    'status': report.geo_process.status,
                    'file': request.build_absolute_uri(reverse('report-download', args=[report.id])) if report.file else None
                }
                for report in reports
            ]
            return Response({'user_reports': serialized_reports}, status=status.HTTP_200_OK)
        except AppUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class ReportDownloadView(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, report_id, format=None):
        try:
            report = Report.objects.get(pk=report_id)
            if report.file:
                response = FileResponse(report.file, as_attachment=True)
                return response
            else:
                return Response({'message': 'Report file not found'}, status=status.HTTP_404_NOT_FOUND)
        except Report.DoesNotExist:
            return Response({'message': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)


class GeoProcessStatusAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, geoprocess_id, format=None):
        try:
            geoprocess = GeoProcess.objects.get(pk=geoprocess_id)
            return Response({'status': geoprocess.status}, status=status.HTTP_200_OK)
        except GeoProcess.DoesNotExist:
            return Response({'message': 'GeoProcess not found'}, status=status.HTTP_404_NOT_FOUND)


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class Process(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def gee_ndvi(self):

        pass


    def send_email(self, email, report_pdf_path, title_file, description_file):
        
        subject = f"Terradata - Geoproceso: {title_file}"
        body = f"{description_file} ---> Ejecutado con éxito"
        from_email = "terradata2023@gmail.com"

        try:
            email_message = EmailMessage(subject, body, from_email, [email])
            email_message.attach_file(report_pdf_path)
            email_message.send()
        except Exception as e:
            print(e)


    def generate_pdf(self, image_path, title, output_path):

        try:
            c = canvas.Canvas(output_path, pagesize=letter)
            c.setFont("Helvetica", 12)
            # Add centered title
            c.drawCentredString(300, 750, title)
            # Add image
            c.drawImage(image_path, 100, 400, width=400, height=300)
            c.save()
        except Exception as e:
            print(e)


    def async_function(self, geoprocess, bbox, option, email):

        xmin = bbox['xmin']
        ymin = bbox['ymin']
        xmax = bbox['xmax']
        ymax = bbox['ymax']
        # Create the desired format
        bbox_formatted = [xmin, ymin, xmax, ymax]


        if option == "arboles":
            image = "Image.tif"
            tms_to_geotiff(output=image, bbox=bbox_formatted, zoom=19, source="ESRI", overwrite=True)
            sam = LangSAM()

            sam.predict(image, 'tree', box_threshold=0.22, text_threshold=0.22)
            output_file = 'arboles.tif'
            title_file = 'Segmentación Automática de Zonas Verdes'
            description_file = 'Reporte describiendo los resultados de la segmentación de espacios verdes.'
            sam.show_anns(
                cmap='Greens',
                box_color='red',
                title='',
                output=output_file)
        elif option == "piletas":
            image = "Image.tif"
            tms_to_geotiff(output=image, bbox=bbox_formatted, zoom=19, source="ESRI", overwrite=True)
            sam = LangSAM()

            sam.predict(image, 'swimming pool', box_threshold=0.23, text_threshold=0.23)
            output_file = 'pools.tif'
            title_file = 'Segmentación Automática de Piletas'
            description_file = 'Reporte describiendo los resultados de la segmentación de piletas.'
            sam.show_anns(
                cmap='Blues',  # You can adjust the colormap as needed
                box_color='red',
                title='',
                output=output_file)
        elif option == "construcciones_sam":
            image = "Image.tif"
            tms_to_geotiff(output=image, bbox=bbox_formatted, zoom=19, source="ESRI", overwrite=True)
            sam = LangSAM()

            sam.predict(image, 'ceiling', box_threshold=0.20, text_threshold=0.20)
            output_file = 'ceilings.tif'
            title_file = 'Segmentación Automática de Construcciones'
            description_file = 'Reporte describiendo los resultados de la segmentación de construcciones.'
            sam.show_anns(
                cmap='Greys',  # Adjust the colormap as needed
                box_color='red',
                title='',
                output=output_file)
        elif option == "agua":
            output_file = 'water.tif'
            title_file = 'Índices de Clasificación de Volumen de Agua'
            description_file = 'Reporte describiendo los resultados del índice de masa de agua.'

            today = date.today()
            yesterday = today - timedelta(days=1)
            six_months_ago = today - timedelta(days=180)

            bbox = ee.Geometry.Rectangle(bbox_formatted)

            # Date format
            start_date = six_months_ago.strftime('%Y-%m-%d')
            end_date = yesterday.strftime('%Y-%m-%d')
        
            # Filter image collection
            imgs_s2 = ee.ImageCollection('COPERNICUS/S2') \
                .filterDate(start_date, end_date) \
                .filterBounds(bbox) \
                .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 10)

            # Select image
            img = imgs_s2.sort('system:time_start').first()

            # Clip the image
            s2_clip = img.clip(bbox)

            # Calculate NDWI
            ndwi = s2_clip.normalizedDifference(['B3', 'B8'])

            # Export the image as a TIFF file
            geemap.ee_export_image(ndwi.visualize(min=-0.5, max=1, palette=['FFFFFF','0000FF']), filename=output_file, scale=10, region=bbox, file_per_band=False)
        elif option == "vegetacion":
            output_file = 'ndvi.tif'
            title_file = 'Índices de Clasificación de Vegetación'
            description_file = 'Reporte describiendo los resultados del índice de vegetación.'

            today = date.today()
            yesterday = today - timedelta(days=1)
            six_months_ago = today - timedelta(days=180)

            bbox = ee.Geometry.Rectangle(bbox_formatted)

            # Date format
            start_date = six_months_ago.strftime('%Y-%m-%d')
            end_date = yesterday.strftime('%Y-%m-%d')
        
            # Filter image collection
            imgs_s2 = ee.ImageCollection('COPERNICUS/S2') \
                .filterDate(start_date, end_date) \
                .filterBounds(bbox) \
                .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 10)

            # Select image
            img = imgs_s2.sort('system:time_start').first()

            # Clip the image
            s2_clip = img.clip(bbox)

            # Calculate NDVI
            ndvi = s2_clip.expression("(nir-red)/(nir+red)", {
                "nir": s2_clip.select("B8"),
                "red": s2_clip.select("B3")
            })

            # Export the image as a TIFF file
            geemap.ee_export_image(ndvi.visualize(min=0, max=0.5, palette=['FFFFFF', 'CE7E45', 'DF923D', 'F18555', 'FCD163', '99B718', '74A901', '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01', '012E01', '011D01', '011301']), filename=output_file, scale=10, region=bbox, file_per_band=False)
        else:
            # Handle an invalid option here if needed
            print("Funcionalidades de GEE en desarrollo")

        # Replace with the actual filename generated by sam.show_anns
        report_pdf_path = output_file.replace('.tif', '.pdf')

        # Generate PDF
        self.generate_pdf(output_file, title_file, report_pdf_path)

        report_instance = Report.objects.create(
            geo_process=geoprocess,
            title= title_file,
            description= description_file
        )

        # Save the report file to the media directory
        with open(report_pdf_path, 'rb') as f:
            report_pdf_content = File(f)
            report_instance.file.save(os.path.basename(report_pdf_path), report_pdf_content)
        
        # Send email
        self.send_email(email, report_pdf_path, title_file, description_file)
        
        geoprocess.status = 'Finalizado'
        geoprocess.save()
        print("Función asíncrona finalizada")


    def process_async(self, bbox, option, email, geoprocess):
        self.async_function(geoprocess, bbox, option, email)
    

    def create_geoprocess(self, bbox, email):
        user = AppUser.objects.get(email=email)
        status_arg = 'En curso'
        geo_process_instance = GeoProcess(status=status_arg, bbox=bbox, user=user)
        return geo_process_instance

	
    def post(self, request, format=None):
        bbox = request.data.get('bbox')
        option = request.data.get('option')
        email = request.data.get('email')
        geoprocess = self.create_geoprocess(bbox, email)
        geoprocess.save()
        
        try:
            if bbox and option and email:
                print('Received bbox:', bbox)
                print('Received option:', option)
                print('Received email:', email)
                # Comienza proceso asincronico en hilo separado
                thread = threading.Thread(target=self.process_async, args=(bbox, option, email, geoprocess))
                thread.start()
                return Response({'id': geoprocess.id}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("An error occurred:", str(e))
            geoprocess.status = 'Error'
            geoprocess.save()
            return Response({'message': 'An error occurred', 'id': geoprocess.id}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
