from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from .models import Album, Izvodjac, Zanr, Prodaja, Recenzija
from .forms import AlbumForm, RecenzijaForm, ZanrForm, IzvodjacForm
import torch
import torch.nn as nn
import pandas as pd
from django.db.models import Count, Avg, Sum

class AlbumNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(3, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)


def ucitaj_model():
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    model = AlbumNet().to(device)
    try:
        model.load_state_dict(torch.load('album_model.pt', map_location=device))
        model.eval()
        return model, device
    except:
        return None, device


def izracunaj_ai_score(album):
    model, device = ucitaj_model()
    if model is None:
        return None
    
    X = torch.tensor([[
        album.godina,
        album.broj_pjesama,
        album.trajanje_min
    ]], dtype=torch.float32).to(device)
    
    with torch.no_grad():
        score = model(X).item()
    
    return round(score * 100, 1)


def popis_albuma(request):
    albumi = Album.objects.select_related('izvodjac', 'zanr').annotate(
        prosjecna_ocjena=Avg('recenzije__ocjena')
    ).order_by('-godina','naslov')
    
    naslov = request.GET.get('naslov', '').strip()
    izvodjac_id = request.GET.get('izvodjac', '')
    zanr_id = request.GET.get('zanr', '')
    godina = request.GET.get('godina', '')  
    sort = request.GET.get('sort', '')
    
    if naslov:
        albumi = albumi.filter(naslov__icontains=naslov)
    if izvodjac_id:
        albumi = albumi.filter(izvodjac_id=izvodjac_id)
    if zanr_id:
        albumi = albumi.filter(zanr_id=zanr_id)
    if godina:
        albumi = albumi.filter(godina=godina)

    if sort == 'abecedno':
        albumi = albumi.order_by('naslov')
    elif sort == 'cijena_asc':
        albumi = albumi.order_by('cijena')
    elif sort == 'cijena_desc':
        albumi = albumi.order_by('-cijena')
    elif sort == 'najnovije_dodano':
        albumi = albumi.order_by('-datum_dodavanja')
    elif sort == 'najprodavanije':
        albumi = albumi.annotate(broj_prodaja=Count('prodaje')).order_by('-broj_prodaja')
    elif sort == 'najocjenjeniji':
        albumi = albumi.annotate(prosjecna=Avg('recenzije__ocjena')).order_by('-prosjecna')
    elif sort == 'ai_score':
        albumi = list(albumi)
        albumi.sort(key=lambda x: izracunaj_ai_score(x) or 0, reverse=True)

    return render(request, 'albumi/popis.html', {
        'albumi': albumi,
        'izvodjaci': Izvodjac.objects.all(),
        'zanrovi': Zanr.objects.all(),
        'f_naslov': naslov,
        'f_izvodjac': izvodjac_id,
        'f_zanr': zanr_id,
        'f_godina': godina,
        'sort': sort,
    })

def detalj_albuma(request, pk):
    album = get_object_or_404(Album, pk=pk)
    recenzije = album.recenzije.all().select_related('korisnik')
    prosjecna_ocjena = recenzije.aggregate(avg=Avg('ocjena'))['avg'] or 0
    slicni_albumi = Album.objects.filter(zanr=album.zanr).exclude(pk=album.pk)[:5]
    
    ai_score = izracunaj_ai_score(album)

    vec_kupio = False
    vec_recenzirao = False
    if request.user.is_authenticated:
        vec_kupio = Prodaja.objects.filter(
            korisnik=request.user, 
            album=album
        ).exists()

        vec_recenzirao = Recenzija.objects.filter(
            korisnik=request.user,
            album=album
        ).exists()

    return render(request, 'albumi/detalj.html', {
        'album': album,
        'recenzije': recenzije,
        'prosjecna_ocjena': round(prosjecna_ocjena, 1),
        'slicni_albumi': slicni_albumi,
        'vec_kupio': vec_kupio,
        'vec_recenzirao': vec_recenzirao,
        'ai_score': ai_score,
    })


def je_admin(user):
    return user.is_authenticated and user.is_staff


