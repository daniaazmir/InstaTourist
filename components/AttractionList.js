import React from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';

const AttractionList = ({ attractions }) => (
  <FlatList
    data={attractions}
    keyExtractor={(item) => item.id.toString()}
    renderItem={({ item }) => (
      <View style={styles.card}>
        <Text style={styles.name}>{item.name}</Text>
        <Text style={styles.description}>{item.description}</Text>
        {item.rating > 0 && (
          <Text style={styles.rating}>Rating: {item.rating} ⭐</Text>
        )}
      </View>
    )}
    style={styles.list}
  />
);

const styles = StyleSheet.create({
  list: {
    maxHeight: '80%',
  },
  card: {
    padding: 15,
    backgroundColor: 'white',
    borderRadius: 10,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  name: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  description: {
    color: '#666',
    marginBottom: 5,
  },
  rating: {
    color: '#FFA000',
    fontWeight: 'bold',
  },
});

export default AttractionList;
