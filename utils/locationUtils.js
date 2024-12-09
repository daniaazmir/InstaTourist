export const fetchNearbyAttractions = async (coords, radius) => {
  const { latitude, longitude } = coords;
  
  try {
    const url = `http://192.168.1.8:5000/api/nearby-attractions/${latitude}/${longitude}/${radius}`;
    console.log('Fetching from URL:', url);

    const response = await fetch(url);
    const data = await response.json();
    
    console.log('API Response:', data);
    return data;
  } catch (error) {
    console.error('Error fetching places:', error);
    return [];
  }
};
  