<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { onBeforeRouteUpdate, useRoute } from 'vue-router';
import { appData } from 'src/AppData';
import { Quest, QuestScene } from 'src/classes/model/Quest';
import QuestDialogue from 'src/components/quest/QuestDialogue.vue';

defineOptions({
  name: 'QuestPage',
});

const route = useRoute();
const { locale } = useI18n();

const id = ref(route.params.id as string);
const quest = ref<Quest | undefined>(undefined);
const loading = ref(true);
const loadError = ref(false);
const selectedSceneId = ref<string | null>(null);

onBeforeRouteUpdate(async (to) => {
  id.value = to.params.id as string;
  await load();
});

async function load() {
  loading.value = true;
  loadError.value = false;
  selectedSceneId.value = null;
  quest.value = await appData.loadQuest(appData.selectedVersion.value, id.value);
  if (!quest.value) {
    const index = appData.questIndex;
    if (!index) {
      await appData.fetchQuestIndex(appData.selectedVersion.value);
    }
    quest.value = await appData.loadQuest(appData.selectedVersion.value, id.value);
    if (!quest.value) {
      loadError.value = true;
    }
  }
  loading.value = false;
}

onMounted(load);
watch(() => appData.selectedVersion.value, load);

const isZh = computed(() => locale.value === 'zh');

function primary(text: { en: string; zh: string }): string {
  return isZh.value ? text.zh : text.en;
}
function secondary(text: { en: string; zh: string }): string {
  return isZh.value ? text.en : text.zh;
}

const faction = computed(() => {
  if (!quest.value?.factionId) {
    return undefined;
  }
  return appData.getFactionById(quest.value.factionId);
});

/** 按任务阶段分组场景；无阶段的场景排在最前 */
const stageGroups = computed(() => {
  return curatedGroups.value;
});

const selectedScene = computed<QuestScene | undefined>(() => {
  if (!quest.value || !selectedSceneId.value) {
    return undefined;
  }
  return quest.value.scenes.find((s) => s.id === selectedSceneId.value);
});

/** 策展场景 vs 自动兜底收录场景 */
const curatedGroups = computed(() => {
  if (!quest.value) {
    return [];
  }
  const isAuto = (sc: QuestScene) => sc.id.startsWith('auto_');
  const stages = quest.value.stages;
  const groups = stages.map((st) => ({
    stage: st,
    scenes: [] as QuestScene[],
  }));
  const ungrouped = { stage: null, scenes: [] as QuestScene[] };
  for (const scene of quest.value.scenes) {
    if (isAuto(scene)) {
      continue;
    }
    if (scene.stage) {
      const group = groups.find((g) => g.stage.id === scene.stage);
      if (group) {
        group.scenes.push(scene);
        continue;
      }
    }
    ungrouped.scenes.push(scene);
  }
  const out = [];
  if (ungrouped.scenes.length > 0) {
    out.push(ungrouped);
  }
  for (const g of groups) {
    if (g.scenes.length > 0) {
      out.push(g);
    }
  }
  return out;
});

const autoScenes = computed<QuestScene[]>(() =>
  (quest.value?.scenes ?? []).filter((sc) => sc.id.startsWith('auto_'))
);

const showAuto = ref(false);

function selectScene(sceneId: string) {
  selectedSceneId.value = sceneId;
}
</script>

