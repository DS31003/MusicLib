from django.contrib import admin
from .models import Zanr, Izvodjac, Album, Prodaja, Recenzija


@admin.register(Zanr)
class ZanrAdmin(admin.ModelAdmin):
    list_display=['naziv']
    search_fields=['naziv']

@admin.register(Izvodjac)
class IzvodjacAdmin(admin.ModelAdmin):
    list_display=['ime','drzava','godina_osnivanja']
    list_filter=['drzava']
    search_fields=['ime']

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display=['naslov', 'izvodjac', 'zanr', 'godina']
    list_filter=['zanr', 'godina']
    search_fields=['naslov', 'izvodjac__ime']

@admin.register(Prodaja)
class ProdajaAdmin(admin.ModelAdmin):
    list_display=['korisnik', 'album', 'cijena', 'datum']
    list_filter=['datum']
    search_fields=['korisnik__username', 'album__naslov']

@admin.register(Recenzija)
class RecenzijaAdmin(admin.ModelAdmin):
    list_display = ['korisnik', 'album', 'ocjena', 'datum']
    list_filter = ['ocjena']
    search_fields = ['korisnik__username', 'album__naslov']