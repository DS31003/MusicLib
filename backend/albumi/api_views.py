from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.db.models import Avg
from .models import Album, Izvodjac, Zanr, Prodaja, Recenzija
from .serializers import (
    AlbumSerializer, IzvodjacSerializer, ZanrSerializer,
    ProdajaSerializer, RecenzijaSerializer,
)


@api_view(['GET'])
@permission_classes([AllowAny])
def popis_albuma_api(request):
    albumi = Album.objects.select_related('izvodjac', 'zanr').annotate(
        prosjecna_ocjena=Avg('recenzije__ocjena')
    ).order_by('-godina', 'naslov')

    naslov = request.GET.get('naslov', '').strip()
    izvodjac_id = request.GET.get('izvodjac', '')
    zanr_id = request.GET.get('zanr', '')
    godina = request.GET.get('godina', '')

    if naslov:
        albumi = albumi.filter(naslov__icontains=naslov)
    if izvodjac_id:
        albumi = albumi.filter(izvodjac_id=izvodjac_id)
    if zanr_id:
        albumi = albumi.filter(zanr_id=zanr_id)
    if godina:
        albumi = albumi.filter(godina=godina)

    return Response(AlbumSerializer(albumi, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def detalj_albuma_api(request, pk):
    album = Album.objects.select_related('izvodjac', 'zanr').filter(pk=pk).annotate(
        prosjecna_ocjena=Avg('recenzije__ocjena')
    ).first()

    if not album:
        return Response({'greska': 'Album ne postoji'}, status=status.HTTP_404_NOT_FOUND)

    recenzije = Recenzija.objects.filter(album=album).select_related('korisnik')

    vec_kupio = False
    vec_recenzirao = False
    if request.user.is_authenticated:
        vec_kupio = Prodaja.objects.filter(korisnik=request.user, album=album).exists()
        vec_recenzirao = Recenzija.objects.filter(korisnik=request.user, album=album).exists()

    return Response({
        'album': AlbumSerializer(album).data,
        'recenzije': RecenzijaSerializer(recenzije, many=True).data,
        'vec_kupio': vec_kupio,
        'vec_recenzirao': vec_recenzirao,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def izvodjaci_api(request):
    return Response(IzvodjacSerializer(Izvodjac.objects.all(), many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def zanrovi_api(request):
    return Response(ZanrSerializer(Zanr.objects.all(), many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def kupi_album_api(request, pk):
    album = Album.objects.filter(pk=pk).first()
    if not album:
        return Response({'greska': 'Album ne postoji'}, status=status.HTTP_404_NOT_FOUND)

    if Prodaja.objects.filter(korisnik=request.user, album=album).exists():
        return Response(
            {'greska': f'{album.naslov} već postoji u tvojoj kolekciji!'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    Prodaja.objects.create(korisnik=request.user, album=album, cijena=album.cijena)
    return Response({'poruka': f'Kupio si {album.naslov}!'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kolekcija_api(request):
    prodaje = Prodaja.objects.filter(korisnik=request.user).select_related(
        'album', 'album__izvodjac', 'album__zanr'
    )
    return Response(ProdajaSerializer(prodaje, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dodaj_recenziju_api(request, pk):
    album = Album.objects.filter(pk=pk).first()
    if not album:
        return Response({'greska': 'Album ne postoji'}, status=status.HTTP_404_NOT_FOUND)

    if not Prodaja.objects.filter(korisnik=request.user, album=album).exists():
        return Response(
            {'greska': 'Možeš recenzirati samo svoje albume!'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if Recenzija.objects.filter(korisnik=request.user, album=album).exists():
        return Response(
            {'greska': 'Recenzija s ovog računa već postoji!'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = RecenzijaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(korisnik=request.user, album=album)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def registracija_api(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'greska': 'Username i password su obavezni'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({'greska': 'Korisnik već postoji'}, status=status.HTTP_400_BAD_REQUEST)

    User.objects.create_user(username=username, password=password)
    return Response({'poruka': 'Registracija uspješna'}, status=status.HTTP_201_CREATED)
