from django.db import models
from django.contrib.auth.models import User


class Zanr(models.Model):
    naziv=models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name="Zanr"
        verbose_name_plural="Zanrovi"
        ordering=['naziv']

    def __str__(self):
        return self.naziv

  
class Izvodjac(models.Model):
    ime=models.CharField(max_length=100)
    drzava=models.CharField(max_length=50, blank=True)
    godina_osnivanja=models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name="Izvodjac"
        verbose_name_plural="Izvodjaci"
        ordering=['ime']
    
    def __str__(self):
        return self.ime


class Album(models.Model):
    naslov=models.CharField(max_length=200)
    izvodjac=models.ForeignKey(
        Izvodjac,
        on_delete=models.CASCADE,
        related_name='albumi'
    )

    zanr=models.ForeignKey(
        Zanr,
        on_delete=models.CASCADE,
        related_name='albumi'
    )

    godina=models.IntegerField()
    broj_pjesama=models.IntegerField()
    trajanje_min=models.IntegerField(help_text="Ukupno trajanje u minutama")
    omot=models.ImageField(upload_to='omoti/',blank=True, null=True)
    opis=models.TextField(blank=True)
    datum_dodavanja=models.DateTimeField(auto_now_add=True)
    cijena=models.DecimalField(max_digits=6, decimal_places=2, default=9.99 )

    class Meta:
        verbose_name="Album"
        verbose_name_plural="Albumi"
        ordering=['-godina', 'naslov']
    
    def __str__(self):
        return f"{self.izvodjac}-{self.naslov}-({self.godina})"



class Prodaja(models.Model):
    korisnik=models.ForeignKey(User, on_delete=models.CASCADE)
    album=models.ForeignKey(Album, on_delete=models.CASCADE, related_name='prodaje')
    datum=models.DateTimeField(auto_now_add=True)
    cijena=models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        verbose_name='Prodaja'
        verbose_name_plural='Prodaje'
    
    def __str__(self):
        return f"{self.korisnik} - {self.album} - {self.datum}"
    

class Recenzija(models.Model):
    korisnik=models.ForeignKey(User, on_delete=models.CASCADE)
    album=models.ForeignKey(Album, on_delete=models.CASCADE, related_name='recenzije')
    tekst=models.TextField()
    ocjena=models.IntegerField(choices=[(i, i) for i in range(1,6)])
    datum=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name='Recenzija'
        verbose_name_plural='Recenzije'
        unique_together=['korisnik', 'album']

    def __str__(self):
        return f"{self.korisnik}-{self.album}-{self.ocjena}"