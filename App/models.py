from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

REGIONS=(
    ("Mayabeque","Mayabeque"),
    ("La Habana","La Habana"),
    ("Artemisa","Artemisa"),
    ("Pinar del río","Pinar del río"),
    ("Isla de la Juventud","Isla de la Juventud"),
    
)

MUNICIPALITIES_HAVANA = (
    ("Playa", "Playa"),
    ("Plaza de la Revolución", "Plaza de la Revolución"),
    ("Centro Habana", "Centro Habana"),
    ("Habana Vieja", "Habana Vieja"),
    ("Guanabacoa", "Guanabacoa"),
    ("Regla", "Regla"),
    ("San Miguel del Padrón", "San Miguel del Padrón"),
    ("Diez de Octubre", "Diez de Octubre"),
    ("Cerro", "Cerro"),
    ("Marianao", "Marianao"),
    ("La Lisa", "La Lisa"),
    ("Boyeros", "Boyeros"),
    ("Arroyo Naranjo", "Arroyo Naranjo"),
    ("Cotorro", "Cotorro"),
    ("Habana del Este", "Habana del Este")
)
MUNICIPALITIES_PINAR_DEL_RIO = (
    ("Pinar del Río", "Pinar del Río"),
    ("Consolación del Sur", "Consolación del Sur"),
    ("Viñales", "Viñales"),
    ("San Luis", "San Luis"),
    ("Minas de Matahambre", "Minas de Matahambre"),
    ("Guane", "Guane"),
    ("La Palma", "La Palma"),
    ("Los Palacios", "Los Palacios"),
    ("San Juan y Martínez", "San Juan y Martínez"),
    ("Mantua", "Mantua"),
    ("Sandino", "Sandino")
)
MUNICIPALITIES_MAYABEQUE = (
    ("San José de las Lajas", "San José de las Lajas"),
    ("Batabanó", "Batabanó"),
    ("Güines", "Güines"),
    ("San Nicolás de Bari", "San Nicolás de Bari"),
    ("Santa Cruz del Norte", "Santa Cruz del Norte"),
    ("Madruga", "Madruga"),
    ("Nueva Paz", "Nueva Paz"),
    ("Quivicán", "Quivicán"),
    ("Bejucal", "Bejucal"),
    ("Jaruco", "Jaruco"),
    ("Melena del Sur", "Melena del Sur")
)
MUNICIPALITIES_ARTEMISA = (
    ("Artemisa", "Artemisa"),
    ("Guanajay", "Guanajay"),
    ("Mariel", "Mariel"),
    ("Bauta", "Bauta"),
    ("San Antonio de los Baños", "San Antonio de los Baños"),
    ("Caimito", "Caimito"),
    ("Bahía Honda", "Bahía Honda"),
    ("Alquízar", "Alquízar"),
    ("Güira de Melena", "Güira de Melena"),
    ("San Cristóbal", "San Cristóbal"),
    ("Candelaria", "Candelaria")
)
MUNICIPALITIES_ISLE_OF_YOUTH = (
    ("Nueva Gerona", "Nueva Gerona"),  # Capital y único municipio
    # Nota: Aunque es un municipio especial, se incluyen localidades importantes:
    ("Santa Fe", "Santa Fe"),
    ("La Demajagua", "La Demajagua"),
    ("Columbia", "Columbia")
)
MILITARY_GRADES=(
    ('Soldado','Soldado'),
    ('Cabo','Cabo'),
    ('S3','S3'),
    ('S2','S2'),
    ('S1','S1'),
    ('Sargento P','Sargento P'),
    ('SubOficial','SubOficial'),
    ('SubTeniente','SubTeniente'),
    ('Teniente','Teniente'),
    ('Primer Teniente','Primer Teniente'),
    ('Capitán','Capitán'),
    ('Mayor','Mayor'),
    ('Teniente Coronel','Teniente Coronel'),
    ('Coronel','Coronel'),
    )


