import { createI18n } from 'vue-i18n';
import en from './en.json';
import zh from './zh.json';

function getInitialLocale(): string {
  const stored = localStorage.getItem('locale');
  if (stored === 'en' || stored === 'zh') {
    return stored;
  }
  if (navigator.language.startsWith('zh')) {
    return 'zh';
  }
  return 'en';
}

const i18n = createI18n({
  legacy: false,
  locale: getInitialLocale(),
  fallbackLocale: 'en',
  messages: { en, zh },
});

export default i18n;
