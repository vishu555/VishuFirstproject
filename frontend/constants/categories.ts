export const EXPENSE_CATEGORIES = [
  { label: 'Food', value: 'Food', icon: 'fast-food', color: '#FF6B6B' },
  { label: 'Transport', value: 'Transport', icon: 'car', color: '#4ECDC4' },
  { label: 'Rent', value: 'Rent', icon: 'home', color: '#45B7D1' },
  { label: 'Shopping', value: 'Shopping', icon: 'cart', color: '#FFA07A' },
  { label: 'Medical', value: 'Medical', icon: 'medkit', color: '#98D8C8' },
  { label: 'Bills', value: 'Bills', icon: 'receipt', color: '#F7DC6F' },
  { label: 'Entertainment', value: 'Entertainment', icon: 'film', color: '#BB8FCE' },
  { label: 'Education', value: 'Education', icon: 'school', color: '#85C1E2' },
  { label: 'Other', value: 'Other', icon: 'ellipsis-horizontal', color: '#95A5A6' },
];

export const INCOME_SOURCES = [
  { label: 'Salary', value: 'Salary' },
  { label: 'Business', value: 'Business' },
  { label: 'Freelance', value: 'Freelance' },
  { label: 'Investment', value: 'Investment' },
  { label: 'Other', value: 'Other' },
];

export const getCategoryColor = (category: string): string => {
  const cat = EXPENSE_CATEGORIES.find(c => c.value === category);
  return cat?.color || '#95A5A6';
};

export const getCategoryIcon = (category: string): string => {
  const cat = EXPENSE_CATEGORIES.find(c => c.value === category);
  return cat?.icon || 'ellipsis-horizontal';
};