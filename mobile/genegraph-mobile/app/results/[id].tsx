import React from 'react';
import { StyleSheet, Text, View, ScrollView, SafeAreaView, TouchableOpacity, Platform } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';

// داتا وهمية للأدوية البديلة
const alternativeDrugs = [
  { name: 'Regorafenib', type: 'Multi-kinase inhibitor', confidence: 88, color: '#3b82f6' },
  { name: 'Lenvatinib', type: 'VEGFR inhibitor', confidence: 85, color: '#14b8a6' },
  { name: 'Cabozantinib', type: 'Tyrosine kinase inhibitor', confidence: 82, color: '#06b6d4' },
  { name: 'Atezolizumab', type: 'PD-L1 inhibitor', confidence: 79, color: '#60a5fa' },
  { name: 'Bevacizumab', type: 'VEGF inhibitor', confidence: 76, color: '#0ea5e9' },
];

// داتا وهمية لأسئلة الذكاء الاصطناعي
const aiQuestions = [
  "Why is this patient resistant to Sorafenib?",
  "Which genes are involved in the resistance?",
  "What pathways are affected?",
  "How do alternative drugs work differently?",
  "What is the evidence for Regorafenib?"
];

export default function ResultDetails() {
  const router = useRouter();
  // السطر ده بيجيب الـ ID من اللينك (مثلاً PT-2024-001)
  const { id } = useLocalSearchParams(); 

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        
        {/* Header */}
        <View style={styles.header}>
          <View style={{flexDirection: 'row', alignItems: 'center'}}>
            <TouchableOpacity onPress={() => router.back()} style={{marginRight: 10}}>
              <Ionicons name="arrow-back" size={24} color="#0f172a" />
            </TouchableOpacity>
            <Ionicons name="git-network" size={24} color="#0ea5e9" style={{marginRight: 8}} />
            <Text style={styles.logoText}>GeneGraphCure</Text>
          </View>
          <Ionicons name="menu" size={28} color="#0f172a" />
        </View>

        {/* Title Section */}
        <View style={styles.titleSection}>
          <View style={styles.titleRow}>
            <Text style={styles.mainTitle}>Analysis Results</Text>
            <Text style={styles.patientId}>{id || 'PT-2024-001'}</Text>
          </View>
          <Text style={styles.subtitle}>Liver Cancer • Sorafenib • Dec 28, 2024</Text>
        </View>

        {/* Alert Card (RESISTANT) */}
        <View style={styles.alertCard}>
          <View style={styles.alertHeader}>
            <Ionicons name="alert-circle" size={32} color="#e11d48" style={{marginRight: 10}} />
            <View>
              <Text style={styles.alertTitle}>RESISTANT</Text>
              <Text style={styles.alertSub}>Patient likely resistant to Sorafenib</Text>
            </View>
          </View>
          
          <View style={styles.confidenceBox}>
            <View style={styles.confidenceRow}>
              <Text style={styles.confidenceLabel}>Confidence Score</Text>
              <Text style={styles.confidenceValue}>92%</Text>
            </View>
            <View style={styles.progressBgAlert}>
              <View style={[styles.progressFillAlert, { width: '92%' }]} />
            </View>
          </View>
        </View>

        {/* Suggested Alternative Drugs */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="link-outline" size={20} color="#0f172a" style={{marginRight: 8}} />
            <Text style={styles.sectionTitle}>Suggested Alternative Drugs</Text>
          </View>

          {alternativeDrugs.map((drug, index) => (
            <View key={index} style={[styles.drugCard, { backgroundColor: drug.color }]}>
              <View style={styles.drugHeader}>
                <View>
                  <Text style={styles.drugName}>{drug.name}</Text>
                  <Text style={styles.drugType}>{drug.type}</Text>
                </View>
                <View style={styles.drugIconBox} />
              </View>
              
              <Text style={styles.drugConfidenceText}>
                <Ionicons name="trending-up" size={14} color="#ffffff" /> {drug.confidence}% Confidence
              </Text>
              <View style={styles.progressBgDrug}>
                <View style={[styles.progressFillDrug, { width: `${drug.confidence}%` }]} />
              </View>
            </View>
          ))}
        </View>

        {/* Ask the AI Assistant */}
        <View style={styles.aiSection}>
          <View style={styles.aiHeaderRow}>
            <Ionicons name="chatbubble-ellipses-outline" size={20} color="#0f172a" style={{marginRight: 8}} />
            <Text style={styles.aiTitle}>Ask the AI Assistant</Text>
          </View>
          <Text style={styles.aiSubtitle}>Tap a question to get detailed explanations:</Text>

          {aiQuestions.map((q, index) => (
            <TouchableOpacity key={index} style={styles.questionCard}>
              <Text style={styles.questionText}>{q}</Text>
              <Ionicons name="arrow-forward" size={18} color="#3b82f6" />
            </TouchableOpacity>
          ))}

          <TouchableOpacity 
            style={styles.chatButton}
            onPress={() => router.push('/(tabs)/chatbot')}
          >
            <Text style={styles.chatButtonText}>Open Chat Assistant</Text>
          </TouchableOpacity>
        </View>

        {/* Key Findings */}
        <View style={styles.findingsSection}>
          <Text style={styles.sectionTitle}>Key Findings</Text>
          <View style={styles.findingCard}>
            
            <View style={styles.bulletRow}>
              <View style={[styles.bulletDot, { borderColor: '#bfdbfe' }]}>
                <View style={[styles.innerDot, { backgroundColor: '#3b82f6' }]} />
              </View>
              <Text style={styles.bulletText}>
                <Text style={{fontWeight: 'bold'}}>VEGFR2 pathway </Text>shows significant alteration
              </Text>
            </View>

            <View style={styles.bulletRow}>
              <View style={[styles.bulletDot, { borderColor: '#bbf7d0' }]}>
                <View style={[styles.innerDot, { backgroundColor: '#10b981' }]} />
              </View>
              <Text style={styles.bulletText}>
                <Text style={{fontWeight: 'bold'}}>RAF/MEK/ERK signaling </Text>pathway upregulated
              </Text>
            </View>

            <View style={styles.bulletRow}>
              <View style={[styles.bulletDot, { borderColor: '#bfdbfe' }]}>
                <View style={[styles.innerDot, { backgroundColor: '#3b82f6' }]} />
              </View>
              <Text style={styles.bulletText}>
                <Text style={{fontWeight: 'bold'}}>BRAF mutation </Text>detected in tumor sample
              </Text>
            </View>

          </View>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#ffffff' },
  scrollContent: { paddingBottom: 40 },
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: 24, paddingTop: Platform.OS === 'android' ? 40 : 20, paddingBottom: 15,
    borderBottomWidth: 1, borderBottomColor: '#f1f5f9',
  },
  logoText: { fontSize: 18, fontWeight: 'bold', color: '#0f172a' },
  titleSection: { paddingHorizontal: 24, marginTop: 25, marginBottom: 20 },
  titleRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 5 },
  mainTitle: { fontSize: 22, fontWeight: '900', color: '#0f172a' },
  patientId: { fontSize: 14, color: '#64748b' },
  subtitle: { fontSize: 14, color: '#64748b' },
  
  alertCard: {
    marginHorizontal: 24, backgroundColor: '#ffe4e6', borderRadius: 16, padding: 20, marginBottom: 30,
    borderWidth: 1, borderColor: '#fecdd3',
  },
  alertHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 15 },
  alertTitle: { fontSize: 18, fontWeight: '900', color: '#e11d48', marginBottom: 2 },
  alertSub: { fontSize: 13, color: '#be123c' },
  confidenceBox: { backgroundColor: '#ffffff', borderRadius: 12, padding: 15 },
  confidenceRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 10 },
  confidenceLabel: { fontSize: 13, fontWeight: 'bold', color: '#881337' },
  confidenceValue: { fontSize: 18, fontWeight: '900', color: '#e11d48' },
  progressBgAlert: { height: 8, backgroundColor: '#fecdd3', borderRadius: 4 },
  progressFillAlert: { height: '100%', backgroundColor: '#e11d48', borderRadius: 4 },

  section: { paddingHorizontal: 24, marginBottom: 30 },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 15 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#0f172a' },
  
  drugCard: { padding: 20, borderRadius: 16, marginBottom: 12 },
  drugHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 15 },
  drugName: { fontSize: 18, fontWeight: 'bold', color: '#ffffff', marginBottom: 2 },
  drugType: { fontSize: 13, color: '#ffffff', opacity: 0.9 },
  drugIconBox: { width: 32, height: 20, backgroundColor: '#ffffff', borderRadius: 10, opacity: 0.9 },
  drugConfidenceText: { color: '#ffffff', fontSize: 13, fontWeight: 'bold', marginBottom: 8 },
  progressBgDrug: { height: 6, backgroundColor: 'rgba(255,255,255,0.3)', borderRadius: 3 },
  progressFillDrug: { height: '100%', backgroundColor: '#ffffff', borderRadius: 3 },

  aiSection: {
    marginHorizontal: 24, backgroundColor: '#f0fdfa', padding: 20, borderRadius: 16, marginBottom: 30,
    borderWidth: 1, borderColor: '#ccfbf1'
  },
  aiHeaderRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  aiTitle: { fontSize: 16, fontWeight: 'bold', color: '#0f172a' },
  aiSubtitle: { fontSize: 13, color: '#475569', marginBottom: 15 },
  questionCard: {
    backgroundColor: '#ffffff', padding: 15, borderRadius: 10, marginBottom: 10,
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    borderWidth: 1, borderColor: '#e2e8f0'
  },
  questionText: { fontSize: 13, color: '#0f172a', flex: 1, paddingRight: 10 },
  chatButton: {
    backgroundColor: '#06b6d4', paddingVertical: 14, borderRadius: 10, alignItems: 'center', marginTop: 10,
  },
  chatButtonText: { color: '#ffffff', fontWeight: 'bold', fontSize: 15 },

  findingsSection: { paddingHorizontal: 24, marginBottom: 40 },
  findingCard: {
    backgroundColor: '#ffffff', padding: 20, borderRadius: 16, marginTop: 15,
    borderWidth: 1, borderColor: '#f1f5f9', shadowColor: '#94a3b8', shadowOffset: {width: 0, height: 2}, shadowOpacity: 0.1, shadowRadius: 8, elevation: 2
  },
  bulletRow: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 15 },
  bulletDot: { width: 16, height: 16, borderRadius: 8, borderWidth: 2, justifyContent: 'center', alignItems: 'center', marginRight: 10, marginTop: 2 },
  innerDot: { width: 6, height: 6, borderRadius: 3 },
  bulletText: { fontSize: 14, color: '#334155', flex: 1, lineHeight: 20 },
});