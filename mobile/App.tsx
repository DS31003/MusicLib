import React, { useState } from 'react';
import { SafeAreaView } from 'react-native';
import LoginScreen from './src/screens/LoginScreen';
import AlbumListScreen from './src/screens/AlbumListScreen';
import AlbumDetailScreen from './src/screens/AlbumDetailScreen';

type Ekran = 'login' | 'popis' | 'detalj';

export default function App() {
  const [ekran, setEkran] = useState<Ekran>('login');
  const [albumId, setAlbumId] = useState<number | null>(null);

  return (
    <SafeAreaView style={{ flex: 1 }}>
      {ekran === 'login' && (
        <LoginScreen naLogin={() => setEkran('popis')} />
      )}

      {ekran === 'popis' && (
        <AlbumListScreen
          naDetalj={(pk) => {
            setAlbumId(pk);
            setEkran('detalj');
          }}
        />
      )}

      {ekran === 'detalj' && albumId !== null && (
        <AlbumDetailScreen
          albumId={albumId}
          natrag={() => setEkran('popis')}
        />
      )}
    </SafeAreaView>
  );
}
