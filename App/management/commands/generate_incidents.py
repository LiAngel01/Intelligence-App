import random
from datetime import datetime, timedelta, time, date
from django.core.management.base import BaseCommand
from App.models import Incident, REGIONS, INFORMANTS, ACTIVITY_TYPES, MUNICIPALITIES_HAVANA, MUNICIPALITIES_PINAR_DEL_RIO, MUNICIPALITIES_MAYABEQUE, MUNICIPALITIES_ARTEMISA, MUNICIPALITIES_ISLE_OF_YOUTH

class Command(BaseCommand):
    help = 'Generates random valid incidencias and inserts them into the database'

    def handle(self, *args, **kwargs):
        # Map region to municipios
        region_to_municipalities = {
            "Mayabeque": MUNICIPALITIES_MAYABEQUE,
            "La Habana": MUNICIPALITIES_HAVANA,
            "Artemisa": MUNICIPALITIES_ARTEMISA,
            "Pinar del río": MUNICIPALITIES_PINAR_DEL_RIO,
            "Isla de la Juventud": MUNICIPALITIES_ISLE_OF_YOUTH,
        }

        for _ in range(100):
            # Random date in the last year
            start_date = date.today() - timedelta(days=365)
            random_date = start_date + timedelta(days=random.randint(0, 365))

            # Random time
            random_time = time(
                hour=random.randint(0, 23),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )

            # Random choices
            informant = random.choice(INFORMANTS)[0]
            activity_type = random.choice(ACTIVITY_TYPES)[0]
            territory = random.choice(REGIONS)[0]

            # Random municipio based on territorio
            municipality_choices = region_to_municipalities.get(territory, [])
            municipality = random.choice(municipality_choices)[0] if municipality_choices else None

            # Random implicado and ampliacion text
            involved_parties = f"Implicado ejemplo {_+1}"
            additional_details = f"Ampliación de la incidencia ejemplo {_+1}"

            # actividades field - can be set to tipo_actividad or a placeholder
            activities = activity_type

            incident = Incident(
                incident_date=random_date,
                incident_time=random_time,
                informant=informant,
                activity_type=activity_type,
                territory=territory,
                municipality=municipality,
                involved_parties=involved_parties,
                additional_details=additional_details,
                activities=activities
            )
            incident.save()

        self.stdout.write(self.style.SUCCESS('Successfully added 100 random incidencias'))
