import os
import threading
from datetime import date, datetime, timedelta

import geemap
from django.contrib.gis.geos import Polygon
from django.core.files import File
from django.core.mail import EmailMessage
from django.http import FileResponse
from django.urls import reverse
from gee.authenticate_gee import ee
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from samgeo import tms_to_geotiff
from samgeo.text_sam import LangSAM
from user_api.models import AppUser

from .models import GeoProcess, Layer, Metadata, Report


class UserReportsAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, email, format=None):
        try:
            user = AppUser.objects.get(email=email)
            reports = Report.objects.filter(geo_process__user=user).order_by('-id')
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


class Process(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def send_email(self, email, report_pdf_path, title_file, description_file):
        
        subject = f"Terradata - Geoproceso: {title_file}"
        body = f"{description_file}\n\nEjecutado con éxito\n\n\n\nTerradata © 2023"
        from_email = "terradata2023@gmail.com"

        try:
            email_message = EmailMessage(subject, body, from_email, [email])
            email_message.attach_file(report_pdf_path)
            email_message.send()
        except Exception as e:
            print(e)

    def get_rgb_ndwi(self, color):
        color_mappings = {
            "red": (1, 0, 0),
            "yellow": (1, 1, 0),
            "green": (0, 1, 0),
            "cyan": (0, 1, 1),
            "blue": (0, 0, 1),
        }
        return color_mappings.get(color, (0, 0, 0))
    
    def get_rgb_ndvi(self, color):
        color_mappings = {
            "Rojo": (1, 0, 0),
            "Amarillo": (1, 1, 0),
            "Verde": (0, 1, 0),
            "Nula": (0.8, 0.8, 0.8),
            "Baja o Escasa": (0.804, 0.522, 0.247),
            "Con Variabilidad": (1, 1, 0.5),
            "Media": (0, 1, 0),
            "Alta": (0.0, 0.502, 0.251),
        }
        return color_mappings.get(color, (0, 0, 0))


    def generate_pdf_sam(self, image_path, title, output_path, additional_info):
        try:
            c = canvas.Canvas(output_path, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)  # Cambiado a negrita y tamaño aumentado
            
            # Add centered title
            c.drawCentredString(300, 750, title)
            
            # Add image
            c.drawImage(image_path, 100, 400, width=400, height=300)
            
            # Add additional information
            additional_info_title = "Información adicional"
            c.setFont("Helvetica-Bold", 12)  # Cambiado a negrita
            c.drawString(100, 350, additional_info_title)  # Posición ajustada
            
            info_y_position = 330  # Aumentado el espacio entre líneas
            for key, value in additional_info.items():
                c.setFont("Helvetica-Bold", 12)  # Cambiado a tamaño 12
                c.setFillColorRGB(0, 0, 0)  # Cambiado a color negro
                if key == "Bounding box":
                    c.drawString(120, info_y_position, "•")  # Bullet point
                    c.drawString(130, info_y_position, f"{key}:")
                    info_y_position -= 15
                    for k, v in value.items():
                        c.drawString(150, info_y_position, f"{k}: {v}")
                        info_y_position -= 15
                    info_y_position -= 5
                else:
                    c.drawString(120, info_y_position, "•")  # Bullet point
                    c.drawString(130, info_y_position, f"{key}: {value}")
                    info_y_position -= 20
            
            # Add footer
            c.setFont("Helvetica-Bold", 8)
            c.setFillColorRGB(0, 0, 0)  # Cambiado a color negro
            c.drawString(400, 30, "Generado por Terradata ©")
            
            c.save()
        except Exception as e:
            print(e)

    def generate_pdf_index(self, image_path, title, output_path, additional_info, is_ndvi):
        try:
            c = canvas.Canvas(output_path, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)  # Cambiado a negrita y tamaño aumentado
            
            # Add centered title
            c.drawCentredString(300, 750, title)
            
            # Add image
            c.drawImage(image_path, 100, 400, width=400, height=300)
            
            # Add references
            references_title = "Referencias"
            c.setFont("Helvetica-Bold", 12)  # Cambiado a negrita y tamaño 12
            c.drawString(100, 350, references_title)  # Posición ajustada con más espacio

            if is_ndvi:
            
                meanings = [
                    "Nula",
                    "Baja o Escasa",
                    "Con Variabilidad",
                    "Media",
                    "Alta"
                ]
                
                colors = [
                    self.get_rgb_ndvi("Nula"),
                    self.get_rgb_ndvi("Baja o Escasa"),
                    self.get_rgb_ndvi("Con Variabilidad"),
                    self.get_rgb_ndvi("Media"),
                    self.get_rgb_ndvi("Alta")
                ]
            
            else:

                meanings = [
                    "Muy Bajo",
                    "Bajo",
                    "Moderado",
                    "Alto",
                    "Muy Alto"
                ]
                
                colors = [
                    self.get_rgb_ndwi("red"),
                    self.get_rgb_ndwi("yellow"),
                    self.get_rgb_ndwi("green"),
                    self.get_rgb_ndwi("cyan"),
                    self.get_rgb_ndwi("blue"),
                ]
                
            color_y_position = 320
            for color, meaning in zip(colors, meanings):
                c.setFillColorRGB(*color)  # Usar el color específico
                c.rect(100, color_y_position, 20, 20, fill=True, stroke=False)
                c.setFont("Helvetica-Bold", 12)
                c.setFillColorRGB(0, 0, 0)  # Cambiado a color negro
                c.drawString(130, color_y_position + 5, f"{meaning}")  # Cambiado a solo el tipo de vegetación
                color_y_position -= 25  # Aumentado el espacio entre líneas
            
            # Add additional information
            additional_info_title = "Información adicional"
            c.setFont("Helvetica-Bold", 12)  # Cambiado a negrita
            c.drawString(100, 200, additional_info_title)  # Posición ajustada
            
            info_y_position = 180  # Aumentado el espacio entre líneas
            for key, value in additional_info.items():
                c.setFont("Helvetica-Bold", 12)  # Cambiado a tamaño 12
                c.setFillColorRGB(0, 0, 0)  # Cambiado a color negro
                c.drawString(120, info_y_position, "•")  # Bullet point
                c.drawString(130, info_y_position, f"{key}: {value}")
                info_y_position -= 20
            
            # Add footer
            c.setFont("Helvetica-Bold", 8)
            c.setFillColorRGB(0, 0, 0)  # Cambiado a color negro
            c.drawString(400, 30, "Generado por Terradata ©")
            
            c.save()
        except Exception as e:
            print(e)
    

    def get_metadata(self, metadata, geoprocess_id):
        
        timestamp_ms = (metadata['properties']['system:time_start']) / 1000  # Convert to seconds
        date_image = datetime.utcfromtimestamp(timestamp_ms).strftime('%Y-%m-%d')

        additional_info = {
            "ID": metadata['id'],
            "Versión": metadata['version'],
            "Satélite": metadata['properties']['SPACECRAFT_NAME'],
            "Porcentaje de Nubosidad": metadata['properties']['CLOUDY_PIXEL_PERCENTAGE'],
            "Fecha de Imagen": date_image,
            "ID de Geoproceso": geoprocess_id,
            }
        

        return additional_info


    def async_function(self, geoprocess, bbox, option, email):

        try:

            xmin = bbox['xmin']
            ymin = bbox['ymin']
            xmax = bbox['xmax']
            ymax = bbox['ymax']
            # Create the desired format
            bbox_formatted = [xmin, ymin, xmax, ymax]
            time_ejecution = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


            if option == "arboles":
                is_segment = True
                source = "GeoSam"
                image = "Image.tif"
                tms_to_geotiff(output=image, bbox=bbox_formatted, zoom=19, source="SATELLITE", overwrite=True)
                sam = LangSAM()

                sam.predict(image, 'tree', box_threshold=0.22, text_threshold=0.22)

                phrases = sam.phrases
                cont_phrases = len(phrases)

                output_file = 'arboles.tif'
                title_file = 'Segmentación Automática de Zonas Verdes'
                description_file = 'Reporte describiendo los resultados de la segmentación de espacios verdes.'
                sam.show_anns(
                    cmap='Greens',
                    box_color='red',
                    title='GeoSam',
                    output=output_file)
            elif option == "piletas":
                is_segment = True
                source = "GeoSam"
                image = "Image.tif"
                tms_to_geotiff(output=image, bbox=bbox_formatted, zoom=19, source="SATELLITE", overwrite=True)
                sam = LangSAM()

                sam.predict(image, 'swimming pool', box_threshold=0.23, text_threshold=0.23)

                phrases = sam.phrases
                cont_phrases = len(phrases)

                output_file = 'pools.tif'
                title_file = 'Segmentación Automática de Piletas'
                description_file = 'Reporte describiendo los resultados de la segmentación de piletas.'
                sam.show_anns(
                    cmap='Blues',  # You can adjust the colormap as needed
                    box_color='red',
                    title='GeoSam',
                    output=output_file)
            elif option == "construcciones_sam":
                is_segment = True
                source = "GeoSam"
                image = "Image.tif"
                tms_to_geotiff(output=image, bbox=bbox_formatted, zoom=19, source="SATELLITE", overwrite=True)
                sam = LangSAM()

                sam.predict(image, 'ceiling', box_threshold=0.20, text_threshold=0.20)

                phrases = sam.phrases
                cont_phrases = len(phrases)

                output_file = 'ceilings.tif'
                title_file = 'Segmentación Automática de Construcciones'
                description_file = 'Reporte describiendo los resultados de la segmentación de construcciones.'
                sam.show_anns(
                    cmap='Greys',  # Adjust the colormap as needed
                    box_color='red',
                    title='',
                    output=output_file)
            elif option == "agua":
                is_segment = False
                is_ndvi = False
                source = "GEE"
                output_file = 'water.tif'
                title_file = 'Índices de Clasificación de Volumen de Agua'
                description_file = 'Reporte describiendo los resultados del índice de masa de agua.'

                today = date.today()
                yesterday = today - timedelta(days=1)
                six_months_ago = today - timedelta(days=180)
                
                bbox_geometry = ee.Geometry.Rectangle(bbox_formatted)

                # Date format
                start_date = six_months_ago.strftime('%Y-%m-%d')
                end_date = yesterday.strftime('%Y-%m-%d')
            
                # Filter image collection
                imgs_s2 = ee.ImageCollection('COPERNICUS/S2') \
                    .filterDate(start_date, end_date) \
                    .filterBounds(bbox_geometry) \
                    .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 10)

                # Select image
                img = imgs_s2.sort('system:time_start', False).first()

                # Get metadata
                metadata = img.getInfo()

                geoprocess_id = geoprocess.id
                additional_info = self.get_metadata(metadata, geoprocess_id)

                # Clip the image
                s2_clip = img.clip(bbox_geometry)

                # Calculate NDWI
                ndwi = s2_clip.normalizedDifference(['B3', 'B8']).rename('NDWI')

                # Export the image as a TIFF file
                geemap.ee_export_image(ndwi.visualize(palette=['red', 'yellow', 'green', 'cyan', 'blue']), filename=output_file, scale=10, region=bbox_geometry, file_per_band=False)
            elif option == "vegetacion":
                is_segment = False
                is_ndvi = True
                source = "GEE"
                output_file = 'ndvi.tif'
                title_file = 'Índices de Clasificación de Vegetación'
                description_file = 'Reporte describiendo los resultados del índice de vegetación.'

                today = date.today()
                yesterday = today - timedelta(days=1)
                six_months_ago = today - timedelta(days=180)

                bbox_geometry = ee.Geometry.Rectangle(bbox_formatted)

                # Date format
                start_date = six_months_ago.strftime('%Y-%m-%d')
                end_date = yesterday.strftime('%Y-%m-%d')
            
                # Filter image collection
                imgs_s2 = ee.ImageCollection('COPERNICUS/S2') \
                    .filterDate(start_date, end_date) \
                    .filterBounds(bbox_geometry) \
                    .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 10)

                # Select image
                img = imgs_s2.sort('system:time_start', False).first()
                
                # Get metadata
                metadata = img.getInfo()

                geoprocess_id = geoprocess.id
                additional_info = self.get_metadata(metadata, geoprocess_id)

                # Clip the image
                s2_clip = img.clip(bbox_geometry)

                # Calculate NDVI
                ndvi = s2_clip.expression("(nir-red)/(nir+red)", {
                    "nir": s2_clip.select("B8"),
                    "red": s2_clip.select("B3")
                })

                palette = ['FFFFFF', 'CE7E45', 'DF923D', 'F18555', 'FCD163', '99B718', '74A901', '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01', '012E01', '011D01', '011301']

                # Export the image as a TIFF file
                geemap.ee_export_image(ndvi.visualize(min=0, max=1, palette=palette), filename=output_file, scale=10, region=bbox_geometry, file_per_band=False)

            else:
                # Handle an invalid option here if needed
                print("Funcionalidades de GEE en desarrollo")

            # Replace with the actual filename generated by sam.show_anns
            report_pdf_path = output_file.replace('.tif', '.pdf')

            # Generate PDF

            report_instance = Report.objects.create(
                geo_process=geoprocess,
                title= title_file,
                description= description_file
            )

            if is_segment:
                additional_info = {
                    "Cantidad de Ocurrencias": cont_phrases,
                    "Bounding box": bbox,
                    "ID de Geoproceso": geoprocess.id,
                    "ID de Reporte": report_instance.id,
                    "Hora de Ejecución": time_ejecution,
                }
                self.generate_pdf_sam(output_file, title_file, report_pdf_path, additional_info)
            else:
                additional_info["ID de Reporte"] = report_instance.id
                additional_info["Hora de Ejecución"] = time_ejecution
                self.generate_pdf_index(output_file, title_file, report_pdf_path, additional_info, is_ndvi)

            # Save the report file to the media directory
            with open(report_pdf_path, 'rb') as f:
                report_pdf_content = File(f)
                report_instance.file.save(os.path.basename(report_pdf_path), report_pdf_content)
            
            # Send email
            self.send_email(email, report_pdf_path, title_file, description_file)

            new_layer = Layer(
                geo_process=geoprocess, 
                title=f'Layer de {title_file}',
                description=description_file,
                type_layer='Raster',
                bbox=Polygon.from_bbox(bbox_formatted)
            )
            new_layer.save()

            user_instancia = AppUser.objects.get(email=email)
            current_datetime = datetime.now()

            metadata = Metadata(
                name=f'Metadata {title_file}',
                description=description_file,
                layer=new_layer,
                keywords='',
                source=source,
                attribution='',
                created_by=user_instancia,
                creation_date=current_datetime,
                zoom=''
            )

            metadata.save()
            
            geoprocess.status = 'Finalizado'
            geoprocess.save()
            print("Función asíncrona finalizada")
        
        except Exception as e:
            print(e)


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
