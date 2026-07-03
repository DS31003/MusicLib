from django import forms
from .models import Album, Recenzija, Zanr, Izvodjac

class AlbumForm(forms.ModelForm):

    class Meta:
        model=Album

        fields=['naslov', 'izvodjac', 'zanr', 'godina', 
                'broj_pjesama', 'trajanje_min', 'cijena', 'omot', 'opis']

        labels={
            'naslov': 'Naslov albuma',
            'izvodjac': 'Izvođač',
            'zanr': 'Žanr',
            'godina': 'Godina izlaska',
            'broj_pjesama': 'Broj pjesama',
            'cijena': 'Cijena',
            'trajanje_min': 'Trajanje (minute)',
            'omot': 'Omot albuma',
            'opis': 'Opis', 
        }

def clean_godina(self):
    godina=self.cleaned_data['godina']
    if godina < 1900 or godina > 2030:
        raise forms.ValidationError("Unesi ispravnu godinu")
    return godina

class RecenzijaForm(forms.ModelForm):
    class Meta:
        model=Recenzija
        fields=['ocjena', 'tekst']
        labels={
            'ocjena': 'Ocjena (1-5)',
            'tekst': 'Recenzija',
        }

class ZanrForm(forms.ModelForm):
    class Meta:
        model=Zanr
        fields=['naziv']
        labels={'naziv': 'Naziv žanra'}


class IzvodjacForm(forms.ModelForm):
    class Meta:
        model = Izvodjac
        fields = ['ime', 'drzava', 'godina_osnivanja']
        labels = {
            'ime': 'Ime izvođača',
            'drzava': 'Država',
            'godina_osnivanja': 'Godina osnivanja',
        }