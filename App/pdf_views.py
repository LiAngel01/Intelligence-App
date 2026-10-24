from django.http import HttpResponse
from django.template.loader import render_to_string
#from weasyprint import HTML
from .models import Incident
from datetime import datetime, time, timedelta
from django.utils import timezone

def export_report_pdf(request):
    incidents = Incident.objects.none()
    incident_date_start = request.GET.get('fecha_incidencia_start', '')
    incident_date_end = request.GET.get('fecha_incidencia_end', '')

    if incident_date_start:
        try:
            start_date = datetime.strptime(incident_date_start, '%Y-%m-%d')
            start_datetime = timezone.make_aware(datetime.combine(start_date, time.min))
        except ValueError:
            start_datetime = None
    else:
        start_datetime = None

    if incident_date_end:
        try:
            end_date = datetime.strptime(incident_date_end, '%Y-%m-%d')
            end_datetime = timezone.make_aware(datetime.combine(end_date, time.max))
        except ValueError:
            end_datetime = None
    else:
        end_datetime = None

    if start_datetime and end_datetime:
        incidents = Incident.objects.filter(incident_date__gte=start_datetime, incident_date__lte=end_datetime)
    elif start_datetime:
        next_day = start_datetime + timedelta(days=1)
        incidents = Incident.objects.filter(incident_date__gte=start_datetime, incident_date__lt=next_day)
    elif end_datetime:
        incidents = Incident.objects.filter(incident_date__lte=end_datetime)

    html_string = render_to_string('App/report.html', {'incidents': incidents})
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="parte.pdf"'
    return response
