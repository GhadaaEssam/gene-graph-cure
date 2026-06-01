//explore.tsx

import React, { useEffect, useState, useCallback } from 'react';
import {
  StyleSheet, Text, View, ScrollView, SafeAreaView,
  TouchableOpacity, ActivityIndicator, Alert, RefreshControl
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import api from '../../services/api';

interface AnalysisItem {
  id: string;
  analysis_code: string;
  drug: string;
  prediction: string;
  confidence: number;
  date: string;
  cancer_type: string;
}

export default function Results() {
  const router = useRouter();
  const [analyses, setAnalyses] = useState<AnalysisItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeFilter, setActiveFilter] = useState<'All' | 'Resistant' | 'Sensitive'>('All');

  const fetchData = async () => {
    try {
      const res = await api.get('/dashboard/all');
      setAnalyses(res.data);
    } catch (err: any) {
      if (err?.response?.status === 401) {
        router.replace('/login');
      } else {
        Alert.alert("Error", "Failed to load analyses");
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { fetchData(); }, []);
  const onRefresh = useCallback(() => { setRefreshing(true); fetchData(); }, []);

  const filtered = activeFilter === 'All'
    ? analyses
    : analyses.filter(a => a.prediction === activeFilter);

  if (loading) {
    return (
      <View style={styles.loader}>
        <ActivityIndicator size="large" color="#0ea5e9" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>

      {/* Header */}
      <View style={styles.header}>
        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          <Ionicons name="git-network" size={24} color="#0ea5e9" style={{ marginRight: 8 }} />
          <Text style={styles.logoText}>GeneGraphCure</Text>
        </View>
        <Ionicons name="menu" size={30} color="#0f172a" />
      </View>

      {/* Banner */}
      <View style={styles.banner}>
        <Text style={styles.bannerTitle}>Analysis Results</Text>
        <Text style={styles.bannerSub}>{analyses.length} total analyses</Text>
      </View>

      {/* Filter Buttons */}
      <View style={styles.filterRow}>
        {(['All', 'Resistant', 'Sensitive'] as const).map(f => (
          <TouchableOpacity
            key={f}
            style={[styles.filterBtn, activeFilter === f && styles.filterBtnActive]}
            onPress={() => setActiveFilter(f)}
          >
            <Text style={[styles.filterText, activeFilter === f && styles.filterTextActive]}>
              {f}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* List */}
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {filtered.length === 0 ? (
          <View style={styles.emptyCard}>
            <Ionicons name="flask-outline" size={48} color="#94a3b8" />
            <Text style={styles.emptyText}>No analyses found</Text>
            <Text style={styles.emptySubText}>Run an analysis from the website first</Text>
          </View>
        ) : (
          filtered.map((item, index) => (
            <TouchableOpacity
              key={index}
              style={styles.card}
              onPress={() => router.push(`/results/${item.analysis_code}`)}
            >
              <View style={styles.cardHeader}>
                <View>
                  <Text style={styles.cardId}>{item.id}</Text>
                  <Text style={styles.cardCancer}>{item.cancer_type}</Text>
                </View>
                <View style={[
                  styles.badge,
                  { backgroundColor: item.prediction === 'Resistant' ? '#ffe4e6' : '#dcfce7' }
                ]}>
                  <Text style={[
                    styles.badgeText,
                    { color: item.prediction === 'Resistant' ? '#e11d48' : '#16a34a' }
                  ]}>
                    {item.prediction}
                  </Text>
                </View>
              </View>

              <View style={styles.cardRow}>
                <Text style={styles.cardLabel}>Drug:</Text>
                <Text style={styles.cardValue}>{item.drug}</Text>
              </View>
              <View style={styles.cardRow}>
                <Text style={styles.cardLabel}>Confidence:</Text>
                <Text style={styles.cardValue}>{item.confidence}%</Text>
              </View>
              <View style={styles.cardRow}>
                <Text style={styles.cardLabel}>Date:</Text>
                <Text style={styles.cardValue}>{item.date}</Text>
              </View>

              <View style={styles.progressBg}>
                <View style={[
                  styles.progressFill,
                  {
                    width: `${item.confidence}%`,
                    backgroundColor: item.prediction === 'Resistant' ? '#e11d48' : '#16a34a'
                  }
                ]} />
              </View>

              <View style={styles.cardFooter}>
                <Text style={styles.viewDetails}>View Details</Text>
                <Ionicons name="arrow-forward" size={16} color="#0ea5e9" />
              </View>
            </TouchableOpacity>
          ))
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  loader: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: 24, paddingVertical: 15,
    backgroundColor: '#ffffff', borderBottomWidth: 1, borderBottomColor: '#f1f5f9',
  },
  logoText: { fontSize: 20, fontWeight: '800', color: '#0f172a' },
  banner: {
    backgroundColor: '#0ea5e9', paddingVertical: 20, paddingHorizontal: 24,
  },
  bannerTitle: { fontSize: 22, fontWeight: '900', color: '#ffffff', marginBottom: 4 },
  bannerSub: { fontSize: 14, color: '#e0f2fe' },
  filterRow: {
    flexDirection: 'row', paddingHorizontal: 16,
    marginTop: 16, marginBottom: 4, gap: 8,
  },
  filterBtn: {
    paddingVertical: 7, paddingHorizontal: 18,
    borderRadius: 20, borderWidth: 1, borderColor: '#e2e8f0',
    backgroundColor: '#ffffff',
  },
  filterBtnActive: { backgroundColor: '#0ea5e9', borderColor: '#0ea5e9' },
  filterText: { fontSize: 13, color: '#64748b', fontWeight: '600' },
  filterTextActive: { color: '#ffffff' },
  scrollContent: { padding: 16, paddingBottom: 40 },
  emptyCard: {
    alignItems: 'center', paddingVertical: 60,
    backgroundColor: '#ffffff', borderRadius: 16,
    borderWidth: 1, borderColor: '#f1f5f9', marginTop: 20,
  },
  emptyText: { fontSize: 16, fontWeight: 'bold', color: '#64748b', marginTop: 16 },
  emptySubText: { fontSize: 13, color: '#94a3b8', marginTop: 6, textAlign: 'center' },
  card: {
    backgroundColor: '#ffffff', borderRadius: 16, padding: 20,
    marginBottom: 14, borderWidth: 1, borderColor: '#f1f5f9',
    elevation: 2, shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05, shadowRadius: 3,
  },
  cardHeader: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'center', marginBottom: 14,
  },
  cardId: { fontSize: 16, fontWeight: 'bold', color: '#0f172a' },
  cardCancer: { fontSize: 13, color: '#64748b', marginTop: 2 },
  badge: { paddingVertical: 4, paddingHorizontal: 12, borderRadius: 20 },
  badgeText: { fontSize: 12, fontWeight: 'bold' },
  cardRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  cardLabel: { fontSize: 14, color: '#64748b' },
  cardValue: { fontSize: 14, fontWeight: 'bold', color: '#0f172a' },
  progressBg: {
    height: 6, backgroundColor: '#e2e8f0', borderRadius: 3,
    marginTop: 10, overflow: 'hidden',
  },
  progressFill: { height: '100%', borderRadius: 3 },
  cardFooter: {
    flexDirection: 'row', justifyContent: 'flex-end',
    alignItems: 'center', marginTop: 14, gap: 4,
  },
  viewDetails: { fontSize: 13, color: '#0ea5e9', fontWeight: 'bold' },
});

// import { Image } from 'expo-image';
// import { Platform, StyleSheet } from 'react-native';

// import { Collapsible } from '@/components/ui/collapsible';
// import { ExternalLink } from '@/components/external-link';
// import ParallaxScrollView from '@/components/parallax-scroll-view';
// import { ThemedText } from '@/components/themed-text';
// import { ThemedView } from '@/components/themed-view';
// import { IconSymbol } from '@/components/ui/icon-symbol';
// import { Fonts } from '@/constants/theme';

// export default function TabTwoScreen() {
//   return (
//     <ParallaxScrollView
//       headerBackgroundColor={{ light: '#D0D0D0', dark: '#353636' }}
//       headerImage={
//         <IconSymbol
//           size={310}
//           color="#808080"
//           name="chevron.left.forwardslash.chevron.right"
//           style={styles.headerImage}
//         />
//       }>
//       <ThemedView style={styles.titleContainer}>
//         <ThemedText
//           type="title"
//           style={{
//             fontFamily: Fonts.rounded,
//           }}>
//           Explore
//         </ThemedText>
//       </ThemedView>
//       <ThemedText>This app includes example code to help you get started.</ThemedText>
//       <Collapsible title="File-based routing">
//         <ThemedText>
//           This app has two screens:{' '}
//           <ThemedText type="defaultSemiBold">app/(tabs)/index.tsx</ThemedText> and{' '}
//           <ThemedText type="defaultSemiBold">app/(tabs)/explore.tsx</ThemedText>
//         </ThemedText>
//         <ThemedText>
//           The layout file in <ThemedText type="defaultSemiBold">app/(tabs)/_layout.tsx</ThemedText>{' '}
//           sets up the tab navigator.
//         </ThemedText>
//         <ExternalLink href="https://docs.expo.dev/router/introduction">
//           <ThemedText type="link">Learn more</ThemedText>
//         </ExternalLink>
//       </Collapsible>
//       <Collapsible title="Android, iOS, and web support">
//         <ThemedText>
//           You can open this project on Android, iOS, and the web. To open the web version, press{' '}
//           <ThemedText type="defaultSemiBold">w</ThemedText> in the terminal running this project.
//         </ThemedText>
//       </Collapsible>
//       <Collapsible title="Images">
//         <ThemedText>
//           For static images, you can use the <ThemedText type="defaultSemiBold">@2x</ThemedText> and{' '}
//           <ThemedText type="defaultSemiBold">@3x</ThemedText> suffixes to provide files for
//           different screen densities
//         </ThemedText>
//         <Image
//           source={require('@/assets/images/react-logo.png')}
//           style={{ width: 100, height: 100, alignSelf: 'center' }}
//         />
//         <ExternalLink href="https://reactnative.dev/docs/images">
//           <ThemedText type="link">Learn more</ThemedText>
//         </ExternalLink>
//       </Collapsible>
//       <Collapsible title="Light and dark mode components">
//         <ThemedText>
//           This template has light and dark mode support. The{' '}
//           <ThemedText type="defaultSemiBold">useColorScheme()</ThemedText> hook lets you inspect
//           what the user&apos;s current color scheme is, and so you can adjust UI colors accordingly.
//         </ThemedText>
//         <ExternalLink href="https://docs.expo.dev/develop/user-interface/color-themes/">
//           <ThemedText type="link">Learn more</ThemedText>
//         </ExternalLink>
//       </Collapsible>
//       <Collapsible title="Animations">
//         <ThemedText>
//           This template includes an example of an animated component. The{' '}
//           <ThemedText type="defaultSemiBold">components/HelloWave.tsx</ThemedText> component uses
//           the powerful{' '}
//           <ThemedText type="defaultSemiBold" style={{ fontFamily: Fonts.mono }}>
//             react-native-reanimated
//           </ThemedText>{' '}
//           library to create a waving hand animation.
//         </ThemedText>
//         {Platform.select({
//           ios: (
//             <ThemedText>
//               The <ThemedText type="defaultSemiBold">components/ParallaxScrollView.tsx</ThemedText>{' '}
//               component provides a parallax effect for the header image.
//             </ThemedText>
//           ),
//         })}
//       </Collapsible>
//     </ParallaxScrollView>
//   );
// }

// const styles = StyleSheet.create({
//   headerImage: {
//     color: '#808080',
//     bottom: -90,
//     left: -35,
//     position: 'absolute',
//   },
//   titleContainer: {
//     flexDirection: 'row',
//     gap: 8,
//   },
// });
