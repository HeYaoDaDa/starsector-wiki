<script setup lang="ts">
import { appData } from 'src/AppData';
import { ref, watchEffect } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const { locale } = useI18n();

const fail = ref(false);

let loading = false;
async function triggerLoad() {
  if (loading) return;
  loading = true;
  const manifestOk = await appData.fetchManifest();
  if (!manifestOk) return;

  // Auto-select first version if none selected
  if (!appData.selectedVersion.value && appData.availableVersions.length > 0) {
    appData.selectedVersion.value = appData.availableVersions[0].version;
    localStorage.setItem('selectedVersion', appData.availableVersions[0].version);
  }

  const version = appData.selectedVersion.value;
  if (!version) {
    fail.value = true;
    return;
  }
  const currentLocale = locale.value || appData.selectedLocale.value || 'en';
  appData.selectedLocale.value = currentLocale;
  await appData.initData(version, currentLocale);
}

watchEffect(() => {
  if ('none' === appData.status.value) {
    triggerLoad();
  } else if ('finish' === appData.status.value) {
    router.replace('/');
  } else if ('fail' === appData.status.value) {
    fail.value = true;
  } else if ('empty' === appData.status.value) {
    fail.value = true;
  }
});
</script>

<template>
  <div id="load-page-root">
    <h1 id="load-data-fail-text" v-if="fail">{{ $t('common.loadError') }}</h1>
    <h1 v-else>{{ $t('common.loading') }}</h1>
  </div>
</template>

<style lang="scss">
#load-page-root {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;

  #load-data-fail-text {
    color: red;
  }
}
</style>
