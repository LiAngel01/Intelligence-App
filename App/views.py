from django.shortcuts import render,redirect
from .forms import IncidentForm,IncidentEditForm,OtherIncidentForm
from .models import Incident, UserAccount,OtherIncident
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.

from django.db.models.functions import ExtractMonth
from django.db.models import Count

from datetime import datetime
from django.db.models.functions import ExtractMonth
from django.db.models import Count

from django.db.models.functions import ExtractMonth
from django.db.models import Count
import json
from datetime import datetime

def dashboard(request):
    current_year = datetime.now().year
    all_months = list(range(1, 13))
    labels = [datetime(1900, m, 1).strftime('%B') for m in all_months]
    total_incidents=Incident.objects.all().count()
    # Aggregate counts by month and tipo_actividad for the year
    counterrevolution_data = (
        Incident.objects.filter(incident_date__year=current_year, activity_type='Contrarevolución')
        .annotate(month=ExtractMonth('incident_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    criminal_activity_data = (
        Incident.objects.filter(incident_date__year=current_year, activity_type='Delictiva')
        .annotate(month=ExtractMonth('incident_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # Determine current quarter months
    current_month = datetime.now().month
    if current_month <= 3:
        quarter_months = [1, 2, 3]
    elif current_month <= 6:
        quarter_months = [4, 5, 6]
    elif current_month <= 9:
        quarter_months = [7, 8, 9]
    else:
        quarter_months = [10, 11, 12]

    quarter_labels = [datetime(1900, m, 1).strftime('%B') for m in quarter_months]

    # Aggregate counts by month and tipo_actividad for the current quarter
    quarter_counterrevolution_data = (
        Incident.objects.filter(incident_date__year=current_year, activity_type='Contrarevolución', incident_date__month__in=quarter_months)
        .annotate(month=ExtractMonth('incident_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    quarter_criminal_activity_data = (
        Incident.objects.filter(incident_date__year=current_year, activity_type='Delictiva', incident_date__month__in=quarter_months)
        .annotate(month=ExtractMonth('incident_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # Prepare counts list with 0 for missing months
    def prepare_counts(data, months):
        data_months = [entry['month'] for entry in data]
        counts = [entry['count'] for entry in data]
        counts_full = []
        for m in months:
            if m in data_months:
                counts_full.append(counts[data_months.index(m)])
            else:
                counts_full.append(0)
        return counts_full

    counterrevolution_counts = prepare_counts(counterrevolution_data, all_months)
    criminal_activity_counts = prepare_counts(criminal_activity_data, all_months)

    quarter_counterrevolution_counts = prepare_counts(quarter_counterrevolution_data, quarter_months)
    quarter_criminal_activity_counts = prepare_counts(quarter_criminal_activity_data, quarter_months)

    form = OtherIncidentForm

    # Calculate region with most incidences
    top_territory_data = (
        Incident.objects.values('territory')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )
    top_territory = top_territory_data['territory'] if top_territory_data else None

    # Calculate count of incidences with today's date
    today = datetime.now().date()
    today_count = Incident.objects.filter(incident_date=today).count()

    # Calculate count and percentage of incidences per territory
    territory_counts = Incident.objects.values('territory').annotate(count=Count('id')).order_by('territory')
    territory_percentages = []
    for entry in territory_counts:
        percentage = (entry['count'] / total_incidents * 100) if total_incidents > 0 else 0
        territory_percentages.append({
            'territory': entry['territory'],
            'count': entry['count'],
            'percentage': round(percentage, 2)
        })

    # New code: count incidences by tipo_actividad for pie chart
    counterrevolution_total = Incident.objects.filter(activity_type='Contrarevolución').count()
    criminal_total = Incident.objects.filter(activity_type='Delictiva').count()
    other_incident_total = OtherIncident.objects.all().count()

    data = {
        'incidents': Incident.objects.all(),
        'form': form,
        'chart_labels': json.dumps(labels),
        'counterrevolution_data': json.dumps(counterrevolution_counts),
        'criminal_activity_data': json.dumps(criminal_activity_counts),
        'quarter_labels': json.dumps(quarter_labels),
        'quarter_counterrevolution_data': json.dumps(quarter_counterrevolution_counts),
        'quarter_criminal_activity_data': json.dumps(quarter_criminal_activity_counts),
        'total':total_incidents,
        'top_territory': top_territory,
        'today_count': today_count,
        'territory_percentages': territory_percentages,
        'pie_chart_labels': json.dumps(['Contrarevolución', 'Delictiva', 'OIncidencia']),
        'pie_chart_data': json.dumps([counterrevolution_total, criminal_total, other_incident_total]),
    }

    # Calculate count of incidences added after last user logout
    new_incidences_since_last_logout = 0
    if request.user.is_authenticated:
        user = request.user
        last_logout = getattr(user, 'last_logout', None)
        if last_logout:
            new_incidences_since_last_logout = Incident.objects.filter(created_at__gt=last_logout).count()

    data['new_incidences_since_last_logout'] = new_incidences_since_last_logout

    return render(request, "App/dashboard.html", data)

import json

def list_users(request):
    users = UserAccount.objects.all()
    data = {
        'users': users
    }
    return render(request, 'App/user_list.html', data)

from .forms import CustomUserCreationForm, UserUpdateForm

def add_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario agregado exitosamente.')
            return redirect('listar_usuarios')
        else:
            messages.error(request, 'Error al agregar usuario. Por favor revise el formulario.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'App/user_create.html', {'form': form})

from .forms import UserPasswordUpdateForm

def edit_user(request, pk):
    user = get_object_or_404(UserAccount, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        password_form = UserPasswordUpdateForm(request.POST)
        if form.is_valid() and password_form.is_valid():
            form.save()
            password1 = password_form.cleaned_data.get('password1')
            if password1:
                user.set_password(password1)
                user.save()
            messages.success(request, 'Usuario editado exitosamente.')
            return redirect('listar_usuarios')
        else:
            messages.error(request, 'Error al editar usuario. Por favor revise el formulario.')
    else:
        form = UserUpdateForm(instance=user)
        password_form = UserPasswordUpdateForm()
    return render(request, 'App/user_edit.html', {'form': form, 'password_form': password_form})




import json

@login_required
def add_incidence(request):
    counterrevolution_activities = [
        ("Actos Vandálicos","Actos Vandálicos"),
        ("Planes SIP","Planes SIP"),
        ("Intentos de Salida Ilegal del Pais (ISIP)","Intentos de Salida Ilegal del Pais (ISIP)"),
        ("Salida ilegal del pais","Salida ilegal del pais"),
        ("Propagandas,carteles C/R","Propagandas,carteles C/R"),
        ("Expresiones C/R","Expresiones C/R"),
        ("Llamadas anónimas de porte alarmistas","Llamadas anónimas de porte alarmistas"),
        ("Reclamos Sociales","Reclamos Sociales"),
        ("Profanación de bustos","Profanación de bustos"),
        ("Alteración del orden en la vía pública","Alteración del orden en la vía pública"),
        ("Sabotajes o Atentados","Sabotajes o Atentados"),
        ("Captura de armamento o medios de uso militar","Captura de armamento o medios de uso militar"),
    ]
    criminal_activities = [
        ("Hechos relacionados con drogas","Hechos relacionados con drogas"),
        ("Hechos con armas de fuego","Hechos con armas de fuego"),
        ("Incendios","incendios"),
        ("Hechos relacionados con extrajeros","Hechos relacionados con extrajeros"),
        ("Hechos contra la vida","Hechos contra la vida"),
        ("Hurtos, robos con fuerza y violencia","Hurtos, robos con fuerza y violencia"),
        ("Hechos contra el ganado mayor","Hechos contra el ganado mayor"),
        ("Hechos contra miembros del MININT","Hechos contra miembros del MININT"),
    ]

    municipalities_by_territory = {
        "Mayabeque": [
            "San José de las Lajas", "Batabanó", "Güines", "San Nicolás de Bari", "Santa Cruz del Norte",
            "Madruga", "Nueva Paz", "Quivicán", "Bejucal", "Jaruco", "Melena del Sur"
        ],
        "La Habana": [
            "Playa", "Plaza de la Revolución", "Centro Habana", "Habana Vieja", "Guanabacoa", "Regla",
            "San Miguel del Padrón", "Diez de Octubre", "Cerro", "Marianao", "La Lisa", "Boyeros",
            "Arroyo Naranjo", "Cotorro", "Habana del Este"
        ],
        "Artemisa": [
            "Artemisa", "Guanajay", "Mariel", "Bauta", "San Antonio de los Baños", "Caimito", "Bahía Honda",
            "Alquízar", "Güira de Melena", "San Cristóbal", "Candelaria"
        ],
        "Pinar del río": [
            "Pinar del Río", "Consolación del Sur", "Viñales", "San Luis", "Minas de Matahambre", "Guane",
            "La Palma", "Los Palacios", "San Juan y Martínez", "Mantua", "Sandino"
        ],
        "Isla de la Juventud": [
            "Nueva Gerona", "Santa Fe", "La Demajagua", "Columbia"
        ]
    }

    if request.method == 'POST':
        form = IncidentForm(request.POST, request.FILES) 
        '''  confirmed = request.POST.get('confirmed', 'false') == 'true'
        if not confirmed:
            formulario = IncidentForm(request.POST, request.FILES)
            data = {
                'form': formulario,
                'actividades_de_contrarevolucion': json.dumps(actividades_de_contrarevolucion),
                'actividades_delictivas': json.dumps(actividades_delictivas),
                'municipios_por_territorio': json.dumps(municipios_por_territorio),
            }
            messages.info(request, 'La creación de la incidencia fue cancelada por el usuario.')
            return render(request, 'App/incident_form.html', data)'''
        if 'save' in request.POST: 
            form = IncidentForm(request.POST, request.FILES)
            if form.is_valid():
                informant = form.cleaned_data.get('informant')
                otros_informante = request.POST.get('otros_informante', '').strip()
                if informant.lower() == 'otros' and otros_informante:
                    form.instance.informant = otros_informante
                form.save()
                messages.success(request, 'Incidencia agregada exitosamente.')
                return redirect('dashboard')
            else:
                messages.error(request, 'Error al agregar incidencia. Por favor revise el formulario.')
        if 'save_another' in request.POST: 
            form = IncidentForm(request.POST, request.FILES)
            if form.is_valid():
                informant = form.cleaned_data.get('informant')
                otros_informante = request.POST.get('otros_informante', '').strip()
                if informant.lower() == 'otros' and otros_informante:
                    form.instance.informant = otros_informante
                form.save()
                messages.success(request, 'Incidencia agregada exitosamente. Puede agregar otra.')
                return redirect('form')         
            else:
                messages.error(request, 'Error al agregar incidencia. Por favor revise el formulario.')
    else:
        form = IncidentForm()
    data = {
        'form': form,
        'counterrevolution_activities': json.dumps(counterrevolution_activities),
        'criminal_activities': json.dumps(criminal_activities),
        'municipios_por_territorio': json.dumps(municipalities_by_territory),
    }
    return render(request, 'App/incident_form.html', data)

def incident_list(request):
 incidents = Incident.objects.all()

# Filter incidences by logged-in user's region if role is TRABAJADOR
 if request.user.is_authenticated:
    user_role = getattr(request.user, 'role', None)
    user_region = getattr(request.user, 'region', None)
    if user_role == 'TRABAJADOR' and user_region:
        incidents = incidents.filter(territory=user_region)
    # If ADMIN, show all incidences (no filter)

 incident_date_start = request.GET.get('fecha_incidencia_start', '')
 incident_date_end = request.GET.get('fecha_incidencia_end', '')
 created_at = request.GET.get('created_at', '')
 informant = request.GET.get('informant', '')
 activity_type = request.GET.get('activity_type', '')
 activities = request.GET.get('activities', '')
 territory = request.GET.get('territory', '')
 municipality = request.GET.get('municipality', '')
 involved_parties = request.GET.get('involved_parties', '')
 additional_details = request.GET.get('additional_details', '')

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
    incidents = incidents.filter(incident_date__gte=start_datetime, incident_date__lte=end_datetime)
 elif start_datetime and not end_datetime:
    incidents = incidents.filter(incident_date=start_datetime)
 elif end_datetime:
    incidents = incidents.filter(incident_date__lte=end_datetime)
 if informant:
    incidents = incidents.filter(informant__icontains=informant)
 if activity_type:
    incidents = incidents.filter(activity_type__icontains=activity_type)
 if activities:
    incidents = incidents.filter(activities__icontains=activities)
 if territory:
    incidents = incidents.filter(territory__icontains=territory)
 if municipality:
    incidents = incidents.filter(municipality__icontains=municipality)
 if involved_parties:
    incidents = incidents.filter(involved_parties__icontains=involved_parties)
 if additional_details:
    incidents = incidents.filter(additional_details__icontains=additional_details)

 cant = incidents.count()
 
 data = {
    'incidents': incidents,
    'total_count': cant,
    'fecha_incidencia_start': incident_date_start,
    'fecha_incidencia_end': incident_date_end,
    'created_at': created_at,
    'informant': informant,
    'activity_type': activity_type,
    'activities': activities,
    'territory': territory,
    'involved_parties': involved_parties,
    'municipality':municipality,
    'additional_details': additional_details,
    'informant_choices': Incident._meta.get_field('informant').choices,
    'activity_type_choices': Incident._meta.get_field('activity_type').choices,
    'territory_choices': Incident._meta.get_field('territory').choices,
}
 return render(request, "App/incident_list.html", data)



def edit_incident(request, id):
    incident = get_object_or_404(Incident,id=id)
    counterrevolution_activities = [
        ("Actos Vandálicos","Actos Vandálicos"),
        ("Planes SIP","Planes SIP"),
        ("Intentos de Salida Ilegal del Pais (ISIP)","Intentos de Salida Ilegal del Pais (ISIP)"),
        ("Salida ilegal del pais","Salida ilegal del pais"),
        ("Propagandas,carteles C/R","Propagandas,carteles C/R"),
        ("Expresiones C/R","Expresiones C/R"),
        ("Llamadas anónimas de porte alarmistas","Llamadas anónimas de porte alarmistas"),
        ("Reclamos Sociales","Reclamos Sociales"),
        ("Profanación de bustos","Profanación de bustos"),
        ("Alteración del orden en la vía pública","Alteración del orden en la vía pública"),
        ("Sabotajes o Atentados","Sabotajes o Atentados"),
        ("Captura de armamento o medios de uso militar","Captura de armamento o medios de uso militar"),
    ]
    criminal_activities = [
        ("Hechos relacionados con drogas","Hechos relacionados con drogas"),
        ("Hechos con armas de fuego","Hechos con armas de fuego"),
        ("Incendios","incendios"),
        ("Hechos relacionados con extrajeros","Hechos relacionados con extrajeros"),
        ("Hechos contra la vida","Hechos contra la vida"),
        ("Hurtos, robos con fuerza y violencia","Hurtos, robos con fuerza y violencia"),
        ("Hechos contra el ganado mayor","Hechos contra el ganado mayor"),
        ("Hechos contra miembros del MININT","Hechos contra miembros del MININT"),
    ]

    municipalities_by_territory = {
        "Mayabeque": [
            "San José de las Lajas", "Batabanó", "Güines", "San Nicolás de Bari", "Santa Cruz del Norte",
            "Madruga", "Nueva Paz", "Quivicán", "Bejucal", "Jaruco", "Melena del Sur"
        ],
        "La Habana": [
            "Playa", "Plaza de la Revolución", "Centro Habana", "Habana Vieja", "Guanabacoa", "Regla",
            "San Miguel del Padrón", "Diez de Octubre", "Cerro", "Marianao", "La Lisa", "Boyeros",
            "Arroyo Naranjo", "Cotorro", "Habana del Este"
        ],
        "Artemisa": [
            "Artemisa", "Guanajay", "Mariel", "Bauta", "San Antonio de los Baños", "Caimito", "Bahía Honda",
            "Alquízar", "Güira de Melena", "San Cristóbal", "Candelaria"
        ],
        "Pinar del río": [
            "Pinar del Río", "Consolación del Sur", "Viñales", "San Luis", "Minas de Matahambre", "Guane",
            "La Palma", "Los Palacios", "San Juan y Martínez", "Mantua", "Sandino"
        ],
        "Isla de la Juventud": [
            "Nueva Gerona", "Santa Fe", "La Demajagua", "Columbia"
        ]
    }



    if request.method == 'POST':
        form = IncidentEditForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            messages.success(request, 'Incidencia editada exitosamente.')
            return redirect('incident_list')
        else:
            messages.error(request, 'Error al editar incidencia. Por favor revise el formulario.')
    else:
        # Format fecha_incidencia as YYYY-MM-DD string for HTML5 date input compatibility
        initial_data = {
            'incident_date': incident.incident_date.strftime('%Y-%m-%d') if incident.incident_date else None
        }
        form=IncidentEditForm(instance=incident, initial=initial_data)
    data={
        'form' : form,
        'counterrevolution_activities': json.dumps(counterrevolution_activities),
        'criminal_activities': json.dumps(criminal_activities),
        'municipios_por_territorio': json.dumps(municipalities_by_territory),
        }
    
    return render(request, 'App/incident_form.html', data )

def delete_incident(request, id):
    incident = get_object_or_404(Incident, id=id)
    incident.delete()
    messages.success(request, 'Incidencia eliminada exitosamente.')
    return redirect('incident_list')



def incident_detail(request,id):
    incident = get_object_or_404(Incident,id=id)
    data={
        'incident':incident
    }
    return render(request,"App/incident_detail.html",data)

from .models import REGIONS

@login_required
def activity_table(request):
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

    # Use all regions from modelos.regiones
    territories = [region[0] for region in REGIONS]

    # Prepare counts dictionary: {(actividad, territorio): count}
    counts = {}
    for activity in counterrevolution_activities + criminal_activities:
        counts[activity] = {}
        for territory in territories:
            count = Incident.objects.filter(activities=activity, territory=territory).count()
            counts[activity][territory] = count

    # Flatten counts to a list of dicts for template
    counts_list = []
    for activity in counterrevolution_activities + criminal_activities:
        total = sum(counts[activity].values())
        for territory in territories:
            counts_list.append({
                'activity': activity,
                'territory': territory,
                'count': counts[activity][territory]
            })
        # Add total as a special territory
        counts_list.append({
            'activity': activity,
            'territory': 'Total',
            'count': total
        })

    counterrevolution_mayabeque_count=Incident.objects.filter(activity_type="Contrarevolución",territory="Mayabeque").count()
    counterrevolution_havana_count=Incident.objects.filter(activity_type="Contrarevolución",territory="La Habana").count()
    counterrevolution_artemisa_count=Incident.objects.filter(activity_type="Contrarevolución",territory="Artemisa").count()
    counterrevolution_pinar_count=Incident.objects.filter(activity_type="Contrarevolución",territory="Pinar del Río").count()
    counterrevolution_isle_count=Incident.objects.filter(activity_type="Contrarevolución",territory="Isla de la Juventud").count()   

    criminal_mayabeque_count=Incident.objects.filter(activity_type="Delictiva",territory="Mayabeque").count()
    criminal_havana_count=Incident.objects.filter(activity_type="Delictiva",territory="La Habana").count()
    criminal_artemisa_count=Incident.objects.filter(activity_type="Delictiva",territory="Artemisa").count()
    criminal_pinar_count=Incident.objects.filter(activity_type="Delictiva",territory="Pinar del Río").count()
    criminal_isle_count=Incident.objects.filter(activity_type="Delictiva",territory="Isla de la Juventud").count()     
    print(counterrevolution_mayabeque_count)
    data = {
        'counterrevolution_activities': counterrevolution_activities,
        'criminal_activities': criminal_activities,
        'territories': territories + ['Total'],
        'counts_list': counts_list,
        'counterrevolution_mayabeque_count':counterrevolution_mayabeque_count,
        'counterrevolution_havana_count':counterrevolution_havana_count,
        'counterrevolution_artemisa_count':counterrevolution_artemisa_count,
        'counterrevolution_pinar_count':counterrevolution_pinar_count,
        'counterrevolution_isle_count':counterrevolution_isle_count,
        'criminal_mayabeque_count':criminal_mayabeque_count,
        'criminal_havana_count':criminal_havana_count,
        'criminal_artemisa_count':criminal_artemisa_count,
        'criminal_pinar_count':criminal_pinar_count,
        'criminal_isle_count':criminal_isle_count
    }
    return render(request,"App/activity_table.html",data)

def get_activity_table_data():
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

    # Use all regions from modelos.regiones
    territories = [region[0] for region in REGIONS]

    # Prepare counts dictionary: {(actividad, territorio): count}
    counts = {}
    for activity in counterrevolution_activities + criminal_activities:
        counts[activity] = {}
        for territory in territories:
            count = Incident.objects.filter(activities=activity, territory=territory).count()
            counts[activity][territory] = count

    # Flatten counts to a list of dicts for template
    counts_list = []
    for activity in counterrevolution_activities + criminal_activities:
        total = sum(counts[activity].values())
        for territory in territories:
            counts_list.append({
                'activity': activity,
                'territory': territory,
                'count': counts[activity][territory]
            })
        # Add total as a special territory
        counts_list.append({
            'activity': activity,
            'territory': 'Total',
            'count': total
        })

    counterrevolution_mayabeque_count=Incident.objects.filter(activity_type="Contrarevolución",territory="Mayabeque").count()
    counterrevolution_havana_count=Incident.objects.filter(activity_type="Contrarevolución",territory="La Habana").count()
    counterrevolution_artemisa_count=Incident.objects.filter(activity_type="Contrarevolución",territory="Artemisa").count()
    counterrevolution_pinar_count=Incident.objects.filter(activity_type="Contrarevolución",territory="Pinar del Río").count()
    counterrevolution_isle_count=Incident.objects.filter(activity_type="Contrarevolución",territory="Isla de la Juventud").count()   

    criminal_mayabeque_count=Incident.objects.filter(activity_type="Delictiva",territory="Mayabeque").count()
    criminal_havana_count=Incident.objects.filter(activity_type="Delictiva",territory="La Habana").count()
    criminal_artemisa_count=Incident.objects.filter(activity_type="Delictiva",territory="Artemisa").count()
    criminal_pinar_count=Incident.objects.filter(activity_type="Delictiva",territory="Pinar del Río").count()
    criminal_isle_count=Incident.objects.filter(activity_type="Delictiva",territory="Isla de la Juventud").count()     
    print(counterrevolution_mayabeque_count)
    data = {
        'counterrevolution_activities': counterrevolution_activities,
        'criminal_activities': criminal_activities,
        'territories': territories + ['Total'],
        'counts_list': counts_list,
        'counterrevolution_mayabeque_count':counterrevolution_mayabeque_count,
        'counterrevolution_havana_count':counterrevolution_havana_count,
        'counterrevolution_artemisa_count':counterrevolution_artemisa_count,
        'counterrevolution_pinar_count':counterrevolution_pinar_count,
        'counterrevolution_isle_count':counterrevolution_isle_count,
        'criminal_mayabeque_count':criminal_mayabeque_count,
        'criminal_havana_count':criminal_havana_count,
        'criminal_artemisa_count':criminal_artemisa_count,
        'criminal_pinar_count':criminal_pinar_count,
        'criminal_isle_count':criminal_isle_count
    }
    return data



from datetime import datetime, time
from django.utils import timezone

from datetime import datetime, time, timedelta
from django.utils import timezone

from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
import io

@login_required
def generate_report(request):
    incident_date_start = request.GET.get('fecha_incidencia_start', '')
    incident_date_end = request.GET.get('fecha_incidencia_end', '')
    other_incidents = OtherIncident.objects.none()
    incidents = Incident.objects.none()
   
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
        other_incidents=OtherIncident.objects.filter(incident_date__gte=start_datetime, incident_date__lte=end_datetime)
        incidents = Incident.objects.filter(incident_date__gte=start_datetime, incident_date__lte=end_datetime)
    elif start_datetime:
        # Filter incidences for the exact start date only
        next_day = start_datetime + timedelta(days=1)
        other_incidents = OtherIncident.objects.filter(incident_date__gte=start_datetime, incident_date__lt=next_day)
        incidents = Incident.objects.filter(incident_date__gte=start_datetime, incident_date__lt=next_day)
    elif end_datetime:
        other_incidents = OtherIncident.objects.filter(incident_date__lte=end_datetime)
        incidents = Incident.objects.filter(incident_date__lte=end_datetime) 

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

    # Use all regions from modelos.regiones
    territories = [region[0] for region in REGIONS]

    # Prepare counts dictionary: {(actividad, territorio): count}
    counts = {}
    for activity in counterrevolution_activities + criminal_activities:
        counts[activity] = {}
        for territory in territories:
            count = incidents.filter(activities=activity, territory=territory).count()
            counts[activity][territory] = count

    # Flatten counts to a list of dicts for template
    counts_list = []
    for activity in counterrevolution_activities + criminal_activities:
        total = sum(counts[activity].values())
        for territory in territories:
            counts_list.append({
                'activity': activity,
                'territory': territory,
                'count': counts[activity][territory]
            })
        # Add total as a special territory
        counts_list.append({
            'activity': activity,
            'territory': 'Total',
            'count': total
        })
    
    counterrevolution_mayabeque_count=incidents.filter(activity_type="Contrarevolución",territory="Mayabeque").count()
    counterrevolution_havana_count=incidents.filter(activity_type="Contrarevolución",territory="La Habana").count()
    counterrevolution_artemisa_count=incidents.filter(activity_type="Contrarevolución",territory="Artemisa").count()
    counterrevolution_pinar_count=incidents.filter(activity_type="Contrarevolución",territory="Pinar del Río").count()
    counterrevolution_isle_count=incidents.filter(activity_type="Contrarevolución",territory="Isla de la Juventud").count()   
    counterrevolution_total=incidents.filter(activity_type="Contrarevolución").count()   
    print(counterrevolution_total)
    criminal_mayabeque_count=incidents.filter(activity_type="Delictiva",territory="Mayabeque").count()
    criminal_havana_count=incidents.filter(activity_type="Delictiva",territory="La Habana").count()
    criminal_artemisa_count=incidents.filter(activity_type="Delictiva",territory="Artemisa").count()
    criminal_pinar_count=incidents.filter(activity_type="Delictiva",territory="Pinar del río").count()
    criminal_isle_count=incidents.filter(activity_type="Delictiva",territory="Isla de la Juventud").count()     
    criminal_total=incidents.filter(activity_type="Delictiva").count()
    print(criminal_total)
    data = {
        'counterrevolution_activities': counterrevolution_activities,
        'criminal_activities': criminal_activities,
        'territories': territories + ['Total'],
        'counts_list': counts_list,
        'counterrevolution_mayabeque_count':counterrevolution_mayabeque_count,
        'counterrevolution_havana_count':counterrevolution_havana_count,
        'counterrevolution_artemisa_count':counterrevolution_artemisa_count,
        'counterrevolution_pinar_count':counterrevolution_pinar_count,
        'counterrevolution_isle_count':counterrevolution_isle_count,
        'criminal_mayabeque_count':criminal_mayabeque_count,
        'criminal_havana_count':criminal_havana_count,
        'criminal_artemisa_count':criminal_artemisa_count,
        'criminal_pinar_count':criminal_pinar_count,
        'criminal_isle_count':criminal_isle_count,
        'counterrevolution_total':counterrevolution_total,
        'criminal_total':criminal_total,
        
    }

    other_incidents = OtherIncident.objects.none()
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
        other_incidents=OtherIncident.objects.filter(incident_date__gte=start_datetime, incident_date__lte=end_datetime)
        incidents = Incident.objects.filter(incident_date__gte=start_datetime, incident_date__lte=end_datetime)
    elif start_datetime:
        # Filter incidences for the exact start date only
        next_day = start_datetime + timedelta(days=1)
        other_incidents = OtherIncident.objects.filter(incident_date__gte=start_datetime, incident_date__lt=next_day)
        incidents = Incident.objects.filter(incident_date__gte=start_datetime, incident_date__lt=next_day)
    elif end_datetime:
        other_incidents = OtherIncident.objects.filter(incident_date__lte=end_datetime)
        incidents = Incident.objects.filter(incident_date__lte=end_datetime)

    data={
        'incidents':incidents,
        'other_incidents':other_incidents,
        'counterrevolution_activities': counterrevolution_activities,
        'criminal_activities': criminal_activities,
        'territories': territories + ['Total'],
        'counts_list': counts_list,
        'counterrevolution_mayabeque_count':counterrevolution_mayabeque_count,
        'counterrevolution_havana_count':counterrevolution_havana_count,
        'counterrevolution_artemisa_count':counterrevolution_artemisa_count,
        'counterrevolution_pinar_count':counterrevolution_pinar_count,
        'counterrevolution_isle_count':counterrevolution_isle_count,
        'criminal_mayabeque_count':criminal_mayabeque_count,
        'criminal_havana_count':criminal_havana_count,
        'criminal_artemisa_count':criminal_artemisa_count,
        'criminal_pinar_count':criminal_pinar_count,
        'criminal_isle_count':criminal_isle_count,
        'counterrevolution_total':counterrevolution_total,
        'criminal_total':criminal_total,   
    }

    
    html_string = render_to_string('App/report.html', data)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="parte.pdf"'
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html_string), dest=result)
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)
    response.write(result.getvalue())
    return response

    return render(request,"App/report.html",data)

@login_required
def add_other_incidence(request):
    if request.method == 'POST':
        form = OtherIncidentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    return render(request,"App/dashboard.html")