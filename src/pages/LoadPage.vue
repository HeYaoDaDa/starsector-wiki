<script setup lang="ts">
import { appData } from 'src/AppData';
import { ref, watchEffect, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const { locale, t } = useI18n();

const fail = ref(false);

const progressPercent = computed(() => appData.loadProgress.value.percent);
const progressMessage = computed(() => {
  const msg = appData.loadProgress.value.message;
  return msg ? t(msg) : '';
});

let loading = false;
async function triggerLoad() {
  if (loading) return;
  loading = true;
  appData.loadProgress.value = { percent: 0, message: 'common.loading' };

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
    const redirectPath = sessionStorage.getItem('redirectAfterLoad') || '/';
    sessionStorage.removeItem('redirectAfterLoad');
    router.replace(redirectPath);
  } else if ('fail' === appData.status.value) {
    fail.value = true;
  } else if ('empty' === appData.status.value) {
    fail.value = true;
  }
});
</script>

<template>
  <div id="load-page-root">
    <template v-if="fail">
      <h1 id="load-data-fail-text">{{ $t('common.loadError') }}</h1>
    </template>
    <template v-else>
      <div id="load-progress">
        <h1>{{ $t('common.loading') }}</h1>
        <q-linear-progress
          :value="progressPercent / 100"
          color="primary"
          size="8px"
          rounded
          class="q-mt-md"
          :indeterminate="progressPercent === 0"
        />
        <p v-if="progressMessage" class="q-mt-sm text-caption">
          {{ progressMessage }}
          <template v-if="progressPercent > 0">
            ({{ progressPercent }}%)
          </template>
        </p>
      </div>
    </template>
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

#load-progress {
  text-align: center;
  min-width: 280px;
  max-width: 400px;
}
</style>