class Usuario(AbstractUser):
    ADMIN = 'ADMIN'
    ARMY = 'EJÉRCITO'
    REGION = 'REGIÓN'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrador'),
        (REGION, 'Región'),
        (ARMY, 'Ejército'),
    ]

    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        blank=True,
        null=True,
        default=REGION,
        help_text='Rol del usuario',
        verbose_name='rol',
    )

    identity_number = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(regex=r'^\d{6}$', message='El número de identidad debe tener exactamente 11 dígitos')], 
        help_text='Número de identidad de 6 dígitos',
        verbose_name='numero identidad',
    )
    region = models.CharField(max_length=100, choices=REGIONS,null=True,blank=False)
    military_grade=models.CharField(choices=MILITARY_GRADES,null=True,blank=False,max_length=50, verbose_name='grado militar')
    unit_number = models.CharField(null=True,verbose_name="unidad militar",max_length=4, validators=[
            RegexValidator(
                regex=r'^\d{4}$',
                message='El número debe tener exactamente 4 dígitos.'
            )
        ])
    last_logout = models.DateTimeField(null=True, blank=True, help_text='Última vez que el usuario cerró sesión')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# Keep the swappable Django user model label stable for existing migrations.
UserAccount = Usuario

INFORMANTS = (
    ("MININT","MININT"),
    ("Guardafronteras","Guardafronteras"),
    ("Cuerpo Guardabosques","Cuerpo Guardabosques"),
    ("Componente no armado","Componente no armado"),
    ("Otros","Otros"),
    
)

ACTIVITY_TYPES= (
    ("Contrarevolución" ,"Contrarevolución"),
    ("Delictiva","Delictiva"),
    
    
)


COUNTERREVOLUTION_ACTIVITIES=(
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
    
    
    )

CRIMINAL_ACTIVITIES=(
    ("Hechos relacionados con drogas","Hechos relacionados con drogas"),
    ("Hechos con armas de fuego","Hechos con armas de fuego"),
    ("Incendios","Incendios"),
    ("Hechos relacionados con extrajeros","Hechos relacionados con extrajeros"),
    ("Hechos contra la vida","Hechos contra la vida"),
    ("Hurtos, robos con fuerza y violencia","Hurtos, robos con fuerza y violencia"),
    ("Hechos contra el ganado mayor","Hechos contra el ganado mayor"),
    ("Hechos contra miembros del MININT","Hechos contra miembros del MININT"),
)

class Incident(models.Model):
    incident_date=models.DateField(verbose_name="Fecha Incidencia")
    incident_time=models.TimeField(verbose_name="Hora Incidencia",null=True)
    created_at=models.DateTimeField(verbose_name="Fecha Registro",auto_now_add=True)
    informant=models.CharField(max_length=100,choices=INFORMANTS, verbose_name="Quien informa",null=False,blank=False)
    activity_type=models.CharField(max_length=100, choices=ACTIVITY_TYPES,null=False,blank=False, verbose_name='tipo actividad')
    territory=models.CharField(max_length=100, choices=REGIONS,null=False,blank=False, verbose_name='territorio')
    municipality=models.CharField(max_length=100, null=True,blank=False, verbose_name='municipio')
    involved_parties=models.TextField(max_length=600,null=True,blank=True, verbose_name="Implicado(s)")
    additional_details=models.TextField(max_length=5000,null=True,blank=True, verbose_name='ampliacion')
    activities=models.CharField(max_length=100,default="N/A",blank=False,verbose_name="Actividad")
    image = models.ImageField(upload_to='incidencias/', null=True, blank=True, verbose_name="Imagen")
    
class OtherIncident(models.Model):
    incident_date=models.DateField(verbose_name="Fecha Incidencia")
    incident_time=models.TimeField(verbose_name="Hora Incidencia",null=True)
    created_at=models.DateTimeField(verbose_name="Fecha Registro",auto_now_add=True)
    description=models.TextField(max_length=5000,null=True,blank=True, verbose_name='descripcion')
