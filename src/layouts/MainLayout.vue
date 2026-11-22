<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import VersionSelector from 'src/components/VersionSelector.vue';
import { appData } from 'src/AppData';

const { locale } = useI18n();

const leftDrawerOpen = ref(false);
const router = useRouter();

// 添加 Escape 键关闭菜单的功能
function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && leftDrawerOpen.value) {
    leftDrawerOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
});

const langOptions = [
  { label: 'English', value: 'en' },
  { label: '中文', value: 'zh' },
];

async function switchLang(lang: string) {
  locale.value = lang;
  localStorage.setItem('locale', lang);
  appData.selectedLocale.value = lang;
  await appData.reloadData(appData.selectedVersion.value, lang);
}

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

function goBack() {
  router.back();
}
</script>

<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-btn flat dense round icon="arrow_back" aria-label="Back" @click="goBack" class="q-ml-sm lt-sm" />

        <q-toolbar-title> {{ $t('app.title') }} </q-toolbar-title>
        <VersionSelector />
        <q-btn-dropdown flat dense :label="locale === 'zh' ? '中文' : 'English'">
          <q-list>
            <q-item v-for="opt in langOptions" :key="opt.value" clickable v-close-popup @click="switchLang(opt.value)">
              <q-item-section>
                <q-item-label>{{ opt.label }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" bordered overlay>
      <q-list>
        <q-item-label header> {{ $t('nav.categories') }} </q-item-label>
        <q-item clickable :to="{ name: 'ships' }">
          <q-item-section>{{ $t('nav.ships') }}</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'ship_systems' }">
          <q-item-section>{{ $t('nav.shipSystems') }}</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'ship_mods' }">
          <q-item-section>{{ $t('nav.shipMods') }}</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'weapons' }">
          <q-item-section>{{ $t('nav.weapons') }}</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'special_items' }">
          <q-item-section>{{ $t('nav.specialItems') }}</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'commodities' }">
          <q-item-section>{{ $t('nav.commodities') }}</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'industries' }">
          <q-item-section>{{ $t('nav.industries') }}</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'planet_types' }">
          <q-item-section>{{ $t('nav.planetTypes') }}</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'market_conditions' }">
          <q-item-section>{{ $t('nav.marketConditions') }}</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'sub_markets' }">
          <q-item-section>{{ $t('nav.subMarkets') }}</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'factions' }">
          <q-item-section>{{ $t('nav.factions') }}</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'star_systems' }">
          <q-item-section>{{ $t('nav.starSystems') }}</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'planets' }">
          <q-item-section>{{ $t('nav.planets') }}</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'persons' }">
          <q-item-section>{{ $t('nav.persons') }}</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'quests' }">
          <q-item-section>{{ $t('nav.quests') }}</q-item-section>
        </q-item>
        <q-separator />
        <q-item clickable tag="a" href="https://github.com/HeYaoDaDa/starsector-wiki" target="_blank">
          <q-item-section>{{ $t('nav.github') }}</q-item-section>
          <q-item-section side>
            <q-icon name="open_in_new" size="xs" />
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view v-slot="{ Component, route }">
        <keep-alive>
          <component v-if="route.meta.keepAlive" :is="Component" :key="route.fullPath" />
        </keep-alive>
        <component v-if="!route.meta.keepAlive" :is="Component" :key="route.fullPath" />
      </router-view>
    </q-page-container>
  </q-layout>
</template>
