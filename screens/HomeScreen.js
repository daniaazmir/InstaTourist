import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Dimensions, Alert, Text, TouchableOpacity } from 'react-native';
import * as Location from 'expo-location';
import * as Google from 'expo-auth-session/providers/google';
import MapView, { Marker, Callout } from 'react-native-maps';
import AttractionList from '../components/AttractionList';
import { sendNotification } from '../utils/notificationUtils';
import { fetchNearbyAttractions } from '../utils/locationUtils';
import LocationButton from '../components/LocationButton';
import RadiusSlider from '../components/RadiusSlider';
import ReviewModal from '../components/ReviewModal';
import { MaterialIcons } from '@expo/vector-icons';
import WeatherForecast from '../components/WeatherForecast';

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
  const [radius, setRadius] = useState(5000); // Default 5km
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [reviewModalVisible, setReviewModalVisible] = useState(false);
  const [userToken, setUserToken] = useState(null);
  const [userReviews, setUserReviews] = useState({});

  // Set up Google Sign In
  const [request, response, promptAsync] = Google.useAuthRequest({
    androidClientId: "your-android-client-id",
    iosClientId: "your-ios-client-id",
    expoClientId: "your-expo-client-id",
    webClientId: "your-web-client-id",
    responseType: "id_token",
    scopes: ["profile", "email"]
  });

  useEffect(() => {
    if (response?.type === 'success') {
      setUserToken(response.authentication.accessToken);
    }
  }, [response]);

  const enableLocation = async () => {
    setIsLoading(true);
    setError(null);
    try {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        setLocationEnabled(true);
        let location = await Location.getCurrentPositionAsync({});
        const { latitude, longitude } = location.coords;
        
        setRegion({
          latitude,
          longitude,
          latitudeDelta: 0.0922,
          longitudeDelta: 0.0421,
        });

        const nearbyAttractions = await fetchNearbyAttractions(location.coords, radius);
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

  const handleRadiusChange = async (newRadius) => {
    setRadius(newRadius);
    if (locationEnabled && region) {
      setIsLoading(true);
      const nearbyAttractions = await fetchNearbyAttractions(
        { latitude: region.latitude, longitude: region.longitude }, 
        newRadius
      );
      setAttractions(nearbyAttractions);
      setIsLoading(false);
    }
  };

  const handleSubmitReview = async (rating, review) => {
    try {
      setUserReviews(prev => ({
        ...prev,
        [selectedPlace.id]: { rating, review }
      }));
      
      Alert.alert('Success', 'Your review has been saved!');
      setReviewModalVisible(false);
    } catch (error) {
      console.error('Error saving review:', error);
      Alert.alert('Error', 'Failed to save review. Please try again.');
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
          >
            <Callout onPress={() => {
              if (!userReviews[attraction.id]) {
                setSelectedPlace(attraction);
                setReviewModalVisible(true);
              }
            }}>
              <View style={styles.calloutContainer}>
                <Text style={styles.calloutTitle}>{attraction.name}</Text>
                
                {userReviews[attraction.id] ? (
                  <View style={styles.reviewContainer}>
                    <Text style={styles.ratingText}>Your Rating:</Text>
                    <View style={styles.starsContainer}>
                      {[...Array(5)].map((_, index) => (
                        <MaterialIcons
                          key={index}
                          name="star"
                          size={16}
                          color={index < userReviews[attraction.id].rating ? '#FFA000' : '#D3D3D3'}
                        />
                      ))}
                    </View>
                  </View>
                ) : (
                  <View style={styles.reviewButton}>
                    <Text style={styles.reviewButtonText}>I've been here!</Text>
                  </View>
                )}
              </View>
            </Callout>
          </Marker>
        ))}
      </MapView>
      
      <View style={styles.overlay}>
        {locationEnabled && (
          <WeatherForecast 
            latitude={region.latitude}
            longitude={region.longitude}
          />
        )}
        <LocationButton 
          onPress={enableLocation} 
          enabled={locationEnabled}
          isLoading={isLoading}
        />
        {locationEnabled && (
          <>
            <RadiusSlider 
              radius={radius}
              onRadiusChange={handleRadiusChange}
            />
            <AttractionList attractions={attractions} />
          </>
        )}
      </View>

      <ReviewModal
        visible={reviewModalVisible}
        onClose={() => setReviewModalVisible(false)}
        place={selectedPlace}
        onSubmitReview={handleSubmitReview}
      />
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
  calloutContainer: {
    minWidth: 150,
    padding: 10,
  },
  calloutTitle: {
    fontWeight: 'bold',
    fontSize: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  reviewButton: {
    backgroundColor: '#4CAF50',
    padding: 8,
    borderRadius: 5,
    marginTop: 5,
  },
  reviewButtonText: {
    color: 'white',
    textAlign: 'center',
    fontWeight: 'bold',
  },
  reviewContainer: {
    alignItems: 'center',
    marginTop: 5,
  },
  ratingText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 3,
  },
  starsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
  },
});

export default HomeScreen;
