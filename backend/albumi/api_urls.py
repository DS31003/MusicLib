from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import api_views

urlpatterns = [
    path('albumi/', api_views.popis_albuma_api, name='api_popis_albuma'),
    path('albumi/<int:pk>/', api_views.detalj_albuma_api, name='api_detalj_albuma'),
    path('albumi/<int:pk>/kupi/', api_views.kupi_album_api, name='api_kupi_album'),
    path('albumi/<int:pk>/recenzija/', api_views.dodaj_recenziju_api, name='api_dodaj_recenziju'),
    path('izvodjaci/', api_views.izvodjaci_api, name='api_izvodjaci'),
    path('zanrovi/', api_views.zanrovi_api, name='api_zanrovi'),
    path('kolekcija/', api_views.kolekcija_api, name='api_kolekcija'),
    path('registracija/', api_views.registracija_api, name='api_registracija'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
