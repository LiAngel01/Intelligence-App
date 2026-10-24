import os
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Incident, REGIONS
from datetime import datetime, time
from django.utils import timezone
import textwrap

@login_required
def generate_report_image(request):
    # Configuración de página (tamaño carta en píxeles a 96 DPI)
    width, height = 816, 1056  # 8.5*96 = 816, 11*96 = 1056
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Configuración de fuentes
    font_path = os.path.join(settings.BASE_DIR, 'App', 'static', 'App', 'fonts', 'arial.ttf')
    try:
        title_font = ImageFont.truetype(font_path, size=18)
        header_font = ImageFont.truetype(font_path, size=14)
        body_font = ImageFont.truetype(font_path, size=12)
    except IOError:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    # Obtener parámetros de fecha
    start_date = request.GET.get('fecha_incidencia_start', '')
    end_date = request.GET.get('fecha_incidencia_end', '')

    # Filtrar incidencias
    incidents = Incident.objects.all()
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            incidents = incidents.filter(incident_date__gte=start_date)
        except ValueError:
            pass

    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            incidents = incidents.filter(incident_date__lte=end_date)
        except ValueError:
            pass

    # Configuración de diseño
    margin = 50
    current_y = margin
    line_height = 20
    max_width = width - 2 * margin

    # Título del documento
    draw.text((width/2, current_y), "REPORTE DE INCIDENCIAS", font=title_font, fill='black', anchor='mt')
    current_y += line_height * 2

    # Rango de fechas
    if start_date and end_date:
        draw.text((width/2, current_y), 
                 f"Período: Desde {start_date.strftime('%d/%m/%Y')} hasta {end_date.strftime('%d/%m/%Y')}", 
                 font=header_font, fill='black', anchor='mt')
        current_y += line_height * 1.5

    # Listado de incidencias en formato de oraciones
    for incident in incidents:
        # Cuerpo en formato de párrafo
        if incident.activity_type == "Contrarevolución":
            activity_adjective="contrarevolucionaria"
        elif incident.activity_type == "Delictiva":
            activity_adjective="delictiva"
        else:
            activity_adjective='de interes'
        report_text = (
            f"El {incident.informant} reportó una actividad {activity_adjective} relacionada con: {incident.activities}  "
            #
            f"ocurrida el día {incident.incident_date.strftime('%d/%m/%Y')} "
            f"{f'a las {incident.incident_time.strftime('%H:%M')}' if incident.incident_time else ''} "
            f"en el {incident.municipality}"
            f"de la región de {incident.territory}. "
            
        )

        # Agregar campos opcionales si existen
        if incident.involved_parties:
            report_text += f"Implicadas: {incident.involved_parties}. "

        # Ajustar texto al ancho
        for line in textwrap.wrap(report_text, width=135 ):  # ~90 caracteres por línea
            draw.text((margin, current_y), line, font=body_font, fill='black')
            current_y += line_height

        # Separador
        draw.line((margin, current_y + 10, width - margin, current_y + 10), fill='white', width=1)
        current_y += line_height * 1.5

        # Control de espacio en página
        if current_y > height - margin - 100:  # Dejar margen para pie de página
            break

    footer = f"Parte generado el {timezone.now().strftime('%d/%m/%Y a las %H:%M')}"
    draw.text((width/2, height - margin), footer, font=body_font, fill='black', anchor='mb')
    
    # Nuevo: Pie de firma en la parte inferior derecha
    footer_text = [
        "Jefe UM-4261",
        "José Javier Martínez león",
        "_________________________"
    ]
    
    # Configuración del pie de firma
    footer_y = height - margin - 70  # 80px arriba del footer existente
    right_margin = margin  # Alineado con el margen derecho
    
    # Dibujar cada línea del pie de firma
    for i, line in enumerate(footer_text):
        text_width = draw.textlength(line, font=body_font)  # Usar textlength en lugar de textsize
        x_position = width - right_margin - text_width
        y_position = footer_y + (i * 25)  # Espaciado vertical de 25px
        
        draw.text((x_position, y_position), line, font=body_font, fill="black")
    
    # Guardar y devolver la imagen (código existente)
    current_date = datetime.now().strftime("%Y%m%d")
    filename = f"reporte_incidencias_{current_date}.png"
    
    response = HttpResponse(content_type="image/png")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    image.save(response, "PNG")
    return response

