<script setup lang="ts">
import { appData } from 'src/AppData';

const versions = appData.availableVersions;

// Auto-select first version if none selected
if (!appData.selectedVersion.value && versions.length > 0) {
  appData.selectedVersion.value = versions[0].version;
  localStorage.setItem('selectedVersion', versions[0].version);
}

async function onVersionChange(version: string) {
  if (version === appData.selectedVersion.value) return;
  appData.selectedVersion.value = version;
  localStorage.setItem('selectedVersion', version);
  await appData.reloadData(version, appData.selectedLocale.value);
}
</script>

<template>
  <q-btn-dropdown
    v-if="versions.length > 0"
    flat dense
    :label="appData.selectedVersion.value || 'No version'"
    class="q-mr-sm"
  >
    <q-list>
      <q-item
        v-for="v in versions"
        :key="v.version"
        clickable v-close-popup
        :active="v.version === appData.selectedVersion.value"
        @click="onVersionChange(v.version)"
      >
        <q-item-section>
          <q-item-label>{{ v.version }}</q-item-label>
          <q-item-label caption>
            {{ v.locales.length > 1 ? v.locales.length + ' languages' : v.locales.length + ' language' }}
          </q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </q-btn-dropdown>
</template>
