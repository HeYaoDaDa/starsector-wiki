<script setup lang="ts">
import { appData } from 'src/AppData';

defineOptions({
  name: 'App',
});
</script>

<template>
  <router-view :key="appData.selectedVersion.value + '-' + appData.selectedLocale.value" />
</template>
