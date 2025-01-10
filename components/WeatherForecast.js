import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  ActivityIndicator 
} from 'react-native';

const WeatherForecast = ({ latitude, longitude }) => {
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchWeatherData();
  }, [latitude, longitude]);

  const fetchWeatherData = async () => {
    try {
      console.log(`Fetching weather for coordinates: ${latitude}, ${longitude}`);  // Debug log
      const response = await fetch(
        `http://192.168.1.16:5000/api/weather/${latitude}/${longitude}`
      );
      const data = await response.json();
      
      console.log('Weather API response:', data);  // Debug log
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      setForecast(data);
    } catch (err) {
      console.error('Weather fetch error:', err);  // Debug log
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <ActivityIndicator size="large" color="#0000ff" />;
  }

  if (error) {
    return <Text style={styles.error}>Error: {error}</Text>;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.location}>
        {forecast.location}, {forecast.country}
      </Text>
      
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {forecast.forecast.map((day, index) => (
          <View key={index} style={styles.dayContainer}>
            <Text style={styles.date}>
              {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
            </Text>
            <Text style={styles.temp}>
              {Math.round(day.max_temp)}°C
            </Text>
            <Text style={styles.temp}>
              {Math.round(day.min_temp)}°C
            </Text>
            <Text style={styles.condition}>
              {day.day_condition}
            </Text>
            {/* <Text style={styles.precipitation}>
              {day.precipitation_probability}% rain
            </Text> */}
          </View>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 15,
    backgroundColor: 'white',
    borderRadius: 10,
    margin: 10,
  },
  location: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  dayContainer: {
    alignItems: 'center',
    marginRight: 20,
    minWidth: 80,
  },
  date: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  temp: {
    fontSize: 14,
  },
  condition: {
    fontSize: 12,
    textAlign: 'center',
    marginTop: 5,
  },
  precipitation: {
    fontSize: 12,
    color: '#666',
  },
  error: {
    color: 'red',
    textAlign: 'center',
    margin: 10,
  },
});

export default WeatherForecast; 