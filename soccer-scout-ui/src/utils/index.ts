import { clsx, type ClassValue } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatNumber(num: number, decimals: number = 2): string {
  return num.toFixed(decimals);
}

export function formatAge(age: number): string {
  return `${age} years old`;
}

export function formatPosition(position: string): string {
  const positionMap: Record<string, string> = {
    'GK': 'Goalkeeper',
    'DF': 'Defender',
    'MF': 'Midfielder',
    'FW': 'Forward',
    'DF,MF': 'Defender/Midfielder',
    'MF,FW': 'Midfielder/Forward',
    'DF,FW': 'Defender/Forward',
  };
  
  return positionMap[position] || position;
}

export function getTierEmoji(potentialScore?: number): string {
  if (!potentialScore) return '📈';
  if (potentialScore >= 8) return '⭐';
  if (potentialScore >= 6) return '🌟';
  if (potentialScore >= 4) return '💫';
  return '📈';
}

export function getTierLabel(potentialScore?: number): string {
  if (!potentialScore) return 'Developing';
  if (potentialScore >= 8) return 'Elite';
  if (potentialScore >= 6) return 'High';
  if (potentialScore >= 4) return 'Good';
  return 'Developing';
}

export function formatDate(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}