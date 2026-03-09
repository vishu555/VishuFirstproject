import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '@/store/authStore';
import { useDataStore } from '@/store/dataStore';
import { BarChart } from 'react-native-gifted-charts';
import { getCategoryColor } from '@/constants/categories';
import { useCurrency } from '@/utils/useCurrency';

const { width } = Dimensions.get('window');

export default function DashboardScreen() {
  const { user } = useAuthStore();
  const { analytics, expenses, fetchAnalytics, fetchExpenses, refreshAll, isLoading } = useDataStore();
  const [refreshing, setRefreshing] = useState(false);
  const { currencySymbol } = useCurrency();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    await refreshAll();
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await refreshAll();
    setRefreshing(false);
  };

  // Get category breakdown for chart
  const getCategoryData = () => {
    const categoryTotals: { [key: string]: number } = {};
    expenses.forEach(exp => {
      categoryTotals[exp.category] = (categoryTotals[exp.category] || 0) + exp.amount;
    });

    return Object.entries(categoryTotals)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([category, amount]) => ({
        value: amount,
        label: category.substring(0, 4),
        frontColor: getCategoryColor(category),
      }));
  };

  const categoryChartData = getCategoryData();

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#4CAF50']} />}
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Hello,</Text>
            <Text style={styles.username}>{user?.name || 'User'}</Text>
          </View>
          <View style={styles.iconContainer}>
            <Ionicons name="wallet" size={32} color="#4CAF50" />
          </View>
        </View>

        {/* Balance Card */}
        <View style={styles.balanceCard}>
          <Text style={styles.balanceLabel}>Total Balance</Text>
          <Text style={styles.balanceAmount}>
            ${currencySymbol}{?analytics?.remaining_balance?.toFixed(2) || '0.00'}
          </Text>
          <View style={styles.balanceDetails}>
            <View style={styles.balanceItem}>
              <Ionicons name="arrow-down-circle" size={20} color="#4CAF50" />
              <Text style={styles.balanceItemLabel}>Income</Text>
              <Text style={styles.balanceItemValue}>${currencySymbol}{?analytics?.total_income?.toFixed(2) || '0.00'}</Text>
            </View>
            <View style={styles.balanceDivider} />
            <View style={styles.balanceItem}>
              <Ionicons name="arrow-up-circle" size={20} color="#F44336" />
              <Text style={styles.balanceItemLabel}>Expenses</Text>
              <Text style={styles.balanceItemValue}>${currencySymbol}{?analytics?.total_expenses?.toFixed(2) || '0.00'}</Text>
            </View>
          </View>
        </View>

        {/* Monthly Summary */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>This Month</Text>
          <View style={styles.summaryGrid}>
            <View style={[styles.summaryCard, { backgroundColor: '#E8F5E9' }]}>
              <Ionicons name="trending-up" size={24} color="#4CAF50" />
              <Text style={styles.summaryLabel}>Income</Text>
              <Text style={styles.summaryValue}>${currencySymbol}{?analytics?.monthly_income?.toFixed(2) || '0.00'}</Text>
            </View>
            <View style={[styles.summaryCard, { backgroundColor: '#FFEBEE' }]}>
              <Ionicons name="trending-down" size={24} color="#F44336" />
              <Text style={styles.summaryLabel}>Expenses</Text>
              <Text style={styles.summaryValue}>${currencySymbol}{?analytics?.monthly_expenses?.toFixed(2) || '0.00'}</Text>
            </View>
            <View style={[styles.summaryCard, { backgroundColor: '#E3F2FD' }]}>
              <Ionicons name="save" size={24} color="#2196F3" />
              <Text style={styles.summaryLabel}>Savings Rate</Text>
              <Text style={styles.summaryValue}>{analytics?.savings_rate?.toFixed(1) || '0'}%</Text>
            </View>
          </View>
        </View>

        {/* Category Spending Chart */}
        {categoryChartData.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Top Spending Categories</Text>
            <View style={styles.chartCard}>
              <BarChart
                data={categoryChartData}
                width={width - 80}
                height={180}
                barWidth={40}
                spacing={20}
                roundedTop
                hideRules
                xAxisThickness={0}
                yAxisThickness={0}
                yAxisTextStyle={{ color: '#666', fontSize: 12 }}
                noOfSections={4}
                maxValue={Math.max(...categoryChartData.map(d => d.value)) * 1.2}
              />
            </View>
          </View>
        )}

        {/* Recent Expenses */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Expenses</Text>
          {expenses.slice(0, 5).map((expense) => (
            <View key={expense.id} style={styles.transactionCard}>
              <View
                style={[
                  styles.categoryIcon,
                  { backgroundColor: getCategoryColor(expense.category) + '20' },
                ]}
              >
                <Ionicons name="cart" size={20} color={getCategoryColor(expense.category)} />
              </View>
              <View style={styles.transactionInfo}>
                <Text style={styles.transactionCategory}>{expense.category}</Text>
                <Text style={styles.transactionDate}>{expense.date}</Text>
              </View>
              <Text style={styles.transactionAmount}>-{currencySymbol}{expense.amount.toFixed(2)}</Text>
            </View>
          ))}
          {expenses.length === 0 && (
            <View style={styles.emptyState}>
              <Ionicons name="receipt-outline" size={48} color="#CCC" />
              <Text style={styles.emptyStateText}>No expenses yet</Text>
            </View>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 24,
  },
  greeting: {
    fontSize: 16,
    color: '#666',
  },
  username: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 4,
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#E8F5E9',
    justifyContent: 'center',
    alignItems: 'center',
  },
  balanceCard: {
    backgroundColor: '#4CAF50',
    marginHorizontal: 24,
    borderRadius: 20,
    padding: 24,
    marginBottom: 24,
  },
  balanceLabel: {
    fontSize: 16,
    color: '#FFFFFF',
    opacity: 0.9,
  },
  balanceAmount: {
    fontSize: 40,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginTop: 8,
    marginBottom: 24,
  },
  balanceDetails: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  balanceItem: {
    flex: 1,
    alignItems: 'center',
  },
  balanceDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#FFFFFF',
    opacity: 0.3,
  },
  balanceItemLabel: {
    fontSize: 14,
    color: '#FFFFFF',
    opacity: 0.9,
    marginTop: 4,
  },
  balanceItemValue: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
    marginTop: 4,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginHorizontal: 24,
    marginBottom: 16,
  },
  summaryGrid: {
    flexDirection: 'row',
    paddingHorizontal: 24,
    gap: 12,
  },
  summaryCard: {
    flex: 1,
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
  },
  summaryLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 8,
    textAlign: 'center',
  },
  summaryValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 4,
  },
  chartCard: {
    backgroundColor: '#FFFFFF',
    marginHorizontal: 24,
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
  },
  transactionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    marginHorizontal: 24,
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  categoryIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  transactionInfo: {
    flex: 1,
  },
  transactionCategory: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  transactionDate: {
    fontSize: 14,
    color: '#999',
    marginTop: 4,
  },
  transactionAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#F44336',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 48,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#999',
    marginTop: 16,
  },
});