import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Platform } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

export default function TabsLayout() {
  const insets = useSafeAreaInsets();
  
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#4CAF50',
        tabBarInactiveTintColor: '#999',
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopWidth: 1,
          borderTopColor: '#E0E0E0',
          height: 60 + insets.bottom,
          paddingBottom: insets.bottom > 0 ? insets.bottom : 8,
          paddingTop: 8,
          position: 'absolute',
          elevation: 8,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: -2 },
          shadowOpacity: 0.1,
          shadowRadius: 4,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600',
          marginBottom: Platform.OS === 'android' ? 4 : 0,
        },
      }}
    >
      <Tabs.Screen
        name="dashboard"
        options={{
          title: 'Dashboard',
          tabBarIcon: ({ color, size }) => <Ionicons name="home" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="expenses"
        options={{
          title: 'Expenses',
          tabBarIcon: ({ color, size }) => <Ionicons name="trending-down" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="income"
        options={{
          title: 'Income',
          tabBarIcon: ({ color, size }) => <Ionicons name="trending-up" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="budget"
        options={{
          title: 'Budget',
          tabBarIcon: ({ color, size }) => <Ionicons name="pie-chart" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size }) => <Ionicons name="person" size={size} color={color} />,
        }}
      />
    </Tabs>
  );
}