<template>
  <q-page padding>
    <div v-if="loading" class="quest-loading">{{ $t('common.loading') }}</div>
    <template v-else>
      <template v-if="!quest">
        <h2>{{ $t('quest.notFound', { id: id }) }}</h2>
      </template>
      <template v-else>
        <!-- 头部 -->
        <div class="quest-header">
          <h4 class="quest-title">{{ primary(quest.name) }}</h4>
          <div v-if="faction" class="quest-faction">
            <img :src="faction.logo" />
            <span :style="{ color: '#' + faction.color }">{{
              faction.displayName
            }}</span>
          </div>
        </div>
        <div class="quest-summary">{{ primary(quest.summary) }}</div>
        <div class="quest-summary-en">{{ secondary(quest.summary) }}</div>

        <!-- 人物 -->
        <h5>{{ $t('quest.characters') }}</h5>
        <div class="quest-characters">
          <div v-for="c in quest.characters" :key="c.id" class="quest-character">
            <div class="quest-character-name">{{ primary(c.name) }}</div>
            <div class="quest-character-title">{{ primary(c.title) }}</div>
          </div>
        </div>

        <!-- 任务阶段 -->
        <h5>{{ $t('quest.stages') }}</h5>
        <div class="quest-stages">
          <div
            v-for="(st, i) in quest.stages"
            :key="st.id"
            class="quest-stage"
            :class="{ 'quest-stage-done': st.id === 'COMPLETED' }"
          >
            <div class="quest-stage-index">{{ i + 1 }}</div>
            <div class="quest-stage-body">
              <div class="quest-stage-name">{{ st.id }}</div>
              <div class="quest-stage-briefing">{{ primary(st.briefing) }}</div>
              <div class="quest-stage-briefing-en">{{ secondary(st.briefing) }}</div>
            </div>
          </div>
        </div>

        <!-- 对话场景 -->
        <div class="quest-scenes-header">
          <h5>{{ $t('quest.scenes') }}</h5>
          <q-btn
            v-if="selectedScene"
            dense
            flat
            no-caps
            icon="arrow_back"
            :label="$t('quest.backToScenes')"
            @click="selectedSceneId = null"
          />
        </div>

        <template v-if="!selectedScene">
          <div class="quest-scenes-hint">{{ $t('quest.selectScene') }}</div>
          <div
            v-for="group in stageGroups"
            :key="group.stage?.id ?? 'none'"
            class="quest-scene-group"
          >
            <div v-if="group.stage" class="quest-scene-group-title">
              {{ $t('quest.stage') }} {{ group.stage.id }}
            </div>
            <div v-else class="quest-scene-group-title quest-scene-group-none">
              {{ $t('quest.stage') }} —
            </div>
            <div class="quest-scene-list">
              <q-btn
                v-for="scene in group.scenes"
                :key="scene.id"
                class="quest-scene-btn"
                no-caps
                align="left"
                @click="selectScene(scene.id)"
              >
                <div class="quest-scene-content">
                  <div class="quest-scene-title">{{ primary(scene.title) }}</div>
                  <div
                    v-if="scene.location"
                    class="quest-scene-location"
                  >
                    {{ primary(scene.location) }}
                  </div>
                </div>
              </q-btn>
            </div>
          </div>

          <!-- 自动兜底收录的场景（折叠） -->
          <div v-if="autoScenes.length > 0" class="quest-auto-block">
            <q-btn
              dense
              flat
              no-caps
              icon="auto_awesome"
              :label="$t('quest.autoScenes', { count: autoScenes.length })"
              @click="showAuto = !showAuto"
            />
            <div v-if="showAuto" class="quest-scene-list">
              <q-btn
                v-for="scene in autoScenes"
                :key="scene.id"
                class="quest-scene-btn quest-scene-btn-auto"
                no-caps
                align="left"
                @click="selectScene(scene.id)"
              >
                <div class="quest-scene-content">
                  <div class="quest-scene-title">{{ primary(scene.title) }}</div>
                </div>
              </q-btn>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="quest-scene-active-header">
            <div class="quest-scene-title-lg">{{ primary(selectedScene.title) }}</div>
            <div v-if="selectedScene.location" class="quest-scene-location">
              {{ primary(selectedScene.location) }}
            </div>
          </div>
          <QuestDialogue :quest="quest" :scene="selectedScene" />
        </template>
      </template>
    </template>
  </q-page>
</template>

<style scoped lang="scss">
.quest-loading {
  opacity: 0.7;
  padding: 16px;
}

.quest-header {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.quest-title {
  margin: 0;
}

.quest-faction {
  display: flex;
  align-items: center;
  gap: 8px;
  img {
    height: 24px;
  }
}

.quest-summary {
  margin-top: 8px;
  line-height: 1.6;
}

.quest-summary-en {
  opacity: 0.5;
  font-style: italic;
  font-size: 0.92em;
  line-height: 1.5;
  margin-bottom: 12px;
}

h5 {
  margin-top: 20px;
  margin-bottom: 8px;
  opacity: 0.9;
}

.quest-characters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.quest-character {
  border: 1px solid rgba(128, 128, 128, 0.3);
  border-radius: 6px;
  padding: 6px 12px;
}

.quest-character-name {
  font-weight: bold;
}

.quest-character-title {
  opacity: 0.65;
  font-size: 0.88em;
}

.quest-stages {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.quest-stage {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  border-left: 3px solid rgba(128, 128, 128, 0.3);
  padding: 4px 10px;
}

.quest-stage-index {
  min-width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8em;
  background: rgba(128, 128, 128, 0.25);
}

.quest-stage-name {
  font-family: monospace;
  font-size: 0.88em;
  opacity: 0.8;
}

.quest-stage-briefing {
  line-height: 1.5;
}

.quest-stage-briefing-en {
  opacity: 0.5;
  font-size: 0.88em;
  font-style: italic;
  line-height: 1.4;
}

.quest-scenes-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.quest-scenes-hint {
  opacity: 0.6;
  margin-bottom: 10px;
}

.quest-scene-group {
  margin-bottom: 14px;
}

.quest-scene-group-title {
  font-family: monospace;
  opacity: 0.7;
  margin-bottom: 6px;
  border-bottom: 1px dashed rgba(128, 128, 128, 0.25);
  display: inline-block;
  padding-bottom: 2px;
}

.quest-scene-group-none {
  opacity: 0.45;
}

.quest-scene-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.quest-scene-btn {
  text-align: left;
}

.quest-scene-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.quest-scene-title {
  font-weight: 500;
}

.quest-scene-location {
  opacity: 0.6;
  font-size: 0.88em;
}

.quest-scene-active-header {
  margin-bottom: 12px;
}

.quest-scene-title-lg {
  font-size: 1.15em;
  font-weight: bold;
}
.quest-scene-btn-auto {
  opacity: 0.75;
}

.quest-auto-block {
  margin-top: 10px;
}
</style>
