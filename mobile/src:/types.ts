export interface Zanr {
  id: number;
  naziv: string;
}

export interface Izvodjac {
  id: number;
  ime: string;
  drzava: string;
  godina_osnivanja: number | null;
}

export interface Album {
  id: number;
  naslov: string;
  izvodjac: Izvodjac;
  zanr: Zanr;
  godina: number;
  broj_pjesama: number;
  trajanje_min: number;
  omot: string | null;
  opis: string;
  cijena: string;
  prosjecna_ocjena: number | null;
  ai_score: number | null;
}

export interface Recenzija {
  id: number;
  korisnik: string;
  album: number;
  tekst: string;
  ocjena: number;
  datum: string;
}

export interface Prodaja {
  id: number;
  album: Album;
  datum: string;
  cijena: string;
}

export interface DetaljAlbumaResponse {
  album: Album;
  recenzije: Recenzija[];
  vec_kupio: boolean;
  vec_recenzirao: boolean;
}
