import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Modal,
  Alert,
  RefreshControl,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useDataStore } from '@/store/dataStore';
import { EXPENSE_CATEGORIES, getCategoryColor, getCategoryIcon } from '@/constants/categories';
import { format } from 'date-fns';
import { useCurrency } from '@/utils/useCurrency';

export default function ExpensesScreen() {
  const { expenses, fetchExpenses, addExpense, deleteExpense } = useDataStore();
  const [modalVisible, setModalVisible] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('Food');
  const [date, setDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { currencySymbol } = useCurrency();

  useEffect(() => {
    fetchExpenses();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchExpenses();
    setRefreshing(false);
  };

  const handleAddExpense = async () => {
    if (!amount || parseFloat(amount) <= 0) {
      Alert.alert('Error', 'Please enter a valid amount');
      return;
    }

    setIsSubmitting(true);
    try {
      await addExpense({
        amount: parseFloat(amount),
        category,
        date,
        notes,
      });
      setModalVisible(false);
      resetForm();
      Alert.alert('Success', 'Expense added successfully');
    } catch (error: any) {
      Alert.alert('Error', error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteExpense = (id: string) => {
    Alert.alert('Delete Expense', 'Are you sure you want to delete this expense?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: async () => {
          try {
            await deleteExpense(id);
            Alert.alert('Success', 'Expense deleted');
          } catch (error: any) {
            Alert.alert('Error', error.message);
          }
        },
      },
    ]);
  };

  const resetForm = () => {
    setAmount('');
    setCategory('Food');
    setDate(format(new Date(), 'yyyy-MM-dd'));
    setNotes('');
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Expenses</Text>
        <TouchableOpacity style={styles.addButton} onPress={() => setModalVisible(true)}>
          <Ionicons name="add" size={24} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.scrollView}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#4CAF50']} />}
      >
        {expenses.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="receipt-outline" size={64} color="#CCC" />
            <Text style={styles.emptyStateText}>No expenses yet</Text>
            <Text style={styles.emptyStateSubtext}>Tap + to add your first expense</Text>
          </View>
        ) : (
          expenses.map((expense) => (
            <TouchableOpacity
              key={expense.id}
              style={styles.expenseCard}
              onLongPress={() => handleDeleteExpense(expense.id)}
              activeOpacity={0.7}
            >
              <View
                style={[
                  styles.categoryIcon,
                  { backgroundColor: getCategoryColor(expense.category) + '20' },
                ]}
              >
                <Ionicons
                  name={getCategoryIcon(expense.category) as any}
                  size={24}
                  color={getCategoryColor(expense.category)}
                />
              </View>
              <View style={styles.expenseInfo}>
                <Text style={styles.expenseCategory}>{expense.category}</Text>
                <Text style={styles.expenseDate}>{expense.date}</Text>
                {expense.notes ? <Text style={styles.expenseNotes}>{expense.notes}</Text> : null}
              </View>
              <Text style={styles.expenseAmount}>-${currencySymbol}{?expense.amount.toFixed(2)}</Text>
            </TouchableOpacity>
          ))
        )}
      </ScrollView>

      {/* Add Expense Modal */}
      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Add Expense</Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Ionicons name="close" size={28} color="#333" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalForm} keyboardShouldPersistTaps="handled">
              <Text style={styles.label}>Amount *</Text>
              <TextInput
                style={styles.input}
                placeholder="0.00"
                value={amount}
                onChangeText={setAmount}
                keyboardType="decimal-pad"
                placeholderTextColor="#999"
              />

              <Text style={styles.label}>Category *</Text>
              <View style={styles.categoryGrid}>
                {EXPENSE_CATEGORIES.map((cat) => (
                  <TouchableOpacity
                    key={cat.value}
                    style={[
                      styles.categoryButton,
                      category === cat.value && {
                        backgroundColor: cat.color + '20',
                        borderColor: cat.color,
                        borderWidth: 2,
                      },
                    ]}
                    onPress={() => setCategory(cat.value)}
                  >
                    <Ionicons name={cat.icon as any} size={24} color={cat.color} />
                    <Text style={styles.categoryLabel}>{cat.label}</Text>
                  </TouchableOpacity>
                ))}
              </View>

              <Text style={styles.label}>Date *</Text>
              <TextInput
                style={styles.input}
                placeholder="YYYY-MM-DD"
                value={date}
                onChangeText={setDate}
                placeholderTextColor="#999"
              />

              <Text style={styles.label}>Notes (Optional)</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                placeholder="Add notes..."
                value={notes}
                onChangeText={setNotes}
                multiline
                numberOfLines={3}
                placeholderTextColor="#999"
              />

              <TouchableOpacity
                style={[styles.submitButton, isSubmitting && styles.submitButtonDisabled]}
                onPress={handleAddExpense}
                disabled={isSubmitting}
              >
                <Text style={styles.submitButtonText}>
                  {isSubmitting ? 'Adding...' : 'Add Expense'}
                </Text>
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 24,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  addButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#4CAF50',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollView: {
    flex: 1,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#999',
    marginTop: 16,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#BBB',
    marginTop: 8,
  },
  expenseCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    marginHorizontal: 24,
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  categoryIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  expenseInfo: {
    flex: 1,
  },
  expenseCategory: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  expenseDate: {
    fontSize: 14,
    color: '#999',
    marginTop: 4,
  },
  expenseNotes: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  expenseAmount: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#F44336',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingTop: 24,
    maxHeight: '90%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    marginBottom: 24,
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  modalForm: {
    paddingHorizontal: 24,
    paddingBottom: Platform.OS === 'ios' ? 32 : 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#333',
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  categoryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 20,
  },
  categoryButton: {
    width: '30%',
    aspectRatio: 1,
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  categoryLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 8,
    textAlign: 'center',
  },
  submitButton: {
    backgroundColor: '#4CAF50',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 8,
    marginBottom: 24,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
  },
});