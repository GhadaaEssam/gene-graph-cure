import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

// ضفنا isTransparent بـ false كافتراضي
export default function Header({ showMenu = true, isTransparent = false }) {
  const router = useRouter();

  const handleMenuPress = () => {
    Alert.alert(
      "تسجيل الخروج",
      "هل أنت متأكد أنك تريد تسجيل الخروج؟",
      [
        { text: "إلغاء", style: "cancel" },
        { text: "خروج", style: "destructive", onPress: () => router.replace('/login') }
      ]
    );
  };

  // لو شفاف، هنخلي الكلام أبيض والباك جراوند شفافة.. لو لأ هنخليه زي الديزاين العادي
  const bgColor = isTransparent ? 'transparent' : '#ffffff';
  const textColor = isTransparent ? '#ffffff' : '#0f172a';
  const iconColor = isTransparent ? '#ffffff' : '#0ea5e9';
  const borderBtm = isTransparent ? 0 : 1; // بنشيل الخط اللي تحت لو شفاف

  return (
    <View style={[styles.headerContainer, { backgroundColor: bgColor, borderBottomWidth: borderBtm }]}>
      <View style={{ flexDirection: 'row', alignItems: 'center' }}>
        <Ionicons name="git-network" size={28} color={iconColor} style={{ marginRight: 8 }} />
        <Text style={[styles.logoText, { color: textColor }]}>GeneGraphCure</Text>
      </View>
      
      {showMenu && (
        <TouchableOpacity onPress={handleMenuPress}>
          <Ionicons name="menu" size={30} color={textColor} />
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  headerContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomColor: '#f1f5f9',
    // شلنا الـ paddingHorizontal من هنا عشان نقدر نتحكم فيه من بره براحتنا
  },
  logoText: {
    fontSize: 20,
    fontWeight: '800',
  },
});