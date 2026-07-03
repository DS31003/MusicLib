const API_URL = 'http://192.168.1.15:8000/api';

let accessToken: string | null = null;

export function postaviToken(token: string | null) {
  accessToken = token;
}

async function fetchApi(endpoint: string, options: RequestInit = {}) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, { ...options, headers });

  if (!response.ok) {
    const greska = await response.json().catch(() => ({}));
    throw new Error(greska.greska || `Greška ${response.status}`);
  }

  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  login: (username: string, password: string) =>
    fetchApi('/token/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  popisAlbuma: (filteri?: Record<string, string>) => {
    const query = filteri ? '?' + new URLSearchParams(filteri).toString() : '';
    return fetchApi(`/albumi/${query}`);
  },

  detaljAlbuma: (pk: number) => fetchApi(`/albumi/${pk}/`),

  kupiAlbum: (pk: number) => fetchApi(`/albumi/${pk}/kupi/`, { method: 'POST' }),

  dodajRecenziju: (pk: number, tekst: string, ocjena: number) =>
    fetchApi(`/albumi/${pk}/recenzija/`, {
      method: 'POST',
      body: JSON.stringify({ tekst, ocjena }),
    }),

  kolekcija: () => fetchApi('/kolekcija/'),

  izvodjaci: () => fetchApi('/izvodjaci/'),

  zanrovi: () => fetchApi('/zanrovi/'),

  registracija: (username: string, password: string) =>
    fetchApi('/registracija/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),
};
