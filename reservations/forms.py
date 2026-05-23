from django import forms
from .models import Reservation


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'client_name', 'client_email', 'client_phone',
            'client_address', 'client_license',
            'start_date', 'end_date',
            'pickup_location', 'return_location', 'notes'
        ]
        widgets = {
            'client_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-yellow-500 focus:outline-none',
                'placeholder': 'Votre nom complet'
            }),
            'client_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-yellow-500 focus:outline-none',
                'placeholder': 'votre@email.com'
            }),
            'client_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-yellow-500 focus:outline-none',
                'placeholder': '+212 6 00 00 00 00'
            }),
            'client_address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-yellow-500 focus:outline-none',
                'rows': 2,
                'placeholder': 'Votre adresse complète'
            }),
            'client_license': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-yellow-500 focus:outline-none',
                'placeholder': 'Numéro de permis de conduire'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-yellow-500 focus:outline-none',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-yellow-500 focus:outline-none',
                'type': 'date'
            }),
            'pickup_location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-yellow-500 focus:outline-none',
            }),
            'return_location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-yellow-500 focus:outline-none',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-yellow-500 focus:outline-none',
                'rows': 3,
                'placeholder': 'Informations supplémentaires...'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError("La date de fin doit être après la date de début.")
        return cleaned_data
