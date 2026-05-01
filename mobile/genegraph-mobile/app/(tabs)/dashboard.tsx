import React from 'react';
import { StyleSheet, Text, View, ScrollView, SafeAreaView, TouchableOpacity, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
// فوق خالص مع الـ imports:
import Header from '../../components/Header'; // (علامتين ../ عشان إحنا جوه فولدر tabs)



// داتا وهمية (Mock Data) لحد ما نربط مع الـ FastAPI Backend
const analyses = [
  { id: 'PT-2024-001', cancer: 'Liver Cancer', status: 'Resistant', drug: 'Sorafenib', confidence: 92, date: '2024-12-28' },
  { id: 'PT-2024-002', cancer: 'Melanoma', status: 'Sensitive', drug: 'Nivolumab', confidence: 89, date: '2024-12-27' },
  { id: 'PT-2024-003', cancer: 'Ovarian Cancer', status: 'Resistant', drug: 'Cisplatin', confidence: 85, date: '2024-12-26' },
  { id: 'PT-2024-004', cancer: 'Liver Cancer', status: 'Sensitive', drug: 'Doxorubicin', confidence: 91, date: '2024-12-25' },
];

export default function Dashboard() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        <Header />
        {/* Top Header Banner */}
        <View style={styles.topBanner}>
          <View style={styles.navbar}>
            <View style={{flexDirection: 'row', alignItems: 'center'}}>
            </View>
            
          </View>
          <Text style={styles.welcomeText}>Welcome, Dr. Smith</Text>
          <Text style={styles.overviewText}>Here's your research overview</Text>
        </View>

        <View style={styles.contentPadding}>
          {/* Quick Stats */}
          <Text style={styles.sectionTitle}>Quick Stats</Text>
          <View style={styles.statsRow}>
            <View style={[styles.statCard, { backgroundColor: '#3b82f6' }]}>
              <Ionicons name="pulse-outline" size={26} color="#ffffff" style={styles.statIcon} />
              <Text style={styles.statNumber}>24</Text>
              <Text style={styles.statLabel}>Total{'\n'}Analyses</Text>
            </View>
            <View style={[styles.statCard, { backgroundColor: '#14b8a6' }]}>
              <Ionicons name="trending-up" size={26} color="#ffffff" style={styles.statIcon} />
              <Text style={styles.statNumber}>87%</Text>
              <Text style={styles.statLabel}>Avg{'\n'}Accuracy</Text>
            </View>
            <View style={[styles.statCard, { backgroundColor: '#06b6d4' }]}>
              <Ionicons name="document-text-outline" size={26} color="#ffffff" style={styles.statIcon} />
              <Text style={styles.statNumber}>156</Text>
              <Text style={styles.statLabel}>Reports{'\n'}Generated</Text>
            </View>
          </View>

          {/* Analysis History */}
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Analysis History</Text>
            <TouchableOpacity>
              <Text style={styles.viewAllText}>View All</Text>
            </TouchableOpacity>
          </View>

          {/* عملنا Map عشان نعرض كل التحليلات من الـ Data فوق */}
          {analyses.map((item, index) => (
            <TouchableOpacity 
              key={index} 
              style={styles.historyCard}
              // هنا الربط بالـ Dynamic Route بتاع النتيجة المحددة
              onPress={() => router.push(`/results/${item.id}`)} 
            >
              <View style={styles.historyHeader}>
                <View>
                  <Text style={styles.patientId}>{item.id}</Text>
                  <Text style={styles.cancerType}>{item.cancer}</Text>
                </View>
                <View style={[
                  styles.statusBadge, 
                  { backgroundColor: item.status === 'Resistant' ? '#ffe4e6' : '#dcfce7' }
                ]}>
                  <Text style={[
                    styles.statusText, 
                    { color: item.status === 'Resistant' ? '#e11d48' : '#16a34a' }
                  ]}>
                    {item.status}
                  </Text>
                </View>
              </View>

              <View style={styles.historyRow}>
                <Text style={styles.historyLabel}>Drug:</Text>
                <Text style={styles.historyValueBold}>{item.drug}</Text>
              </View>
              <View style={styles.historyRow}>
                <Text style={styles.historyLabel}>Confidence:</Text>
                <Text style={styles.historyValueBold}>{item.confidence}%</Text>
              </View>
              <View style={styles.historyRow}>
                <Text style={styles.historyLabel}>Date:</Text>
                <Text style={styles.historyValue}>
                  <Ionicons name="time-outline" size={14}/> {item.date}
                </Text>
              </View>

              {/* Progress Bar */}
              <View style={styles.progressBarBackground}>
                <View style={[
                  styles.progressBarFill, 
                  { width: `${item.confidence}%`, backgroundColor: '#0ea5e9' }
                ]} />
              </View>
            </TouchableOpacity>
          ))}

          {/* Performance Summary */}
          <Text style={styles.sectionTitle}>Performance Summary</Text>
          
          {/* Prediction Distribution */}
          <View style={styles.summaryCard}>
            <Text style={styles.summaryTitle}>Prediction Distribution</Text>
            
            <View style={styles.distRow}>
              <Text style={styles.distLabel}>Resistant</Text>
              <Text style={[styles.distValue, { color: '#e11d48' }]}>45%</Text>
            </View>
            <View style={styles.progressBarBackground}>
              <View style={[styles.progressBarFill, { width: '45%', backgroundColor: '#e11d48' }]} />
            </View>

            <View style={[styles.distRow, { marginTop: 15 }]}>
              <Text style={styles.distLabel}>Sensitive</Text>
              <Text style={[styles.distValue, { color: '#16a34a' }]}>55%</Text>
            </View>
            <View style={styles.progressBarBackground}>
              <View style={[styles.progressBarFill, { width: '55%', backgroundColor: '#16a34a' }]} />
            </View>
          </View>

          {/* Cancer Type Distribution */}
          <View style={styles.summaryCard}>
            <Text style={styles.summaryTitle}>Cancer Type Distribution</Text>
            
            <View style={styles.distRow}>
              <Text style={styles.distLabel}>Liver Cancer</Text>
              <Text style={styles.historyValueBold}>42%</Text>
            </View>
            <View style={styles.progressBarBackground}>
              <View style={[styles.progressBarFill, { width: '42%', backgroundColor: '#3b82f6' }]} />
            </View>

            <View style={[styles.distRow, { marginTop: 15 }]}>
              <Text style={styles.distLabel}>Ovarian Cancer</Text>
              <Text style={styles.historyValueBold}>33%</Text>
            </View>
            <View style={styles.progressBarBackground}>
              <View style={[styles.progressBarFill, { width: '33%', backgroundColor: '#14b8a6' }]} />
            </View>

            <View style={[styles.distRow, { marginTop: 15 }]}>
              <Text style={styles.distLabel}>Melanoma</Text>
              <Text style={styles.historyValueBold}>25%</Text>
            </View>
            <View style={styles.progressBarBackground}>
              <View style={[styles.progressBarFill, { width: '25%', backgroundColor: '#06b6d4' }]} />
            </View>
          </View>

        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  scrollContent: {
    paddingBottom: 40,
  },
  topBanner: {
    backgroundColor: '#0ea5e9', // لون أزرق للبانر
    paddingTop: Platform.OS === 'ios' ? 50 : 40,
    paddingBottom: 30,
    paddingHorizontal: 24,
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
  },
  navbar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 25,
  },
  logoTextWhite: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  welcomeText: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 5,
  },
  overviewText: {
    fontSize: 15,
    color: '#e0f2fe',
  },
  contentPadding: {
    paddingHorizontal: 24,
    marginTop: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#0f172a',
    marginBottom: 15,
    marginTop: 10,
  },
  viewAllText: {
    color: '#3b82f6',
    fontWeight: 'bold',
    fontSize: 14,
    marginBottom: 15,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 25,
  },
  statCard: {
    width: '31%',
    padding: 15,
    borderRadius: 16,
    alignItems: 'flex-start',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statIcon: {
    marginBottom: 10,
  },
  statNumber: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#ffffff',
    opacity: 0.9,
  },
  historyCard: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 16,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#f1f5f9',
    shadowColor: '#94a3b8',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 2,
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  patientId: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#0f172a',
  },
  cancerType: {
    fontSize: 13,
    color: '#64748b',
    marginTop: 2,
  },
  statusBadge: {
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 20,
  },
  statusText: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  historyRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  historyLabel: {
    fontSize: 14,
    color: '#64748b',
  },
  historyValue: {
    fontSize: 14,
    color: '#334155',
  },
  historyValueBold: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#0f172a',
  },
  progressBarBackground: {
    height: 6,
    backgroundColor: '#e2e8f0',
    borderRadius: 3,
    marginTop: 10,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 3,
  },
  summaryCard: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 16,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#f1f5f9',
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#0f172a',
    marginBottom: 20,
  },
  distRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  distLabel: {
    fontSize: 14,
    color: '#475569',
  },
  distValue: {
    fontSize: 14,
    fontWeight: 'bold',
  },
});