@login_required
def generate_activity_table_image(request):
    # Configuración de página
    width, height = 1300, 1800
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # Configuración de fuentes
    font_path = os.path.join(settings.BASE_DIR, 'App', 'static', 'App', 'fonts', 'arial.ttf')
    try:
        title_font = ImageFont.truetype(font_path, size=24)
        header_font = ImageFont.truetype(font_path, size=14)
        body_font = ImageFont.truetype(font_path, size=14)
    except IOError:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    # Datos para activity_table
    counterrevolution_activities = [
        "Actos Vandálicos",
        "Planes SIP",
        "Intentos de Salida Ilegal del Pais (ISIP)",
        "Salida ilegal del pais",
        "Propagandas,carteles C/R",
        "Expresiones C/R",
        "Llamadas anónimas de porte alarmistas",
        "Reclamos Sociales",
        "Profanación de bustos",
        "Alteración del orden en la vía pública",
        "Sabotajes o Atentados",
        "Captura de armamento o medios de uso militar",
    ]
    criminal_activities = [
        "Hechos relacionados con drogas",
        "Hechos con armas de fuego",
        "Incendios",
        "Hechos relacionados con extrajeros",
        "Hechos contra la vida",
        "Hurtos, robos con fuerza y violencia",
        "Hechos contra el ganado mayor",
        "Hechos contra miembros del MININT",
    ]

    territories = [region[0] for region in REGIONS]

    # Preparar counts
    counts = {}
    for activity in counterrevolution_activities + criminal_activities:
        counts[activity] = {}
        for territory in territories:
            count = Incident.objects.filter(activities__icontains=activity, territory=territory).count()
            counts[activity][territory] = count

    # Agregar totales
    for activity in counts:
        counts[activity]['Total'] = sum(counts[activity].values())

    # Diseño con bordes completos
    margin = 40
    current_y = margin
    line_height = 30
    first_col_width = 50
    actividad_col_width = 250
    border_color = 'black'
    border_width = 1

    # Título principal
    draw.text((width/2, current_y), "INCIDENCIAS POR ACTIVIDAD Y TERRITORIO", 
              font=title_font, fill='black', anchor='mt')
    current_y += line_height * 2

    def draw_table_section(title, activities):
        nonlocal current_y
        
        # Cálculo de anchos
        available_width = width - 2 * margin
        remaining_width = available_width - first_col_width - actividad_col_width
        num_territorios = len(territories) + 1
        col_width = remaining_width / num_territorios

        # Título de sección
        draw.text((width/2, current_y), title.upper(), 
                 font=header_font, fill='black', anchor='mt')
        current_y += line_height * 1.5

        # Coordenadas iniciales para bordes
        table_top = current_y - 10
        table_left = margin
        table_right = width - margin

        # Dibujar encabezados con bordes
        header_bottom = current_y + line_height
        
        # Borde superior de la tabla
        draw.line([(table_left, table_top), (table_right, table_top)], 
                 fill=border_color, width=border_width)

        # Encabezados con bordes verticales
        x_positions = [margin]  # Lista de posiciones X para bordes verticales
        
        # Columna No.
        cell_right = margin + first_col_width
        draw.rectangle([(margin, table_top), (cell_right, header_bottom)], 
                      outline=border_color, width=border_width)
        draw.text((margin + first_col_width/2, table_top + line_height/2), 
                 "No.", font=header_font, fill='black', anchor='mm')
        x_positions.append(cell_right)

        # Columna Actividad
        cell_right += actividad_col_width
        draw.rectangle([(x_positions[-1], table_top), (cell_right, header_bottom)], 
                      outline=border_color, width=border_width)
        draw.text((x_positions[-1] + actividad_col_width/2, table_top + line_height/2), 
                 "ACTIVIDAD", font=header_font, fill='black', anchor='mm')
        x_positions.append(cell_right)

        # Columnas de territorios
        for territory in territories + ['TOTAL']:
            cell_right += col_width
            draw.rectangle([(x_positions[-1], table_top), (cell_right, header_bottom)], 
                          outline=border_color, width=border_width)
            draw.text((x_positions[-1] + col_width/2, table_top + line_height/2), 
                     territory.upper(), font=header_font, fill='black', anchor='mm')
            x_positions.append(cell_right)

        # Borde inferior del encabezado
        draw.line([(table_left, header_bottom), (table_right, header_bottom)], 
                 fill=border_color, width=border_width)

        current_y = header_bottom

        # Filas de datos con bordes completos
        for idx, activity in enumerate(activities, start=1):
            row_top = current_y
            row_bottom = current_y + line_height
            
            # Dibujar bordes horizontales
            draw.line([(table_left, row_top), (table_right, row_top)], 
                     fill=border_color, width=border_width)
            
            # Columna No.
            draw.rectangle([(x_positions[0], row_top), (x_positions[1], row_bottom)], 
                          outline=border_color, width=border_width)
            draw.text((x_positions[0] + first_col_width/2, row_top + line_height/2), 
                     str(idx), font=body_font, fill='black', anchor='mm')

            # Columna Actividad (con ajuste de texto)
            actividad_text = activity
            if draw.textlength(activity, font=body_font) > actividad_col_width - 10:
                max_chars = int((actividad_col_width - 10) / 8)
                actividad_text = activity[:max_chars-3] + "..."
            
            draw.rectangle([(x_positions[1], row_top), (x_positions[2], row_bottom)], 
                          outline=border_color, width=border_width)
            draw.text((x_positions[1] + 5, row_top + line_height/2),
                     actividad_text, font=body_font, fill='black', anchor='lm')

            # Columnas de territorios
            for i, territory in enumerate(territories + ['Total']):
                cell_left = x_positions[2 + i]
                cell_right = x_positions[2 + i + 1] if (2 + i + 1) < len(x_positions) else table_right
                
                draw.rectangle([(cell_left, row_top), (cell_right, row_bottom)], 
                              outline=border_color, width=border_width)
                
                count = counts[activity].get(territory, 0)
                text = str(count) if count > 0 else "-"
                draw.text((cell_left + col_width/2, row_top + line_height/2), 
                         text, font=body_font, fill='black', anchor='mm')

            current_y = row_bottom

        # Borde inferior final de la tabla
        draw.line([(table_left, current_y), (table_right, current_y)], 
                 fill=border_color, width=border_width)
        
        current_y += line_height

    # Dibujar secciones de la tabla
    draw_table_section("Actividades Contrarevolucionarias", counterrevolution_activities)
    draw_table_section("Actividades Delictivas", criminal_activities)

    # Pie de página profesional
    footer_date = timezone.now().strftime('%d/%m/%Y %H:%M')
    footer_text = f"Generado el {footer_date} | UM-4261"
    
    # Firma alineada a la derecha
    signature_lines = [
        "Jefe UM-4261",
        "_________________________",
        "Nombre y Apellidos"
    ]
    
    footer_y = height - margin - 100
    for i, line in enumerate(signature_lines):
        text_width = draw.textlength(line, font=body_font)
        draw.text((width - margin - text_width, footer_y + (i * 30)), 
                 line, font=body_font, fill="black")

    # Pie central
    draw.text((width/2, height - margin), footer_text, 
             font=body_font, fill='black', anchor='mb')

    # Generar respuesta
    current_date = datetime.now().strftime("%Y%m%d")
    filename = f"tabla_incidencias_{current_date}.png"

    response = HttpResponse(content_type="image/png")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    image.save(response, "PNG")
    return response
