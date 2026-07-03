
from django.urls import path
from . import views
from django.urls import path, include

app_name = 'albumi'

urlpatterns = [
    path('', views.popis_albuma, name='popis'),
    path('album/<int:pk>/', views.detalj_albuma, name='detalj'),
    path('dodaj/', views.dodaj_album, name='dodaj'),
    path('album/<int:pk>/uredi/', views.uredi_album, name='uredi'),
    path('album/<int:pk>/obrisi/', views.obrisi_album, name='obrisi'),
    path('kupi/<int:pk>/', views.kupi_album, name='kupi'),
    path('kolekcija/', views.kolekcija, name='kolekcija'),
    path('statistika/', views.statistika, name='statistika'),
    path('album/<int:pk>/recenzija/', views.dodaj_recenziju, name='dodaj_recenziju'),
    path('upravljanje/', views.upravljanje, name='upravljanje'),
    path('izvodjac/<int:pk>/', views.detalj_izvodjaca, name='detalj_izvodjaca'),
    path('izvodjac/<int:pk>/uredi/', views.uredi_izvodjaca, name='uredi_izvodjaca'),
    path('recenzije/korisnik/', views.korisnik_recenzije, name='recenzije'),
    path('albumi_s_prosjekom/', views.popis_albuma_s_prosjekom_ocjena, name='popis_albuma_prosjeci'),
    path('izvodjaci_s_brojem_albuma/', views.popis_izvodjaca_s_brojem_albuma, name='popis_izvodjaca_broj_albuma'),
    path('korisnik_albumi_recenzije/', views.korisnik_albumi_recenzije, name='popis_korisnikovih_albuma_recenzija'),
    path('zanr/<int:pk>/', views.detalj_zanra, name='detalj_zanra'),
    path('top_korisnici/', views.top_korisnici, name='korisnici'),
    path('top_korisnici_detalj/<int:pk>', views.top_korisnik_detalj, name='korisnici_detalj'),
    path('izvodjac/<int:pk>/obrisi/', views.obrisi_izvodjaca, name='obrisi_izvodjaca'),
    path('najprodavaniji_albumi/', views.najprodavaniji_albumi, name='najprodavaniji_albumi'),
    path('pretraga/', views.forma_pretrage, name='forma_pretrage'),
    path('rezultati/', views.rezultati_pretrage, name='rezultati_pretrage'),    
    path('api/', include('albumi.api_urls')),

]