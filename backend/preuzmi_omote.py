import urllib.request
import urllib.parse
import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zbirka.settings')
django.setup()

from albumi.models import Album

def dohvati_omot(naslov, izvodjac):
    try:
        upit = urllib.parse.quote(f'{naslov} {izvodjac}')
        url = f'https://itunes.apple.com/search?term={upit}&media=music&entity=album&limit=1'
        zahtjev = urllib.request.Request(url, headers={'User-Agent': 'GlazbenaZbirka/1.0'})
        odgovor = urllib.request.urlopen(zahtjev)
        podaci = json.loads(odgovor.read())
        
        if podaci['resultCount'] == 0:
            return None
            
        # iTunes daje 100x100, zamijeni sa 600x600
        slika_url = podaci['results'][0]['artworkUrl100']
        slika_url = slika_url.replace('100x100', '600x600')
        return slika_url
        
    except Exception as e:
        print(f'  API greška: {e}')
        return None

for album in Album.objects.all():  # all() da prepiše stare loše slike
    print(f'Tražim: {album.naslov} - {album.izvodjac}')
    url = dohvati_omot(album.naslov, str(album.izvodjac))
    if url:
        try:
            naziv_datoteke = f'omoti/{album.pk}.jpg'
            puna_putanja = f'media/{naziv_datoteke}'
            os.makedirs('media/omoti', exist_ok=True)
            zahtjev = urllib.request.Request(url, headers={'User-Agent': 'GlazbenaZbirka/1.0'})
            with urllib.request.urlopen(zahtjev) as odgovor:
                with open(puna_putanja, 'wb') as f:
                    f.write(odgovor.read())
            album.omot = naziv_datoteke
            album.save()
            print(f' OK ')
        except Exception as e:
            print(f'  Greška: {e}')
    else:
        print(f'  Nije pronađen')
