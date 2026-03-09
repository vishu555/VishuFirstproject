import { useAuthStore } from '@/store/authStore';
import { getCurrencySymbol } from '@/constants/currencies';

export const useCurrency = () => {
  const user = useAuthStore((state) => state.user);
  const currencyCode = user?.currency || 'USD';
  const currencySymbol = getCurrencySymbol(currencyCode);

  const formatAmount = (amount: number): string => {
    return `${currencySymbol}${amount.toFixed(2)}`;
  };

  return {
    currencyCode,
    currencySymbol,
    formatAmount,
  };
};
