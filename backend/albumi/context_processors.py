def zaposlenik_status(request):
    je_zaposlenik = False
    if request.user.is_authenticated:
        je_zaposlenik = request.user.groups.filter(name='Zaposlenici').exists()
    return {'je_zaposlenik': je_zaposlenik}