def registracija(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            korisnik=form.save()
            login(request, korisnik)
            messages.success(request, f'Dobrodošli, {korisnik.username}!')
            return redirect('albumi:popis')
    else:
        form=UserCreationForm()
    return render(request, 'registration/registracija.html', {'form': form})


@login_required
@user_passes_test(je_admin)
def dodaj_album(request):
    if request.method=='POST':
        form=AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            album=form.save()
            messages.success(request, f'Album "{album.naslov}" dodan!')
            return redirect('albumi:detalj', pk=album.pk)
    else:
        form=AlbumForm()
    return render(request, 'albumi/forma_album.html',
                  {'form': form, 'naslov_stranice': 'Novi album'})


@login_required
@user_passes_test(je_admin)
def uredi_album(request, pk):
    album=get_object_or_404(Album, pk=pk)
    if request.method=='POST':
        form=AlbumForm(request.POST, request.FILES, instance=album)
        if form.is_valid():
            form.save()
            messages.success(request, f'Album "{album.naslov}" ažuriran!')
            return redirect('albumi:detalj', pk=album.pk)
    else:
        form=AlbumForm(instance=album)
    return render(request, 'albumi/forma_album.html',
                  {'form': form, 'naslov_stranice': f'Uredi: {album.naslov}'})


@login_required
@user_passes_test(je_admin)
def obrisi_album(request, pk):
    album=get_object_or_404(Album, pk=pk)
    if request.method=='POST':
        ime=album.naslov
        album.delete()
        messages.success(request, f'Album "{ime}" obrisan.')
        return redirect('albumi:popis')
    return render(request, 'albumi/potvrda_brisanja.html', {'album': album})



@login_required
def kupi_album(request, pk):
    album=get_object_or_404(Album, pk=pk)

    vec_kupljen=Prodaja.objects.filter(
        korisnik=request.user, 
        album=album
    ).exists()

    if vec_kupljen:
        messages.error(request, f'{album.naslov} vec postoji u tvojoj kolekciji!')
        return redirect('albumi:detalj', pk=pk)

    if request.method=='POST':
        Prodaja.objects.create(
            korisnik=request.user,
            album=album,
            cijena=album.cijena
        )
        messages.success(request, f'Kupio si {album.naslov}!')
        return redirect('albumi:kolekcija')
    
    return render(request, 'albumi/potvrda_kupnje.html', {'album' : album})


@login_required
def kolekcija(request):
    kupljeni_albumi=Prodaja.objects.filter(
        korisnik=request.user
    ).select_related('album', 'album__izvodjac', 'album__zanr')

    return render(request, 'albumi/kolekcija.html', {'kupljeni_albumi' : kupljeni_albumi})


def je_zaposlenik(user):
    return user.is_authenticated and user.groups.filter(name='Zaposlenici').exists()


def je_zaposlenik_ili_admin(user):
    return je_zaposlenik(user) or user.is_staff


@login_required
@user_passes_test(je_zaposlenik_ili_admin)
@login_required
@user_passes_test(je_zaposlenik_ili_admin)
def statistika(request):
    najprodavaniji_albumi = Album.objects.annotate(
        broj_prodaja=Count('prodaje')
    ).order_by('-broj_prodaja')[:5]

    najpopularniji_zanrovi = Zanr.objects.annotate(
        broj_prodaja=Count('albumi__prodaje') 
    ).order_by('-broj_prodaja')[:5]

    najpopularniji_izvodjaci = Izvodjac.objects.annotate(
        broj_prodaja=Count('albumi__prodaje')
    ).order_by('-broj_prodaja')[:5]

    ukupno_prodano_albuma = Prodaja.objects.count()
    
    top_ai_albumi = list(Album.objects.all())
    top_ai_albumi.sort(key=lambda x: izracunaj_ai_score(x) or 0, reverse=True)
    top_ai_albumi = top_ai_albumi[:5]

    return render(request, 'albumi/statistika.html', 
                  {
                    'najprodavaniji_albumi': najprodavaniji_albumi,
                    'najpopularniji_zanrovi': najpopularniji_zanrovi,
                    'ukupno_prodano_albuma': ukupno_prodano_albuma,
                    'najpopularniji_izvodjaci': najpopularniji_izvodjaci,
                    'top_ai_albumi': top_ai_albumi,
    })


@login_required
def dodaj_recenziju(request, pk):
    album=get_object_or_404(Album, pk=pk)

    if not Prodaja.objects.filter(korisnik=request.user, album=album).exists():
        messages.error(request, 'Možeš recenzirati samo svoje albume!')
        return redirect('albumi:detalj', pk=pk)

    if Recenzija.objects.filter(korisnik=request.user, album=album).exists():
        messages.error(request, 'Recenzija s ovog računa već postoji!')
        return redirect('albumi:detalj', pk=pk)

    if request.method=='POST':
        form=RecenzijaForm(request.POST)
        if form.is_valid():
            recenzija=form.save(commit=False)
            recenzija.korisnik=request.user
            recenzija.album=album
            recenzija.save()
            messages.success(request, 'Recenzija dodana!')
            return redirect('albumi:detalj', pk=pk)
    else:
        form=RecenzijaForm()

    return render(request, 'albumi/recenzija.html', {
        'form': form,
        'album': album
    })


@login_required
@user_passes_test(je_admin)
def upravljanje(request):
    zanr_form = ZanrForm()
    izvodjac_form = IzvodjacForm()

    if request.method == 'POST':
        if 'dodaj_zanr' in request.POST:
            zanr_form = ZanrForm(request.POST)
            if zanr_form.is_valid():
                zanr_form.save()
                messages.success(request, 'Žanr dodan!')
                return redirect('albumi:upravljanje')

        elif 'dodaj_izvodjaca' in request.POST:
            izvodjac_form = IzvodjacForm(request.POST)
            if izvodjac_form.is_valid():
                izvodjac_form.save()
                messages.success(request, 'Izvođač dodan!')
                return redirect('albumi:upravljanje')

    return render(request, 'albumi/upravljanje.html', {
        'zanr_form': zanr_form,
        'izvodjac_form': izvodjac_form,
        'zanrovi': Zanr.objects.all(),
        'izvodjaci': Izvodjac.objects.all(),
    })


def detalj_izvodjaca(request, pk):
    izvodjac = get_object_or_404(Izvodjac, pk=pk)
    albumi = Album.objects.filter(izvodjac=izvodjac).order_by('-godina')
    prosjecna_ocjena = Recenzija.objects.filter(album__izvodjac=izvodjac).aggregate(avg=Avg('ocjena'))['avg'] or 0
    
    return render(request, 'albumi/detalj_izvodjaca.html', {
        'izvodjac': izvodjac,
        'albumi': albumi,
        'prosjecna_ocjena': round(prosjecna_ocjena, 1)
    })


@login_required
@user_passes_test(je_admin)
def uredi_izvodjaca(request, pk):
    izvodjac = get_object_or_404(Izvodjac, pk=pk)
    if request.method == 'POST':
        form = IzvodjacForm(request.POST, instance=izvodjac)
        if form.is_valid():
            form.save()
            messages.success(request, f'{izvodjac.ime} ažuriran!')
            return redirect('albumi:detalj_izvodjaca', pk=izvodjac.pk)
    else:
        form = IzvodjacForm(instance=izvodjac)
    return render(request, 'albumi/forma_izvodjac.html', {
        'form': form,
        'izvodjac': izvodjac
    })

@login_required
@user_passes_test(je_admin)
def obrisi_izvodjaca(request, pk):
    izvodjac=get_object_or_404(Izvodjac, pk=pk)
    if request.method == 'POST':
        ime=izvodjac.ime
        izvodjac.delete()
        messages.success(request, f'Izvodjac "{ime}" obrisan.')
        return redirect('albumi:popis')
    return render(request, 'albumi/brisanje_izvodjaca.html', {'izvodjac':izvodjac})

def je_obican_korisnik(user):
    return not je_zaposlenik_ili_admin(user)

@login_required
@user_passes_test(je_obican_korisnik)
def korisnik_recenzije(request):
    recenzije=Recenzija.objects.filter(korisnik=request.user).select_related('korisnik', 'album', 'album__izvodjac').order_by('-datum')
    return render(request, 'albumi/recenzije_korisnik.html', {'recenzije':recenzije})


def popis_albuma_s_prosjekom_ocjena(request):
    albumi=Album.objects.annotate(
        broj_prodaja=Count('prodaje'),
        prosjecna_ocjena=Avg('recenzije__ocjena')
    ).order_by('-broj_prodaja')
    return render(request, 'albumi/popis_albuma_s_prosjekom_ocjena.html', {'albumi':albumi})


def popis_izvodjaca_s_brojem_albuma(request):
    izvodjaci=Izvodjac.objects.annotate(broj_albuma=Count('albumi')).order_by('-broj_albuma')
    return render(request, 'albumi/popis_izvodjaca_s_brojem_albuma.html', {'izvodjaci': izvodjaci})


@login_required
def korisnik_albumi_recenzije(request):
    prodaje=Prodaja.objects.filter(korisnik=request.user).select_related('album')
    recenzije=Recenzija.objects.filter(korisnik=request.user).select_related('album')
    return render(request, 'albumi/korisnik_albumi_recenzije.html', {'prodaje': prodaje, 'recenzije':recenzije})


def detalj_zanra(request, pk):
    zanr=get_object_or_404(Zanr, pk=pk)
    albumi=Album.objects.filter(zanr=zanr).annotate(prosjecna_ocjena=Avg('recenzije__ocjena'))  
    statistika=albumi.aggregate(
        prosjecna_cijena=Avg('cijena'),
        prosjecna_ocjena_zanra=Avg('recenzije__ocjena')
    )

    return render(request, 'albumi/detalj_zanra.html', {
        'zanr':zanr,
        'albumi':albumi,
        'prosjecna_cijena': round(statistika['prosjecna_cijena'] or 0, 2),
        'prosjecna_ocjena': round(statistika['prosjecna_ocjena_zanra'] or 0, 1)
        })


def top_korisnici(request):
    korisnici=User.objects.annotate(broj_kupljenih=Count('prodaja')).order_by('-broj_kupljenih')[:3]
    return render(request, 'albumi/korisnici.html', {'korisnici': korisnici})

def top_korisnik_detalj(request, pk):
    korisnik=get_object_or_404(User, pk=pk)
    prodaje=Prodaja.objects.filter(korisnik=korisnik).select_related('album')
    return render(request, 'albumi/top_korisnik_detalj.html', {'korisnik':korisnik, 'prodaje':prodaje})

def najprodavaniji_albumi(request):
    albumi=Album.objects.annotate(broj_kupovina=Count('prodaje')).order_by('-broj_kupovina')[:3]
    return render(request, 'albumi/top_albumi.html', {'albumi':albumi})

def najprodavaniji_albumi_detalj(request, pk):
    album=get_object_or_404(User, pk=pk)
    return render(request, 'albumi/detalj.html', {'album':album})

def top3_ocjenjena_albuma(request):
    albumi=Album.objects.annotate(prosjecna_ocjena=Avg('recenzije__ocjena')).order_by('-prosjecna_ocjena')[:3]
    return render(request, 'albumi/top3_ocjenjena_albuma.html', {'albumi':albumi})

def top3_ocjenjena_albuma_detalj(request, pk):
    album=get_object_or_404(Album, pk=pk)
    recenzije=Recenzija.objects.filter(album=album)
    return render(request, 'albumi/top3_ocjenjena_albuma_detalj.html', {'recenzije':recenzije})

def top3_zanra_po_prodaji(request):
    zanrovi=Zanr.objects.annotate(broj_prodaja=Count('albumi__prodaje')).order_by('-broj_prodaja')[:3]
    return render(request, 'albumi/top_zanrovi.html', {'zanrovi':zanrovi})

def top3_zanra_po_prodaji_detalj_zanra(request, pk):
    zanr=get_object_or_404(Zanr, pk=pk)
    albumi=Album.objects.filter(zanr=zanr).annotate(broj_prodaja=Count('prodaje')).order_by('-broj_prodaja')
    return render(request, 'albumi/top3_zanra_detalj.html', {'albumi':albumi})

def top3_izvodjaca_s_najvecim_brojem_recenzija(request):
    izvodjaci=Izvodjac.objects.annotate(broj_recenzija=Count('albumi__recenzije')).order_by('-broj_recenzija')
    return render(request, 'albumi/top_izvodjaci_po_recenzijama.html', {'izvodjaci':izvodjaci})

def top3_izvodjaca_s_najvecim_brojem_recenzija_detalj(request,pk):
    izvodjac=get_object_or_404(Izvodjac, pk=pk)
    albumi=Album.objects.filter(izvodjac=izvodjac).annotate(prosjecna_ocjena=Avg('recenzije__ocjena'))
    return render(request, 'albumi/top_izvodjaci_po_recenzijama_detalj.html', {'albumi':albumi, 'izvodjac':izvodjac})

def top3_korisnika_po__broju_recenzija(request):
    korisnici = User.objects.annotate(
        broj_recenzija=Count('recenzija')
    ).order_by('-broj_recenzija')[:3]

def top3_izvodjaca_po_prihodu(request):
    izvodjaci = Izvodjac.objects.annotate(
        ukupan_prihod=Sum('albumi__prodaje__cijena')
    ).order_by('-ukupan_prihod')[:3]

def top3_zanra_po_ocjeni(request):
    zanrovi = Zanr.objects.annotate(
        prosjecna_ocjena=Avg('albumi__recenzije__ocjena')
    ).order_by('-prosjecna_ocjena')[:3]

def top3_potrosaci(request):
    korisnici = User.objects.annotate(ukupno_potroseno=Sum('prodaja__cijena')).order_by('-ukupno_potroseno')[:3]
    return render(request, 'albumi/top3_potrosaci.html', {'korisnici': korisnici})

def top3_potrosaci_detalj(request, pk):
    korisnik = get_object_or_404(User, pk=pk)
    prodaje = Prodaja.objects.filter(korisnik=korisnik).select_related('album').order_by('-cijena')
    return render(request, 'albumi/top3_potrosaci_detalj.html', {'korisnik': korisnik, 'prodaje': prodaje})

def top3_zanrovi_po_broju_albuma(request):
    zanrovi = Zanr.objects.annotate(broj_albuma=Count('albumi')).order_by('-broj_albuma')[:3]
    return render(request, 'albumi/top3_zanrovi.html', {'zanrovi': zanrovi})

def top3_zanrovi_po_broju_albuma_detalj(request, pk):
    zanr = get_object_or_404(Zanr, pk=pk)
    albumi = Album.objects.filter(zanr=zanr).select_related('izvodjac').order_by('naslov')
    return render(request, 'albumi/top3_zanrovi_detalj.html', {'zanr': zanr, 'albumi': albumi})

def top3_albuma_po_broju_recenzija(request):
    albumi = Album.objects.annotate(broj_recenzija=Count('recenzije')).order_by('-broj_recenzija')[:3]
    return render(request, 'albumi/top3_albuma_recenzije.html', {'albumi': albumi})

def top3_albuma_po_broju_recenzija_detalj(request, pk):
    album = get_object_or_404(Album, pk=pk)
    recenzije = Recenzija.objects.filter(album=album).select_related('korisnik').order_by('-datum')
    return render(request, 'albumi/top3_albuma_recenzije_detalj.html', {'album': album, 'recenzije': recenzije})

def top3_skupi_albumi(request):
    albumi = Album.objects.order_by('-cijena')[:3]
    return render(request, 'albumi/top3_skupi_albumi.html', {'albumi': albumi})

def top3_skupi_albumi_detalj(request, pk):
    album = get_object_or_404(Album, pk=pk)
    kupci = Prodaja.objects.filter(album=album).select_related('korisnik').order_by('-datum')
    return render(request, 'albumi/top3_skupi_albumi_detalj.html', {'album': album, 'kupci': kupci})

def top3_izvodjaca_po_prihodu(request):
    izvodjaci = Izvodjac.objects.annotate(ukupan_prihod=Sum('albumi__prodaje__cijena')).order_by('-ukupan_prihod')[:3]
    return render(request, 'albumi/top3_izvodjaca_po_prihodu.html', {'izvodjaci': izvodjaci})

def top3_izvodjaca_po_prihodu_detalj(request, pk):
    izvodjac = get_object_or_404(Izvodjac, pk=pk)
    albumi = Album.objects.filter(izvodjac=izvodjac).annotate(prihod=Sum('prodaje__cijena')).order_by('-prihod')
    return render(request, 'albumi/top3_izvodjaca_po_prihodu_detalj.html', {'izvodjac': izvodjac, 'albumi': albumi})

def top3_zanra_po_ocjeni(request):
    zanrovi = Zanr.objects.annotate(prosjecna_ocjena=Avg('albumi__recenzije__ocjena')).order_by('-prosjecna_ocjena')[:3]
    return render(request, 'albumi/top3_zanra_po_ocjeni.html', {'zanrovi': zanrovi})

def top3_zanra_po_ocjeni_detalj(request, pk):
    zanr = get_object_or_404(Zanr, pk=pk)
    albumi = Album.objects.filter(zanr=zanr).annotate(prosjecna_ocjena=Avg('recenzije__ocjena')).order_by('-prosjecna_ocjena')
    return render(request, 'albumi/top3_zanra_po_ocjeni_detalj.html', {'zanr': zanr, 'albumi': albumi})

def top3_albuma_po_prihodu(request):
    albumi = Album.objects.annotate(ukupan_prihod=Sum('prodaje__cijena')).order_by('-ukupan_prihod')[:3]
    return render(request, 'albumi/top3_albuma_po_prihodu.html', {'albumi': albumi})

def top3_albuma_po_prihodu_detalj(request, pk):
    album = get_object_or_404(Album, pk=pk)
    kupci = Prodaja.objects.filter(album=album).select_related('korisnik').order_by('-datum')
    return render(request, 'albumi/top3_albuma_po_prihodu_detalj.html', {'album': album, 'kupci': kupci})

def top3_korisnika_po_ocjenama_iz_recenzija(request):
    korisnici = User.objects.annotate(prosjecna_ocjena=Avg('recenzija__ocjena')).order_by('-prosjecna_ocjena')[:3]
    return render(request, 'albumi/top3_korisnika_po_ocjenama.html', {'korisnici': korisnici})

def top3_korisnika_po_ocjenama_iz_recenzija_detalj(request, pk):
    korisnik = get_object_or_404(User, pk=pk)
    recenzije = Recenzija.objects.filter(korisnik=korisnik).select_related('album').order_by('-ocjena')
    return render(request, 'albumi/top3_korisnika_po_ocjenama_detalj.html', {'korisnik': korisnik, 'recenzije': recenzije})

def top3_izvodjaca_po_broju_albuma(request):
    izvodjaci = Izvodjac.objects.annotate(broj_albuma=Count('albumi')).order_by('-broj_albuma')[:3]
    return render(request, 'albumi/top3_izvodjaca_po_albumima.html', {'izvodjaci': izvodjaci})

def top3_izvodjaca_po_broju_albuma_detalj(request, pk):
    izvodjac = get_object_or_404(Izvodjac, pk=pk)
    albumi = Album.objects.filter(izvodjac=izvodjac).annotate(broj_prodaja=Count('prodaje')).order_by('-broj_prodaja')
    return render(request, 'albumi/top3_izvodjaca_po_albumima_detalj.html', {'izvodjac': izvodjac, 'albumi': albumi})


def albumi_bez_recenzija(request):
    albumi = Album.objects.annotate(broj_recenzija=Count('recenzije')).filter(broj_recenzija=0)
    return render(request, 'albumi/albumi_bez_recenzija.html', {'albumi': albumi})

def korisnici_bez_kupovine(request):
    korisnici = User.objects.annotate(broj_kupovina=Count('prodaja')).filter(broj_kupovina=0)
    return render(request, 'albumi/korisnici_bez_kupovine.html', {'korisnici': korisnici})

def korisnici_koji_su_kupili_i_recenzirali(request):
    korisnici = User.objects.annotate(
        broj_kupovina=Count('prodaja'),
        broj_recenzija=Count('recenzija')
    ).filter(broj_kupovina__gt=0, broj_recenzija__gt=0)
    return render(request, 'albumi/korisnici_aktivni.html', {'korisnici': korisnici})

def albumi_nikad_nisu_kupljeni(request):
    albumi = Album.objects.annotate(broj_prodaja=Count('prodaje')).filter(broj_prodaja=0)
    return render(request, 'albumi/albumi_nekupljeni.html', {'albumi': albumi})

def albumi_bez_recenzija(request):
    albumi = Album.objects.annotate(
        broj_recenzija=Count('recenzije')
    ).filter(broj_recenzija=0)
    return render(request, 'albumi/albumi_bez_recenzija.html', {'albumi': albumi})

def izvodjaci_bez_recenzija(request):
    izvodjaci = Izvodjac.objects.annotate(
        broj_recenzija=Count('albumi__recenzije')
    ).filter(broj_recenzija=0)
    return render(request, 'albumi/izvodjaci_bez_recenzija.html', {'izvodjaci': izvodjaci})


def zanrovi_bez_prodaje(request):
    zanrovi = Zanr.objects.annotate(
        broj_prodaja=Count('albumi__prodaje')
    ).filter(broj_prodaja=0)
    return render(request, 'albumi/zanrovi_bez_prodaje.html', {'zanrovi': zanrovi})


def korisnici_bez_recenzija(request):
    korisnici = User.objects.annotate(
        broj_recenzija=Count('recenzija')
    ).filter(broj_recenzija=0)
    return render(request, 'albumi/korisnici_bez_recenzija.html', {'korisnici': korisnici})


def zanrovi_bez_recenzija(request):
    zanrovi = Zanr.objects.annotate(
        broj_recenzija=Count('albumi__recenzije')
    ).filter(broj_recenzija=0)
    return render(request, 'albumi/zanrovi_bez_recenzija.html', {'zanrovi': zanrovi})

def forma_pretrage(request):
    return render(request, 'albumi/forma_pretrage.html', {
        'zanrovi': Zanr.objects.all(),
        'izvodjaci': Izvodjac.objects.all(),
    })

def rezultati_pretrage(request):
    albumi = Album.objects.select_related('izvodjac', 'zanr').all()
    
    godina = request.GET.get('godina', '')
    drzava = request.GET.get('drzava', '')
    zanr_id = request.GET.get('zanr', '')
    izvodjac_id = request.GET.get('izvodjac', '')

    if godina:
        albumi = albumi.filter(godina=godina)
    if drzava:
        albumi = albumi.filter(izvodjac__drzava__icontains=drzava)
    if zanr_id:
        albumi = albumi.filter(zanr_id=zanr_id)
    if izvodjac_id:
        albumi = albumi.filter(izvodjac_id=izvodjac_id)

    return render(request, 'albumi/rezultati_pretrage.html', {
        'albumi': albumi,
        'godina': godina,
        'drzava': drzava,
    })

def statistika_po_godini(request):
    from django.db.models import Count, Sum
    godine = Album.objects.values('godina').annotate(
        broj_albuma=Count('id'),
        broj_prodaja=Count('prodaje'),
        ukupan_prihod=Sum('prodaje__cijena')
    ).order_by('-godina')
    return render(request, 'albumi/statistika_po_godini.html', {'godine': godine})

def izvodjaci_bez_prodaje(request):
    izvodjaci = Izvodjac.objects.annotate(
        broj_prodaja=Count('albumi__prodaje')
    ).filter(broj_prodaja=0)
    return render(request, 'albumi/izvodjaci_bez_prodaje.html', {'izvodjaci': izvodjaci})

