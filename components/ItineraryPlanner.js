import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Platform,
  Button,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import RNPickerSelect from 'react-native-picker-select';

const ItineraryPlanner = ({ attractions, visible, onClose }) => {
  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [preferences, setPreferences] = useState({
    startTime: '9:00 AM',
    endTime: '6:00 PM',
    pace: 'moderate',
    transportation: 'walking',
  });

  useEffect(() => {
    if (!visible) {
      setItinerary(null);
      setPreferences({
        startTime: '9:00 AM',
        endTime: '6:00 PM',
        pace: 'moderate',
        transportation: 'walking',
      });
    }
  }, [visible]);

  const handleClose = () => {
    setItinerary(null);
    onClose();
  };

  const timeOptions = [
    { label: '8:00 AM', value: '8:00 AM' },
    { label: '9:00 AM', value: '9:00 AM' },
    { label: '10:00 AM', value: '10:00 AM' },
    { label: '11:00 AM', value: '11:00 AM' },
    { label: '12:00 PM', value: '12:00 PM' },
    { label: '1:00 PM', value: '1:00 PM' },
    { label: '2:00 PM', value: '2:00 PM' },
    { label: '3:00 PM', value: '3:00 PM' },
    { label: '4:00 PM', value: '4:00 PM' },
    { label: '5:00 PM', value: '5:00 PM' },
    { label: '6:00 PM', value: '6:00 PM' },
  ];

  const paceOptions = [
    { label: 'Relaxed - Take your time', value: 'relaxed' },
    { label: 'Moderate - Balanced pace', value: 'moderate' },
    { label: 'Fast - See as much as possible', value: 'fast' }
  ];

  const transportOptions = [
    { label: '🚶 Walking', value: 'walking' },
    { label: '🚌 Public Transport', value: 'public_transport' },
    { label: '🚗 Driving', value: 'driving' }
  ];

  const retryFetch = async (url, options, maxRetries = 3) => {
    for (let i = 0; i < maxRetries; i++) {
      try {
        const response = await fetch(url, options);
        return response;
      } catch (err) {
        if (i === maxRetries - 1) throw err;
        await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1))); // Exponential backoff
      }
    }
  };

  const generateItinerary = async () => {
    setLoading(true);
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);

      const response = await retryFetch(
        'http://10.168.234.234:5000/api/generate-itinerary',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            attractions,
            preferences,
            latitude: attractions[0].location.lat,
            longitude: attractions[0].location.lng,
          }),
          signal: controller.signal,
        }
      );
      
      clearTimeout(timeoutId);
      
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      setItinerary(data.itinerary);
    } catch (error) {
      console.error('Error generating itinerary:', error);
      alert(
        error.name === 'AbortError' 
          ? 'Request took too long. Please try again.'
          : 'Failed to generate itinerary. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      animationType="slide"
      transparent={true}
      visible={visible}
      onRequestClose={handleClose}
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalContent}>
          <TouchableOpacity style={styles.closeButton} onPress={handleClose}>
            <MaterialIcons name="close" size={24} color="#000" />
          </TouchableOpacity>
          
          <Text style={styles.title}>Plan Your Day</Text>
          
          <ScrollView style={styles.preferencesContainer}>
            <Text style={styles.sectionTitle}>Customize Your Plan</Text>
            
            <View style={styles.pickerContainer}>
              <Text style={styles.label}>Start Time</Text>
              <View style={styles.pickerWrapper}>
                <RNPickerSelect
                  onValueChange={(value) => setPreferences({...preferences, startTime: value})}
                  value={preferences.startTime}
                  items={timeOptions}
                  style={pickerSelectStyles}
                  useNativeAndroidPickerStyle={false}
                  placeholder={{ label: 'Select start time...', value: null }}
                  Icon={() => <MaterialIcons name="arrow-drop-down" size={24} color="#666" />}
                />
              </View>
            </View>

            <View style={styles.pickerContainer}>
              <Text style={styles.label}>End Time</Text>
              <View style={styles.pickerWrapper}>
                <RNPickerSelect
                  onValueChange={(value) => setPreferences({...preferences, endTime: value})}
                  value={preferences.endTime}
                  items={timeOptions}
                  style={pickerSelectStyles}
                  useNativeAndroidPickerStyle={false}
                  placeholder={{ label: 'Select end time...', value: null }}
                  Icon={() => <MaterialIcons name="arrow-drop-down" size={24} color="#666" />}
                />
              </View>
            </View>

            <View style={styles.pickerContainer}>
              <Text style={styles.label}>Pace</Text>
              <View style={styles.pickerWrapper}>
                <RNPickerSelect
                  onValueChange={(value) => setPreferences({...preferences, pace: value})}
                  value={preferences.pace}
                  items={paceOptions}
                  style={pickerSelectStyles}
                  useNativeAndroidPickerStyle={false}
                  placeholder={{ label: 'Select pace...', value: null }}
                  Icon={() => <MaterialIcons name="arrow-drop-down" size={24} color="#666" />}
                />
              </View>
            </View>

            <View style={styles.pickerContainer}>
              <Text style={styles.label}>Transportation</Text>
              <View style={styles.pickerWrapper}>
                <RNPickerSelect
                  onValueChange={(value) => setPreferences({...preferences, transportation: value})}
                  value={preferences.transportation}
                  items={transportOptions}
                  style={pickerSelectStyles}
                  useNativeAndroidPickerStyle={false}
                  placeholder={{ label: 'Select transportation...', value: null }}
                  Icon={() => <MaterialIcons name="arrow-drop-down" size={24} color="#666" />}
                />
              </View>
            </View>
          </ScrollView>

          <TouchableOpacity 
            style={styles.generateButton}
            onPress={generateItinerary}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="white" />
            ) : (
              <Text style={styles.generateButtonText}>Generate Itinerary</Text>
            )}
          </TouchableOpacity>

          {itinerary && (
            <ScrollView style={styles.itineraryContainer}>
              <View style={styles.itineraryHeader}>
                <MaterialIcons name="schedule" size={24} color="#2196F3" />
                <Text style={styles.itineraryHeaderText}>Your Personalized Itinerary</Text>
              </View>
              
              {itinerary.split('\n').map((line, index) => {
                if (line.trim() === '') return null;
                
                if (line.includes(' - ') && line.includes('AM') || line.includes('PM')) {
                  // This is a time-location line
                  const [time, rest] = line.split(' - ');
                  const [location, duration] = rest.split(' (');
                  return (
                    <View key={index} style={styles.timeBlock}>
                      <View style={styles.timeStamp}>
                        <MaterialIcons name="access-time" size={20} color="#2196F3" />
                        <Text style={styles.timeText}>{time.trim()}</Text>
                      </View>
                      <View style={styles.locationContainer}>
                        <Text style={styles.locationText}>{location.trim()}</Text>
                        <Text style={styles.durationText}>
                          {duration ? `(${duration.replace(')', '')}` : ''}
                        </Text>
                      </View>
                    </View>
                  );
                } else if (line.startsWith('-')) {
                  // This is a detail/tip line
                  return (
                    <View key={index} style={styles.detailItem}>
                      <MaterialIcons 
                        name={
                          line.toLowerCase().includes('weather') ? 'wb-sunny' :
                          line.toLowerCase().includes('travel') ? 'directions' :
                          'info'
                        } 
                        size={16} 
                        color="#666"
                      />
                      <Text style={styles.detailText}>{line.substring(1).trim()}</Text>
                    </View>
                  );
                } else {
                  // Other lines (headers, etc)
                  return (
                    <Text key={index} style={styles.regularText}>{line}</Text>
                  );
                }
              })}
            </ScrollView>
          )}
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
    maxHeight: '90%',
  },
  closeButton: {
    position: 'absolute',
    right: 20,
    top: 20,
    zIndex: 1,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  preferencesContainer: {
    maxHeight: 300,
    marginBottom: 15,
  },
  pickerWrapper: {
    backgroundColor: 'white',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ccc',
    marginTop: 5,
  },
  pickerContainer: {
    marginBottom: 20,
    marginBottom: 15,
    backgroundColor: '#f5f5f5',
    borderRadius: 10,
    padding: 10,
  },
  label: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 5,
    color: '#333',
  },
  picker: {
    backgroundColor: 'white',
    borderRadius: 8,
  },
  generateButton: {
    backgroundColor: '#2196F3',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginVertical: 20,
  },
  generateButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  itineraryContainer: {
    marginTop: 10,
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 15,
  },
  itineraryHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  itineraryHeaderText: {
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 10,
    color: '#2196F3',
  },
  timeBlock: {
    marginBottom: 15,
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  timeStamp: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  timeText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2196F3',
    marginLeft: 5,
  },
  locationContainer: {
    marginLeft: 25,
  },
  locationText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
  durationText: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 35,
    marginBottom: 8,
    backgroundColor: '#f0f0f0',
    padding: 8,
    borderRadius: 6,
  },
  detailText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 8,
    flex: 1,
  },
  regularText: {
    fontSize: 15,
    color: '#444',
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
});

const pickerSelectStyles = StyleSheet.create({
  inputIOS: {
    fontSize: 16,
    paddingVertical: 12,
    paddingHorizontal: 10,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    color: 'black',
    backgroundColor: 'white',
    paddingRight: 30,
  },
  inputAndroid: {
    fontSize: 16,
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    color: 'black',
    backgroundColor: 'white',
    paddingRight: 30,
  },
});

export default ItineraryPlanner; 