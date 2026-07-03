import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import { api, postaviToken } from '../api';

interface Props {
  naLogin: () => void;
}

export default function LoginScreen({ naLogin }: Props) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [greska, setGreska] = useState('');

  async function prijaviSe() {
    setGreska('');
    try {
      const podaci = await api.login(username, password);
      postaviToken(podaci.access);
      naLogin();
    } catch (e: any) {
      setGreska(e.message);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.naslov}>Prijava</Text>

      <TextInput
        style={styles.input}
        placeholder="Korisničko ime"
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
      />
      <TextInput
        style={styles.input}
        placeholder="Lozinka"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      {greska ? <Text style={styles.greska}>{greska}</Text> : null}

      <Button title="Prijavi se" onPress={prijaviSe} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: 'center' },
  naslov: { fontSize: 24, fontWeight: 'bold', marginBottom: 20 },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 6,
    padding: 10,
    marginBottom: 12,
  },
  greska: { color: 'red', marginBottom: 12 },
});
