import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';
import * as Location from 'expo-location';
import MapView, { Marker } from 'react-native-maps';
import AttractionList from '../components/AttractionList';
import { sendNotification } from '../utils/notificationUtils';
import { fetchNearbyAttractions } from '../utils/locationUtils';
import LocationButton from '../components/LocationButton';

const HomeScreen = () => {
  const [locationEnabled, setLocationEnabled] = useState(false);
  const [attractions, setAttractions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [region, setRegion] = useState({
    latitude: 3.1390,  // Default to Malaysia
    longitude: 101.6869,
    latitudeDelta: 0.0922,
    longitudeDelta: 0.0421,
  });

  const enableLocation = async () => {
    setIsLoading(true);
    setError(null);
    try {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        setLocationEnabled(true);
        let location = await Location.getCurrentPositionAsync({});
        const { latitude, longitude } = location.coords;
        
        // Update map region
        setRegion({
          latitude,
          longitude,
          latitudeDelta: 0.0922,
          longitudeDelta: 0.0421,
        });

        const nearbyAttractions = await fetchNearbyAttractions(location.coords);
        setAttractions(nearbyAttractions);
        sendNotification('Attractions loaded', 'Check out the nearby places!');
      } else {
        alert('Permission to access location was denied');
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <MapView 
        style={styles.map}
        region={region}
      >
        {locationEnabled && (
          <Marker
            coordinate={{
              latitude: region.latitude,
              longitude: region.longitude,
            }}
            title="You are here"
          />
        )}
        {attractions.map((attraction) => (
          <Marker
            key={attraction.id}
            coordinate={{
              latitude: attraction.location.lat,
              longitude: attraction.location.lng,
            }}
            title={attraction.name}
            description={attraction.description}
          />
        ))}
      </MapView>
      
      <View style={styles.overlay}>
        <LocationButton 
          onPress={enableLocation} 
          enabled={locationEnabled}
          isLoading={isLoading}
        />
        {locationEnabled && <AttractionList attractions={attractions} />}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    width: Dimensions.get('window').width,
    height: Dimensions.get('window').height,
  },
  overlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'white',
    padding: 16,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: -2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
    maxHeight: '50%',
  },
});

export default HomeScreen;
