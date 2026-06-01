//layout.tsx
import { Tabs } from 'expo-router';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { Platform } from 'react-native';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false, 
        tabBarActiveTintColor: '#0ea5e9',
        tabBarInactiveTintColor: '#94a3b8',
        tabBarStyle: {
          backgroundColor: '#ffffff',
          borderTopWidth: 1,
          borderTopColor: '#f1f5f9',
          height: Platform.OS === 'ios' ? 85 : 65,
          paddingBottom: Platform.OS === 'ios' ? 25 : 10,
          paddingTop: 10,
          elevation: 10,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: -2 },
          shadowOpacity: 0.05,
          shadowRadius: 4,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600',
          marginTop: 2,
        }
      }}
    >
      {/* 1. Dashboard */}
      <Tabs.Screen
        name="dashboard"
        options={{
          title: 'Dashboard',
          tabBarIcon: ({ color }) => (
            <MaterialCommunityIcons name="view-dashboard-outline" size={26} color={color} />
          ),
        }}
      />

      {/* 2. AI Assistant */}
      <Tabs.Screen
        name="chatbot"
        options={{
          title: 'AI Assistant',
          tabBarIcon: ({ color }) => (
            <Ionicons name="chatbubble-ellipses-outline" size={26} color={color} />
          ),
        }}
      />

      {/* 3. Results ✅ أضفناه */}
      <Tabs.Screen
        name="explore"
        options={{
          title: 'Results',
          tabBarIcon: ({ color }) => (
            <Ionicons name="flask-outline" size={26} color={color} />
          ),
        }}
      />

      {/* ملفات مخفية */}
      <Tabs.Screen name="index" options={{ href: null }} />
      <Tabs.Screen name="impact" options={{ href: null }} />
    </Tabs>
  );
}

// import React from 'react';
// import { Tabs } from 'expo-router';
// import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
// import { Platform } from 'react-native';

// export default function TabLayout() {
//   return (
//     <Tabs
//       screenOptions={{
//         // بنخفي الهيدر الافتراضي عشان إحنا عاملين Header مخصص وشيك في كل شاشة
//         headerShown: false, 
        
//         // ألوان الشريط مطابقة للديزاين بتاعك
//         tabBarActiveTintColor: '#0ea5e9', // أزرق لما تكوني دايسة عليه
//         tabBarInactiveTintColor: '#94a3b8', // رمادي لما يكون مش متفعل
        
//         // ستايل الشريط نفسه
//         tabBarStyle: {
//           backgroundColor: '#ffffff',
//           borderTopWidth: 1,
//           borderTopColor: '#f1f5f9',
//           height: Platform.OS === 'ios' ? 85 : 65, // عشان الآيفون بيبقى ليه مساحة تحت
//           paddingBottom: Platform.OS === 'ios' ? 25 : 10,
//           paddingTop: 10,
//           elevation: 10,
//           shadowColor: '#000',
//           shadowOffset: { width: 0, height: -2 },
//           shadowOpacity: 0.05,
//           shadowRadius: 4,
//         },
//         tabBarLabelStyle: {
//           fontSize: 12,
//           fontWeight: '600',
//           marginTop: 2,
//         }
//       }}
//     >
//       {/* 1. تاب الداشبورد */}
//       <Tabs.Screen
//         name="dashboard" // لازم يكون نفس اسم ملف الـ dashboard.tsx
//         options={{
//           title: 'Dashboard',
//           tabBarIcon: ({ color }) => (
//             <MaterialCommunityIcons name="view-dashboard-outline" size={26} color={color} />
//           ),
//         }}
//       />

//       {/* 2. تاب المساعد الذكي */}
//       <Tabs.Screen
//         name="chatbot" // لازم يكون نفس اسم ملف الـ chatbot.tsx
//         options={{
//           title: 'AI Assistant',
//           tabBarIcon: ({ color }) => (
//             <Ionicons name="chatbubble-ellipses-outline" size={26} color={color} />
//           ),
//         }}
//       />
      
//       {/* لو عندك ملفات تانية جوه فولدر tabs مش عايزاها تظهر كزرار تحت (زي ملف index لو كان موجود)، بتخفيها كده: */}
//       <Tabs.Screen
//         name="index"
//         options={{ href: null }}
//       />
//     </Tabs>
//   );
// }