from django import forms
from .models import Incident, UserAccount,OtherIncident
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UserChangeForm

class IncidentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            classes = existing_classes.split()
            if 'form-control' not in classes:
                classes.append('form-control')
            field.widget.attrs['class'] = ' '.join(classes)

   # fecha_registro = forms.DateTimeField(widget=forms.DateTimeInput(attrs={ 'type':'datetime-local' ,'class': 'form-control'}))
    class Meta:
        model = Incident
        fields = '__all__'
        widgets={
            'incident_date':forms.DateTimeInput(attrs={ 'type':'date' ,'class': 'form-control '}), 
            'incident_time':forms.DateTimeInput(attrs={ 'type':'time' ,'class': 'form-control'}),
            'created_at':forms.DateTimeInput(attrs={ 'type':'datetime-local' ,'class': 'form-control'}),
            'involved_parties': forms.Textarea(attrs={'type': 'text','class':'form-control'}),
            'additional_details': forms.Textarea(attrs={'type': 'text','class':'form-control'}),
        }


class IncidentEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            classes = existing_classes.split()
            if 'form-control' not in classes:
                classes.append('form-control')
            field.widget.attrs['class'] = ' '.join(classes)

   # fecha_registro = forms.DateTimeField(widget=forms.DateTimeInput(attrs={ 'type':'datetime-local' ,'class': 'form-control'}))
    class Meta:
        model = Incident
        fields = '__all__'
        widgets={
            'incident_date':forms.DateInput(attrs={ 'type':'date' ,'class': 'form-control '}),
            'created_at':forms.DateTimeInput(attrs={ 'type':'datetime-local' ,'class': 'form-control'}),
            'involved_parties': forms.Textarea(attrs={'type': 'text','class':'form-control'}),
            'additional_details': forms.Textarea(attrs={'type': 'text','class':'form-control'}),
        }

class CustomUserCreationForm(DjangoUserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            classes = existing_classes.split()
            if 'form-control' not in classes:
                classes.append('form-control')
            field.widget.attrs['class'] = ' '.join(classes)

    class Meta:
        model = UserAccount
        fields = ['username', 'role', 'identity_number', 'region', 'email', 'first_name', 'last_name']

class UserUpdateForm(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            classes = existing_classes.split()
            if 'form-control' not in classes:
                classes.append('form-control')
            field.widget.attrs['class'] = ' '.join(classes)

    class Meta:
        model = UserAccount
        fields = ['username', 'role', 'identity_number', 'unit_number','military_grade' ,'region', 'email', 'first_name', 'last_name']

class UserPasswordUpdateForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            classes = existing_classes.split()
            if 'form-control' not in classes:
                classes.append('form-control')
            field.widget.attrs['class'] = ' '.join(classes)

    password1 = forms.CharField(
        label="Nueva Contraseña",
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )
    password2 = forms.CharField(
        label="Confirmar Nueva Contraseña",
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

class OtherIncidentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            classes = existing_classes.split()
            if 'form-control' not in classes:
                classes.append('form-control')
            field.widget.attrs['class'] = ' '.join(classes)



    class Meta:
        model = OtherIncident
        fields = '__all__'

        widgets={
            'incident_date':forms.DateTimeInput(attrs={ 'type':'date' ,'class': 'form-control '}),
            'incident_time':forms.DateTimeInput(attrs={ 'type':'time' ,'class': 'form-control'}), 
            }