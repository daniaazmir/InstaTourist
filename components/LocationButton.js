import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, Platform } from 'react-native';
import { BlurView } from 'expo-blur';

const LocationButton = ({ onPress, enabled, isLoading }) => (
  <TouchableOpacity 
    style={styles.buttonContainer} 
    onPress={onPress}
  >
    <BlurView intensity={80} style={[
      styles.button,
      enabled ? styles.enabledButton : styles.disabledButton
    ]}>
      {isLoading ? (
        <ActivityIndicator color="white" />
      ) : (
        <Text style={styles.buttonText}>
          {enabled ? "Location Enabled" : "Turn On Location"}
        </Text>
      )}
    </BlurView>
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  buttonContainer: {
    overflow: 'hidden',
    borderRadius: 25,
  },
  button: {
    padding: 15,
    alignItems: 'center',
    marginBottom: 10,
    borderRadius: 25,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  enabledButton: {
    backgroundColor: 'rgba(76, 175, 80, 0.3)',
  },
  disabledButton: {
    backgroundColor: 'rgba(33, 150, 243, 0.3)',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default LocationButton;
