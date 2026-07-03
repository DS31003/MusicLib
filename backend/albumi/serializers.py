from rest_framework import serializers
from .models import Album, Izvodjac, Zanr, Prodaja, Recenzija


class ZanrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zanr
        fields = ['id', 'naziv']


class IzvodjacSerializer(serializers.ModelSerializer):
    class Meta:
        model = Izvodjac
        fields = ['id', 'ime', 'drzava', 'godina_osnivanja']


class AlbumSerializer(serializers.ModelSerializer):
    izvodjac = IzvodjacSerializer(read_only=True)
    zanr = ZanrSerializer(read_only=True)
    prosjecna_ocjena = serializers.FloatField(read_only=True, required=False)
    ai_score = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id', 'naslov', 'izvodjac', 'zanr', 'godina', 'broj_pjesama',
            'trajanje_min', 'omot', 'opis', 'cijena',
            'prosjecna_ocjena', 'ai_score',
        ]

    def get_ai_score(self, album):
        from .views import izracunaj_ai_score
        return izracunaj_ai_score(album)


class RecenzijaSerializer(serializers.ModelSerializer):
    korisnik = serializers.ReadOnlyField(source='korisnik.username')

    class Meta:
        model = Recenzija
        fields = ['id', 'korisnik', 'album', 'tekst', 'ocjena', 'datum']
        read_only_fields = ['korisnik', 'album', 'datum']


class ProdajaSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(read_only=True)

    class Meta:
        model = Prodaja
        fields = ['id', 'album', 'datum', 'cijena']
