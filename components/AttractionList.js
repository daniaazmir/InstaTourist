import React, { useState } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import AttractionDetail from './AttractionDetail';
import ItineraryPlanner from './ItineraryPlanner';
import { MaterialIcons } from '@expo/vector-icons';

const AttractionList = ({ attractions }) => {
  const [selectedAttraction, setSelectedAttraction] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [plannerVisible, setPlannerVisible] = useState(false);

  const handleAttractionPress = (attraction) => {
    setSelectedAttraction(attraction);
    setModalVisible(true);
  };

  return (
    <>
      <TouchableOpacity
        style={styles.plannerButton}
        onPress={() => setPlannerVisible(true)}
      >
        <MaterialIcons name="schedule" size={24} color="white" />
        <Text style={styles.plannerButtonText}>Plan My Day</Text>
      </TouchableOpacity>

      <FlatList
        data={attractions}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <TouchableOpacity onPress={() => handleAttractionPress(item)}>
            <View style={styles.card}>
              <Text style={styles.name}>{item.name}</Text>
              <Text style={styles.description}>{item.description}</Text>
              {item.rating > 0 && (
                <Text style={styles.rating}>Rating: {item.rating} ⭐</Text>
              )}
            </View>
          </TouchableOpacity>
        )}
        style={styles.list}
      />

      <AttractionDetail
        attraction={selectedAttraction}
        visible={modalVisible}
        onClose={() => setModalVisible(false)}
      />

      <ItineraryPlanner
        attractions={attractions}
        visible={plannerVisible}
        onClose={() => setPlannerVisible(false)}
      />
    </>
  );
};

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
  plannerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#4CAF50',
    padding: 12,
    borderRadius: 10,
    marginBottom: 15,
    justifyContent: 'center',
  },
  plannerButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});

export default AttractionList;
