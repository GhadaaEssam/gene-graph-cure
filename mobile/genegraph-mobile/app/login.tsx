import React, { useState } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  TextInput, 
  TouchableOpacity, 
  SafeAreaView, 
  KeyboardAvoidingView, 
  Platform, 
  ScrollView 
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
// فوق خالص مع الـ imports ضيفي ده:
//import Header from '../components/Header';

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // الدالة دي اللي هنربطها بالـ FastAPI بعدين
  const handleLogin = () => {
    // بناءً على المكتوب في الديزاين (Demo: Enter any email...)
    // هننقل اليوزر على طول لصفحة الداشبورد
    router.push('/(tabs)/dashboard'); 
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView 
        style={{ flex: 1 }} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          
          {/* Header */}
          {/* <Header showMenu={false} /> */}
          <View style={styles.header}>
            <View style={{flexDirection: 'row', alignItems: 'center'}}>
              <Ionicons name="git-network" size={28} color="#0ea5e9" style={{marginRight: 8}} />
              <Text style={styles.logoText}>GeneGraphCure</Text>
            </View>
            <Ionicons name="menu" size={30} color="#0f172a" />
          </View>

          <View style={styles.mainContainer}>
            {/* GG Logo Box */}
            <View style={styles.logoBox}>
              <Text style={styles.logoBoxText}>GG</Text>
            </View>

            {/* Titles */}
            <Text style={styles.title}>Welcome Back</Text>
            <Text style={styles.subtitle}>Login to access GeneGraphCure</Text>

            {/* Login Card */}
            <View style={styles.card}>
              
              {/* Email Input */}
              <Text style={styles.inputLabel}>Email Address</Text>
              <View style={styles.inputContainer}>
                <Ionicons name="mail-outline" size={20} color="#94a3b8" style={styles.inputIcon} />
                <TextInput 
                  style={styles.input}
                  placeholder="researcher@example.com"
                  placeholderTextColor="#94a3b8"
                  keyboardType="email-address"
                  autoCapitalize="none"
                  value={email}
                  onChangeText={setEmail}
                />
              </View>

              {/* Password Input */}
              <Text style={styles.inputLabel}>Password</Text>
              <View style={styles.inputContainer}>
                <Ionicons name="lock-closed-outline" size={20} color="#94a3b8" style={styles.inputIcon} />
                <TextInput 
                  style={styles.input}
                  placeholder="Enter your password"
                  placeholderTextColor="#94a3b8"
                  secureTextEntry
                  value={password}
                  onChangeText={setPassword}
                />
              </View>

              {/* Forgot Password */}
              <TouchableOpacity style={styles.forgotPassword}>
                <Text style={styles.forgotPasswordText}>Forgot password?</Text>
              </TouchableOpacity>

              {/* Login Button */}
              <TouchableOpacity style={styles.loginButton} onPress={handleLogin}>
                <Text style={styles.loginButtonText}>Login</Text>
              </TouchableOpacity>

            </View>

            {/* Footer Text */}
            <View style={styles.footerContainer}>
              <Text style={styles.footerText}>Don't have an account? </Text>
              <TouchableOpacity>
                <Text style={styles.contactAdminText}>Contact Admin</Text>
              </TouchableOpacity>
            </View>

            {/* Demo Box */}
            <View style={styles.demoBox}>
              <Text style={styles.demoText}>
                <Text style={{fontWeight: 'bold'}}>Demo: </Text>
                Enter any email and password to login
              </Text>
            </View>

          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f8fafc', // لون الخلفية الفاتح جداً اللي في الديزاين
  },
  scrollContent: {
    flexGrow: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 15,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  logoText: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0f172a',
  },
  mainContainer: {
    flex: 1,
    paddingHorizontal: 24,
    alignItems: 'center',
    paddingTop: 40,
  },
  logoBox: {
    width: 60,
    height: 60,
    backgroundColor: '#0ea5e9',
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    shadowColor: '#0ea5e9',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 5,
  },
  logoBoxText: {
    color: '#ffffff',
    fontSize: 24,
    fontWeight: '900',
  },
  title: {
    fontSize: 26,
    fontWeight: '900',
    color: '#0f172a',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 15,
    color: '#64748b',
    marginBottom: 30,
  },
  card: {
    backgroundColor: '#ffffff',
    width: '100%',
    padding: 24,
    borderRadius: 20,
    shadowColor: '#94a3b8',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 3,
    marginBottom: 30,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#334155',
    marginBottom: 8,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 10,
    paddingHorizontal: 12,
    height: 50,
    marginBottom: 20,
    backgroundColor: '#ffffff',
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    fontSize: 15,
    color: '#0f172a',
  },
  forgotPassword: {
    alignSelf: 'flex-end',
    marginBottom: 24,
  },
  forgotPasswordText: {
    color: '#3b82f6',
    fontSize: 14,
    fontWeight: '600',
  },
  loginButton: {
    backgroundColor: '#06b6d4',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    shadowColor: '#06b6d4',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 4,
  },
  loginButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  footerContainer: {
    flexDirection: 'row',
    marginBottom: 30,
  },
  footerText: {
    color: '#64748b',
    fontSize: 14,
  },
  contactAdminText: {
    color: '#3b82f6',
    fontSize: 14,
    fontWeight: 'bold',
  },
  demoBox: {
    backgroundColor: '#f0fdfa',
    borderWidth: 1,
    borderColor: '#bae6fd',
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderRadius: 10,
    width: '100%',
    alignItems: 'center',
  },
  demoText: {
    color: '#334155',
    fontSize: 13,
  },
});