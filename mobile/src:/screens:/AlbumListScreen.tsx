import React, { useEffect, useState } from 'react';
import {
  View, Text, TextInput, FlatList, TouchableOpacity,
  StyleSheet, ActivityIndicator,
} from 'react-native';
import { api } from '../api';
import { Album } from '../types';

interface Props {
  naDetalj: (pk: number) => void;
}

export default function AlbumListScreen({ naDetalj }: Props) {
  const [albumi, setAlbumi] = useState<Album[]>([]);
  const [naslov, setNaslov] = useState('');
  const [ucitava, setUcitava] = useState(true);
  const [greska, setGreska] = useState('');

  async function ucitajAlbume() {
    setUcitava(true);
    setGreska('');
    try {
      const podaci = await api.popisAlbuma(naslov ? { naslov } : undefined);
      setAlbumi(podaci);
    } catch (e: any) {
      setGreska(e.message);
    } finally {
      setUcitava(false);
    }
  }

  useEffect(() => {
    ucitajAlbume();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.naslov}>Albumi</Text>

      <TextInput
        style={styles.pretraga}
        placeholder="Pretraži po naslovu..."
        value={naslov}
        onChangeText={setNaslov}
        onSubmitEditing={ucitajAlbume}
      />

      {greska ? <Text style={styles.greska}>{greska}</Text> : null}
      {ucitava && <ActivityIndicator size="large" />}

      <FlatList
        data={albumi}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.karta} onPress={() => naDetalj(item.id)}>
            <Text style={styles.albumNaslov}>{item.naslov}</Text>
            <Text style={styles.podnaslov}>
              {item.izvodjac.ime} · {item.godina} · {item.cijena} €
            </Text>
            {item.prosjecna_ocjena ? (
              <Text style={styles.ocjena}>★ {item.prosjecna_ocjena.toFixed(1)}</Text>
            ) : null}
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  naslov: { fontSize: 24, fontWeight: 'bold', marginBottom: 12 },
  pretraga: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 6,
    padding: 10,
    marginBottom: 12,
  },
  greska: { color: 'red', marginBottom: 8 },
  karta: {
    padding: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  albumNaslov: { fontSize: 16, fontWeight: '600' },
  podnaslov: { color: '#666', marginTop: 2 },
  ocjena: { color: '#e0a500', marginTop: 4 },
});
