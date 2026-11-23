<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { appData } from 'src/AppData';
import { questMeta } from 'src/questEditorial';
import { Bilingual } from 'src/classes/model/Quest';

defineOptions({
  name: 'QuestsPage',
});

const { locale } = useI18n();
const loading = ref(true);

const isZh = computed(() => locale.value === 'zh');

async function load() {
  loading.value = true;
  await appData.fetchQuestIndex(appData.selectedVersion.value);
  loading.value = false;
}

onMounted(load);
watch(() => appData.selectedVersion.value, load);

const quests = computed(() => appData.questIndex?.quests ?? []);

function primary(text: Bilingual): string {
  return isZh.value ? text.zh : text.en;
}

/** 官方名优先；无官方名（聚合包/未翻译任务名）用 wiki 编辑层标签 */
function questName(quest: { id: string; name?: Bilingual }): {
  text: string;
  isWiki: boolean;
} {
  if (quest.name) {
    return { text: primary(quest.name), isWiki: false };
  }
  const meta = questMeta(quest.id);
  if (meta) {
    return { text: primary(meta.name), isWiki: true };
  }
  return { text: quest.id, isWiki: true };
}

function questSummary(quest: { id: string; summary?: Bilingual }): string {
  if (quest.summary) {
    return primary(quest.summary);
  }
  const meta = questMeta(quest.id);
  return meta?.summary ? primary(meta.summary) : '';
}

function factionName(factionId: string | null): string {
  if (!factionId) {
    return '';
  }
  const faction = appData.getFactionById(factionId);
  return faction?.displayName ?? factionId;
}
</script>

<template>
  <q-page padding>
    <div v-if="loading" class="quest-loading">{{ $t('common.loading') }}</div>
    <template v-else>
      <div v-if="quests.length === 0" class="quest-loading">
        {{ $t('quest.none') }}
      </div>
      <template v-else>
        <div class="result-count">
          {{ $t('filter.results', { count: quests.length }) }}
        </div>
        <div class="card-item-list-page">
          <q-btn
            class="card-item quest-card"
            no-caps
            v-for="quest in quests"
            :key="quest.id"
            :to="{ name: 'quest', params: { id: quest.id } }"
          >
            <div class="quest-card-content">
              <div class="quest-card-title">
                <span class="quest-card-name">{{ questName(quest).text }}</span>
                <q-chip v-if="questName(quest).isWiki" dense size="sm" outline>
                  {{ $t('quest.wikiLabel') }}
                </q-chip>
                <span
                  v-if="factionName(quest.factionId)"
                  class="quest-card-faction"
                >
                  {{ factionName(quest.factionId) }}
                </span>
              </div>
              <div v-if="questSummary(quest)" class="quest-card-summary">
                {{ questSummary(quest) }}
              </div>
              <div class="quest-card-meta">
                <q-chip dense size="sm">
                  {{ $t('quest.stages') }}: {{ quest.stageCount }}
                </q-chip>
                <q-chip dense size="sm">
                  {{ $t('quest.sceneCount', { count: quest.sceneCount }) }}
                </q-chip>
              </div>
            </div>
          </q-btn>
        </div>
      </template>
    </template>
  </q-page>
</template>

<style scoped lang="scss">
.quest-loading {
  opacity: 0.7;
  padding: 16px;
}

.quest-card {
  width: 100%;
  margin-bottom: 8px;
  text-align: left;
}

.quest-card-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-start;
  width: 100%;
}

.quest-card-title {
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}

.quest-card-name {
  font-size: 1.2em;
  font-weight: bold;
}

.quest-card-faction {
  opacity: 0.7;
  font-size: 0.9em;
}

.quest-card-summary {
  opacity: 0.85;
  font-size: 0.95em;
  text-align: left;
}

.quest-card-meta {
  display: flex;
  gap: 4px;
}
</style>
