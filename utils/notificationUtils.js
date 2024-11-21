import * as Notifications from 'expo-notifications';

export const sendNotification = (title, body) => {
  Notifications.scheduleNotificationAsync({
    content: {
      title: title,
      body: body,
    },
    trigger: null, // Instant notification
  });
};
