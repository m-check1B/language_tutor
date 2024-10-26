import { browser } from '$app/environment';
import { init, register, getLocaleFromNavigator } from 'svelte-i18n';

register('en', () => import('./i18n/en.json'));
register('cs', () => import('./i18n/cs.json'));
register('es', () => import('./i18n/es.json'));

export function initI18n() {
  init({
    fallbackLocale: 'en',
    initialLocale: browser ? getLocaleFromNavigator() : 'en',
  });
}
