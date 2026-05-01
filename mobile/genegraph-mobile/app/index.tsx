import React from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';

// Components صغيرة عشان ننظم الكود
const ResearchItem = ({ title }) => (
  <View style={styles.researchItem}>
    <View style={styles.researchItemIndicator} />
    <Text style={styles.researchItemText}>{title}</Text>
  </View>
);

const TrustItem = ({ icon, title, desc }) => (
  <View style={styles.trustItem}>
    <Ionicons name={icon} size={24} color="#0ea5e9" style={styles.trustIcon} />
    <View>
      <Text style={styles.trustTitle}>{title}</Text>
      <Text style={styles.trustDesc}>{desc}</Text>
    </View>
  </View>
);

const WhoCard = ({ icon, title, desc }) => (
  <View style={styles.whoCard}>
    <Ionicons name={icon} size={32} color="#3b82f6" style={styles.whoIcon} />
    <View>
      <Text style={styles.whoTitle}>{title}</Text>
      <Text style={styles.whoDesc}>{desc}</Text>
    </View>
  </View>
);

export default function LandingPage() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        
        {/* Header */}
        <View style={styles.header}>
          <View style={{flexDirection: 'row', alignItems: 'center'}}>
            <Ionicons name="git-network" size={28} color="#0ea5e9" style={{marginRight: 8}} />
            <Text style={styles.logoText}>GeneGraphCure</Text>
          </View>
          <Ionicons name="menu" size={30} color="#0f172a" />
        </View>

        {/* Hero Section */}
        <View style={styles.heroSection}>
          <Text style={styles.mainTitle}>Explaining Cancer Drug Resistance</Text>
          <Text style={styles.subTitle}>
            AI-powered insights for chemotherapy, targeted therapy, and immunotherapy.
          </Text>
          <TouchableOpacity style={styles.primaryButton}>
            <Text style={styles.primaryButtonText}>Get Started</Text>
          </TouchableOpacity>
        </View>

        {/* Info Box */}
        <View style={styles.infoBox}>
          <Text style={styles.infoText}>
            Modern cancer treatment relies on multiple therapeutic strategies, including{' '}
            <Text style={styles.linkText}>chemotherapy</Text>,{' '}
            <Text style={styles.linkText}>targeted therapy</Text>, and{' '}
            <Text style={styles.linkText}>immunotherapy</Text>. While these treatments can be highly effective, patient responses vary widely depending on tumor biology and molecular context.
          </Text>
        </View>

        {/* Key Platform Features */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Key Platform Features</Text>
          <View style={styles.featuresGrid}>
            <View style={styles.featureCard}>
              <MaterialCommunityIcons name="brain" size={32} color="#2563eb" style={styles.iconMargin} />
              <Text style={styles.featureTitle}>Drug Resistance Prediction</Text>
              <Text style={styles.featureDesc}>Advanced prediction models</Text>
            </View>
            <View style={styles.featureCard}>
              <Ionicons name="trending-up" size={32} color="#0d9488" style={styles.iconMargin} />
              <Text style={styles.featureTitle}>Multi-Omics Integration</Text>
              <Text style={styles.featureDesc}>Comprehensive data analysis</Text>
            </View>
            <View style={styles.featureCard}>
              <Ionicons name="bulb-outline" size={32} color="#2563eb" style={styles.iconMargin} />
              <Text style={styles.featureTitle}>Explainable AI</Text>
              <Text style={styles.featureDesc}>Transparent insights</Text>
            </View>
            <View style={styles.featureCard}>
              <Ionicons name="bar-chart-outline" size={32} color="#0d9488" style={styles.iconMargin} />
              <Text style={styles.featureTitle}>Interactive Visualizations</Text>
              <Text style={styles.featureDesc}>Real-time data exploration</Text>
            </View>
             <View style={styles.featureCard}>
              <Ionicons name="flask-outline" size={32} color="#2563eb" style={styles.iconMargin} />
              <Text style={styles.featureTitle}>Alternative Drug Rec.</Text>
              <Text style={styles.featureDesc}>Personalized treatment options</Text>
            </View>
             <View style={styles.featureCard}>
              <Ionicons name="chatbubble-ellipses-outline" size={32} color="#0d9488" style={styles.iconMargin} />
              <Text style={styles.featureTitle}>AI Results Assistant</Text>
              <Text style={styles.featureDesc}>Natural language explanations</Text>
            </View>
          </View>
        </View>

        {/* Built on Scientific Research */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Built on Scientific Research</Text>
          <ResearchItem title="Traditional ML approaches" />
          <ResearchItem title="GNN-based models" />
          <ResearchItem title="Pathway-aware learning" />
          <ResearchItem title="GC-PGE contribution" />
          <TouchableOpacity style={styles.outlineButton}>
            <Text style={styles.outlineButtonText}>View Literature Survey</Text>
          </TouchableOpacity>
        </View>

        {/* --- الأجزاء الجديدة اللي ضفناها --- */}
        
        {/* Trust & Ethics Section */}
        <View style={styles.trustContainer}>
          <Text style={styles.sectionTitle}>Trust & Ethics</Text>
          <TrustItem icon="shield-outline" title="Research-use focused" desc="Designed for scientific exploration" />
          <TrustItem icon="medkit-outline" title="No clinical diagnosis" desc="Not a replacement for medical advice" />
          <TrustItem icon="lock-closed-outline" title="Data privacy aware" desc="Secure and compliant" />
          <TrustItem icon="eye-outline" title="Explainable by design" desc="Transparent AI reasoning" />
        </View>

        {/* Who Is It For Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Who Is It For?</Text>
          <WhoCard icon="people-outline" title="Clinicians" desc="Personalized insights" />
          <WhoCard icon="flask-outline" title="Researchers" desc="Accelerated discovery" />
          <WhoCard icon="business-outline" title="Healthcare Institutions" desc="Scalable analytics" />
        </View>

        {/* System Integration Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Integration & Accessibility</Text>
          
          <View style={styles.integrationCard}>
            <View style={styles.integrationHeader}>
              <Ionicons name="server-outline" size={24} color="#3b82f6" style={{marginRight: 10}} />
              <Text style={styles.integrationTitle}>Odoo ERP Integration</Text>
            </View>
            <Text style={styles.bulletPoint}>• Patient management</Text>
            <Text style={styles.bulletPoint}>• Clinical dashboards</Text>
            <Text style={styles.bulletPoint}>• Automated reporting</Text>
          </View>

          <View style={styles.integrationCard}>
            <View style={styles.integrationHeader}>
              <Ionicons name="phone-portrait-outline" size={24} color="#0d9488" style={{marginRight: 10}} />
              <Text style={styles.integrationTitle}>Mobile Application</Text>
            </View>
            <Text style={styles.bulletPoint}>• iOS & Android support</Text>
            <Text style={styles.bulletPoint}>• Secure clinician access</Text>
          </View>
        </View>

        {/* --- نهاية الأجزاء الجديدة --- */}

        {/* Bottom CTA */}
        <View style={styles.bottomCta}>
          <Text style={styles.ctaTitle}>Ready to Get Started?</Text>
          <Text style={styles.ctaSub}>Join the growing community advancing precision oncology.</Text>
          
          <TouchableOpacity 
            style={styles.loginButton} 
            onPress={() => router.push('/login')}
          >
            <Text style={styles.loginButtonText}>Login Now</Text>
          </TouchableOpacity>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  // ... (نفس الستايلز القديمة بالظبط)
  container: { flex: 1, backgroundColor: '#ffffff' },
  scrollContent: { padding: 24, paddingTop: Platform.OS === 'android' ? 40 : 20, paddingBottom: 40 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 35 },
  logoText: { fontSize: 20, fontWeight: '800', color: '#0f172a' },
  heroSection: { marginBottom: 35 },
  mainTitle: { fontSize: 34, fontWeight: '900', color: '#0f172a', marginBottom: 12, lineHeight: 40 },
  subTitle: { fontSize: 16, color: '#64748b', marginBottom: 24, lineHeight: 24 },
  primaryButton: { backgroundColor: '#06b6d4', paddingVertical: 14, paddingHorizontal: 28, borderRadius: 8, alignSelf: 'flex-start', shadowColor: '#06b6d4', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.3, shadowRadius: 5, elevation: 4 },
  primaryButtonText: { color: '#ffffff', fontWeight: 'bold', fontSize: 16 },
  infoBox: { backgroundColor: '#f0fdfa', padding: 20, borderRadius: 16, marginBottom: 40 },
  infoText: { fontSize: 15, color: '#334155', lineHeight: 24 },
  linkText: { color: '#2563eb', fontWeight: '600' },
  section: { marginBottom: 40 },
  sectionTitle: { fontSize: 22, fontWeight: '900', color: '#0f172a', marginBottom: 20 },
  featuresGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  featureCard: { width: '48%', backgroundColor: '#ffffff', padding: 18, borderRadius: 16, marginBottom: 16, borderWidth: 1, borderColor: '#f1f5f9', shadowColor: '#94a3b8', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 8, elevation: 2 },
  iconMargin: { marginBottom: 12 },
  featureTitle: { fontSize: 14, fontWeight: 'bold', color: '#0f172a', marginBottom: 6 },
  featureDesc: { fontSize: 12, color: '#64748b', lineHeight: 18 },
  researchItem: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#f8fafc', borderRadius: 8, marginBottom: 12, overflow: 'hidden' },
  researchItemIndicator: { width: 4, height: '100%', backgroundColor: '#3b82f6', position: 'absolute', left: 0 },
  researchItemText: { paddingVertical: 16, paddingHorizontal: 16, fontSize: 15, color: '#334155' },
  outlineButton: { borderWidth: 1.5, borderColor: '#3b82f6', borderRadius: 8, paddingVertical: 14, alignItems: 'center', marginTop: 10 },
  outlineButtonText: { color: '#3b82f6', fontWeight: 'bold', fontSize: 16 },
  
  // --- ستايلز الأجزاء الجديدة ---
  trustContainer: { backgroundColor: '#f0fdfa', padding: 24, borderRadius: 16, marginBottom: 40 },
  trustItem: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  trustIcon: { marginRight: 15 },
  trustTitle: { fontSize: 16, fontWeight: 'bold', color: '#0f172a', marginBottom: 4 },
  trustDesc: { fontSize: 14, color: '#64748b' },
  
  whoCard: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#f8fafc', padding: 20, borderRadius: 12, marginBottom: 15, borderWidth: 1, borderColor: '#e2e8f0' },
  whoIcon: { marginRight: 20 },
  whoTitle: { fontSize: 18, fontWeight: 'bold', color: '#0f172a', marginBottom: 4 },
  whoDesc: { fontSize: 14, color: '#64748b' },

  integrationCard: { backgroundColor: '#ffffff', padding: 24, borderRadius: 16, marginBottom: 16, borderWidth: 1, borderColor: '#f1f5f9', shadowColor: '#94a3b8', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 8, elevation: 2 },
  integrationHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 15 },
  integrationTitle: { fontSize: 18, fontWeight: 'bold', color: '#0f172a' },
  bulletPoint: { fontSize: 14, color: '#475569', marginBottom: 8, marginLeft: 34 },
  // -----------------------------

  bottomCta: { backgroundColor: '#0ea5e9', padding: 30, borderRadius: 16, alignItems: 'center' },
  ctaTitle: { color: '#ffffff', fontSize: 24, fontWeight: '900', marginBottom: 10 },
  ctaSub: { color: '#e0f2fe', fontSize: 15, textAlign: 'center', marginBottom: 24, lineHeight: 22 },
  loginButton: { backgroundColor: '#ffffff', paddingVertical: 14, paddingHorizontal: 30, borderRadius: 8, width: '100%', alignItems: 'center', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 },
  loginButtonText: { color: '#0ea5e9', fontWeight: 'bold', fontSize: 16 },
});