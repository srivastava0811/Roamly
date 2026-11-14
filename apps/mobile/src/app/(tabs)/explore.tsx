import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { colors } from '@roamly/design-tokens';

export default function ExploreScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Budget-First Discovery</Text>
      <Text style={styles.subtitle}>
        Destination discovery agent will recommend places matching your maximum spending ceiling.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.neutral[50],
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.neutral[900],
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: colors.neutral[500],
    textAlign: 'center',
    lineHeight: 20,
  },
});
