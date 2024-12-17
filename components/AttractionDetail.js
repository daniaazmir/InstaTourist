import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  Image, 
  ScrollView, 
  Modal,
  TouchableOpacity,
  ActivityIndicator
} from 'react-native';

const AttractionDetail = ({ attraction, visible, onClose }) => {
  const [placeDetails, setPlaceDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (visible && attraction) {
      fetchPlaceDetails();
    }
  }, [visible, attraction]);

  const fetchPlaceDetails = async () => {
    try {
      const response = await fetch(
        `http://192.168.1.15:5000/api/place-details/${attraction.id}`
      );
      const data = await response.json();
      setPlaceDetails(data);
    } catch (error) {
      console.error('Error fetching place details:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!attraction) return null;

  return (
    <Modal
      animationType="slide"
      transparent={true}
      visible={visible}
      onRequestClose={onClose}
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalContent}>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Text style={styles.closeButtonText}>×</Text>
          </TouchableOpacity>

          <ScrollView>
            {loading ? (
              <ActivityIndicator size="large" color="#0000ff" />
            ) : (
              <>
                {placeDetails?.photos?.map((photo, index) => (
                  <Image
                    key={index}
                    source={{ uri: photo }}
                    style={styles.image}
                    resizeMode="cover"
                  />
                ))}

                <Text style={styles.name}>{attraction.name}</Text>
                <Text style={styles.description}>{attraction.description}</Text>
                
                {attraction.rating > 0 && (
                  <View style={styles.ratingContainer}>
                    <Text style={styles.rating}>Rating: {attraction.rating} ⭐</Text>
                    <Text>({placeDetails?.reviews?.length || 0} reviews)</Text>
                  </View>
                )}

                {placeDetails?.reviews?.map((review, index) => (
                  <View key={index} style={styles.reviewContainer}>
                    <Text style={styles.reviewAuthor}>{review.author_name}</Text>
                    <Text style={styles.reviewRating}>Rating: {review.rating} ⭐</Text>
                    <Text style={styles.reviewText}>{review.text}</Text>
                  </View>
                ))}
              </>
            )}
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: 'white',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    maxHeight: '80%',
  },
  closeButton: {
    position: 'absolute',
    right: 20,
    top: 20,
    zIndex: 1,
  },
  closeButtonText: {
    fontSize: 30,
    color: '#000',
  },
  image: {
    width: '100%',
    height: 200,
    borderRadius: 10,
    marginBottom: 15,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  description: {
    fontSize: 16,
    color: '#666',
    marginBottom: 15,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  rating: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFA000',
    marginRight: 10,
  },
  reviewContainer: {
    padding: 15,
    backgroundColor: '#f5f5f5',
    borderRadius: 10,
    marginBottom: 10,
  },
  reviewAuthor: {
    fontWeight: 'bold',
    marginBottom: 5,
  },
  reviewRating: {
    color: '#FFA000',
    marginBottom: 5,
  },
  reviewText: {
    color: '#444',
  },
});

export default AttractionDetail; 