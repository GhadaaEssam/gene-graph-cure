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
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

// الأسئلة المقترحة (Suggested Questions)
const suggestions = [
  "Why is this patient resistant to Sorafenib?",
  "Which genes are involved?",
  "Explain the pathway alterations",
  "Compare Regorafenib vs Sorafenib"
];

export default function Chatbot() {
  const router = useRouter();
  const [message, setMessage] = useState('');

  // دالة الإرسال اللي هتربطوها بالـ LLM API بعدين
  const handleSend = () => {
    if (message.trim() === '') return;
    console.log("Sending message to LLM:", message);
    // هنا المفروض نبعت الـ Request للـ Backend
    setMessage('');
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        style={{ flex: 1 }} 
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        
        {/* Header (نفس اللي في كل الشاشات) */}
        <View style={styles.header}>
          <View style={{flexDirection: 'row', alignItems: 'center'}}>
            <TouchableOpacity onPress={() => router.back()} style={{marginRight: 10}}>
              <Ionicons name="arrow-back" size={24} color="#0f172a" />
            </TouchableOpacity>
            <Ionicons name="git-network" size={24} color="#0ea5e9" style={{marginRight: 8}} />
            <Text style={styles.logoText}>GeneGraphCure</Text>
          </View>
          <Ionicons name="menu" size={30} color="#0f172a" />
        </View>

        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          
          {/* Top Blue Banner */}
          <View style={styles.topBanner}>
            <View style={styles.bannerIconBox}>
              <View style={styles.bannerIconInner} />
            </View>
            <View>
              <Text style={styles.bannerTitle}>AI Results Assistant</Text>
              <Text style={styles.bannerSub}>Ask me anything about the analysis</Text>
            </View>
          </View>

          {/* Welcome Area */}
          <View style={styles.welcomeArea}>
            <View style={styles.robotIconContainer}>
              <MaterialCommunityIcons name="robot-outline" size={36} color="#0ea5e9" />
            </View>
            
            <Text style={styles.welcomeTitle}>Welcome to AI Assistant</Text>
            <Text style={styles.welcomeText}>
              I can explain the resistance prediction, involved genes, pathways, and alternative treatment options.
            </Text>

            <Text style={styles.tryAskingText}>Try asking:</Text>

            {/* Suggestions List */}
            {suggestions.map((item, index) => (
              <TouchableOpacity 
                key={index} 
                style={styles.suggestionCard}
                onPress={() => setMessage(item)} // لما يضغط على سؤال، بيكتبه في الـ Input تحت
              >
                <Text style={styles.suggestionText}>{item}</Text>
              </TouchableOpacity>
            ))}
          </View>

        </ScrollView>

        {/* Bottom Chat Input */}
        <View style={styles.inputArea}>
          <View style={styles.inputContainer}>
            <TextInput 
              style={styles.textInput}
              placeholder="Ask about the analysis..."
              placeholderTextColor="#94a3b8"
              value={message}
              onChangeText={setMessage}
              multiline
            />
          </View>
          <TouchableOpacity 
            style={[styles.sendButton, { opacity: message.trim() ? 1 : 0.6 }]} 
            onPress={handleSend}
            disabled={!message.trim()}
          >
            <Ionicons name="send" size={20} color="#ffffff" style={{ marginLeft: 3 }} />
          </TouchableOpacity>
        </View>

      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  scrollContent: {
    paddingBottom: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  logoText: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0f172a',
  },
  topBanner: {
    backgroundColor: '#0ea5e9', // لون أزرق مطابق للديزاين
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 25,
    paddingHorizontal: 24,
  },
  bannerIconBox: {
    width: 44,
    height: 44,
    backgroundColor: '#ffffff',
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  bannerIconInner: {
    width: 20,
    height: 20,
    backgroundColor: '#e0f2fe',
    borderRadius: 10,
  },
  bannerTitle: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  bannerSub: {
    color: '#e0f2fe',
    fontSize: 13,
  },
  welcomeArea: {
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingTop: 40,
  },
  robotIconContainer: {
    width: 70,
    height: 70,
    backgroundColor: '#e0f2fe',
    borderRadius: 35,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  welcomeTitle: {
    fontSize: 22,
    fontWeight: '900',
    color: '#0f172a',
    marginBottom: 10,
  },
  welcomeText: {
    textAlign: 'center',
    fontSize: 14,
    color: '#64748b',
    lineHeight: 22,
    marginBottom: 30,
    paddingHorizontal: 10,
  },
  tryAskingText: {
    fontSize: 14,
    color: '#64748b',
    marginBottom: 15,
  },
  suggestionCard: {
    width: '100%',
    paddingVertical: 16,
    paddingHorizontal: 20,
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#94a3b8',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 1,
  },
  suggestionText: {
    fontSize: 15,
    color: '#334155',
    fontWeight: '500',
  },
  inputArea: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#f8fafc',
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
  },
  inputContainer: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#cbd5e1',
    borderRadius: 25,
    minHeight: 50,
    maxHeight: 120,
    justifyContent: 'center',
    paddingHorizontal: 20,
    paddingVertical: 10,
    marginRight: 10,
  },
  textInput: {
    fontSize: 15,
    color: '#0f172a',
    maxHeight: 100,
  },
  sendButton: {
    width: 50,
    height: 50,
    backgroundColor: '#67e8f9', // اللون اللبني الفاتح اللي في الديزاين
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#06b6d4',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 2,
  },
});