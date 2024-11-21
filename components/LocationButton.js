import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator } from 'react-native';

const LocationButton = ({ onPress, enabled, isLoading }) => (
  <TouchableOpacity 
    style={[
      styles.button,
      enabled ? styles.enabledButton : styles.disabledButton
    ]} 
    onPress={onPress}
  >
    {isLoading ? (
      <ActivityIndicator color="white" />
    ) : (
      <Text style={styles.buttonText}>
        {enabled ? "Location Enabled" : "Turn On Location"}
      </Text>
    )}
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  button: {
    padding: 15,
    borderRadius: 25,
    alignItems: 'center',
    marginBottom: 10,
  },
  enabledButton: {
    backgroundColor: '#4CAF50',
  },
  disabledButton: {
    backgroundColor: '#2196F3',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default LocationButton;
