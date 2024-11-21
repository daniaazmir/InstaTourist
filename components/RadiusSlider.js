import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Slider from '@react-native-community/slider';

const RadiusSlider = ({ radius, onRadiusChange }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.label}>Search Radius: {(radius/1000).toFixed(1)} km</Text>
      <Slider
        style={styles.slider}
        minimumValue={1000}
        maximumValue={50000}
        step={1000}
        value={radius}
        onValueChange={onRadiusChange}
        minimumTrackTintColor="#2196F3"
        maximumTrackTintColor="#000000"
        thumbTintColor="#2196F3"
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 10,
    backgroundColor: 'white',
    borderRadius: 10,
    marginBottom: 10,
  },
  label: {
    fontSize: 16,
    marginBottom: 5,
    textAlign: 'center',
  },
  slider: {
    width: '100%',
    height: 40,
  },
});

export default RadiusSlider; 