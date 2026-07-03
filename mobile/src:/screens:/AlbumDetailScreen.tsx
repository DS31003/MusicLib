import React, { useEffect, useState } from 'react';
import {
  View, Text, Button, StyleSheet, ActivityIndicator,
  TextInput, ScrollView,
} from 'react-native';
import { api } from '../api';
import { DetaljAlbumaResponse } from '../types';

interface Props {
  albumId: number;
  natrag: () => void;
}

export default function AlbumDetailScreen({ albumId, natrag }: Props) {
  const [podaci, setPodaci] = useState<DetaljAlbumaResponse | null>(null);
  const [ucitava, setUcitava] = useState(true);
  const [poruka, setPoruka] = useState('');
  const [tekstRecenzije, setTekstRecenzije] = useState('');
  const [ocjena, setOcjena] = useState('5');

  async function ucitaj() {
    setUcitava(true);
    try {
      const rezultat = await api.detaljAlbuma(albumId);
      setPodaci(rezultat);
    } catch (e: any) {
      setPoruka(e.message);
    } finally {
      setUcitava(false);
    }
  }

  useEffect(() => {
    ucitaj();
  }, [albumId]);

  async function kupi() {
    setPoruka('');
    try {
      const rezultat = await api.kupiAlbum(albumId);
      setPoruka(rezultat.poruka);
      ucitaj();
    } catch (e: any) {
      setPoruka(e.message);
    }
  }

  async function posaljiRecenziju() {
    setPoruka('');
    try {
      await api.dodajRecenziju(albumId, tekstRecenzije, parseInt(ocjena, 10));
      setTekstRecenzije('');
      ucitaj();
    } catch (e: any) {
      setPoruka(e.message);
    }
  }

  if (ucitava) return <ActivityIndicator size="large" style={{ marginTop: 40 }} />;
  if (!podaci) return <Text style={styles.greska}>{poruka || 'Greška pri učitavanju'}</Text>;

  const { album, recenzije, vec_kupio, vec_recenzirao } = podaci;

  return (
    <ScrollView style={styles.container}>
      <Button title="← Natrag" onPress={natrag} />

      <Text style={styles.naslov}>{album.naslov}</Text>
      <Text style={styles.podnaslov}>{album.izvodjac.ime} · {album.godina}</Text>
      <Text style={styles.opis}>{album.opis}</Text>
      <Text style={styles.cijena}>{album.cijena} €</Text>

      {album.ai_score !== null && (
        <Text style={styles.aiScore}>AI Score: {album.ai_score}%</Text>
      )}

      {poruka ? <Text style={styles.poruka}>{poruka}</Text> : null}

      {!vec_kupio && <Button title="Kupi album" onPress={kupi} />}

      {vec_kupio && !vec_recenzirao && (
        <View style={styles.recenzijaForma}>
          <Text style={styles.podNaslov}>Ostavi recenziju</Text>
          <TextInput
            style={styles.input}
            placeholder="Tvoje mišljenje..."
            value={tekstRecenzije}
            onChangeText={setTekstRecenzije}
            multiline
          />
          <TextInput
            style={styles.input}
            placeholder="Ocjena (1-5)"
            value={ocjena}
            onChangeText={setOcjena}
            keyboardType="numeric"
          />
          <Button title="Pošalji recenziju" onPress={posaljiRecenziju} />
        </View>
      )}

      <Text style={styles.podNaslov}>Recenzije ({recenzije.length})</Text>
      {recenzije.map((r) => (
        <View key={r.id} style={styles.recenzijaKarta}>
          <Text style={styles.recenzijaKorisnik}>{r.korisnik} · ★ {r.ocjena}</Text>
          <Text>{r.tekst}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  naslov: { fontSize: 24, fontWeight: 'bold', marginTop: 12 },
  podnaslov: { color: '#666', marginBottom: 8 },
  opis: { marginBottom: 8 },
  cijena: { fontSize: 18, fontWeight: '600', marginBottom: 8 },
  aiScore: { color: '#2e7d32', fontWeight: '600', marginBottom: 12 },
  poruka: { color: '#c62828', marginVertical: 8 },
  greska: { color: 'red', margin: 20 },
  podNaslov: { fontSize: 18, fontWeight: '600', marginTop: 20, marginBottom: 8 },
  recenzijaForma: { marginTop: 16 },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 6,
    padding: 10,
    marginBottom: 10,
  },
  recenzijaKarta: {
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  recenzijaKorisnik: { fontWeight: '600' },
});
