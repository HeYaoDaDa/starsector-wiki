<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { appData } from 'src/AppData';

defineOptions({
  name: 'DialogueDictPage',
});

const { locale } = useI18n();
const loading = ref(true);
const search = ref('');
const category = ref('all');
const shown = ref(100);

const isZh = computed(() => locale.value === 'zh');

async function load() {
  loading.value = true;
  await appData.loadDictionary(appData.selectedVersion.value);
  loading.value = false;
}

onMounted(load);
watch(() => appData.selectedVersion.value, load);

const entries = computed(() => appData.dictionary?.entries ?? []);

const categories = computed(() => {
  const cats = new Set<string>();
  for (const e of entries.value) {
    cats.add(e.cat);
  }
  return Array.from(cats).sort();
});

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase();
  let list = entries.value;
  if (category.value !== 'all') {
    list = list.filter((e) => e.cat === category.value);
  }
  if (q) {
    list = list.filter(
      (e) =>
        e.id.toLowerCase().includes(q) ||
        e.zh.toLowerCase().includes(q) ||
        e.en.toLowerCase().includes(q) ||
        e.o.some((o) => o.zh.toLowerCase().includes(q) || o.en.toLowerCase().includes(q))
    );
  }
  return list;
});

const visible = computed(() => filtered.value.slice(0, shown.value));

const STAGE_RE = /^\$\w+_stage == (\S+)$/;
const FLAG_RE = /^(!?)\$(\S+)$/;

function condLabel(raw: string): string {
  const c = raw.trim();
  const neg = c.startsWith('!');
  const body = neg ? c.slice(1) : c;
  const stageM = body.match(STAGE_RE);
  if (stageM) {
    return `${neg ? '¬ ' : ''}${stageM[1]}`;
  }
  const m = body.match(FLAG_RE);
  if (m) {
    return `${neg ? '¬' : ''}$${m[2]}`;
  }
  return c;
}
</script>

<template>
  <q-page padding>
    <div v-if="loading" class="dict-loading">{{ $t('common.loading') }}</div>
    <template v-else>
      <div class="dict-toolbar">
        <q-input
          v-model="search"
          dense
          clearable
          class="dict-search"
          :placeholder="$t('dict.searchPlaceholder')"
        >
          <template v-slot:prepend><q-icon name="search" /></template>
        </q-input>
        <q-select
          v-model="category"
          dense
          clearable
          emit-value
          map-options
          :options="[
            { label: $t('dict.category.all'), value: 'all' },
            ...categories
              .filter((c) => c !== 'all')
              .map((c) => ({ label: $t(`dict.cat.${c}`), value: c })),
          ]"
          class="dict-cat"
        />
      </div>

      <div class="result-count">
        {{ $t('dict.entries', { count: filtered.length }) }}
      </div>

      <div v-if="filtered.length === 0" class="dict-loading">
        {{ $t('dict.noResults') }}
      </div>

      <div v-for="e in visible" :key="e.id" class="dict-entry">
        <div class="dict-entry-head">
          <span class="dict-entry-id">{{ e.id }}</span>
          <q-chip dense size="sm">{{ $t(`dict.cat.${e.cat}`) }}</q-chip>
          <q-chip dense size="sm" outline>{{ e.t }}</q-chip>
        </div>
        <div v-if="e.c.length > 0" class="dict-entry-conds">
          <q-chip v-for="(c, i) in e.c.slice(0, 6)" :key="i" dense size="sm" color="grey-6" text-color="white">
            {{ condLabel(c) }}
          </q-chip>
          <span v-if="e.c.length > 6" class="dict-more">+{{ e.c.length - 6 }}</span>
        </div>
        <div v-if="e.zh" class="dict-text">{{ isZh ? e.zh : e.en }}</div>
        <div v-if="e.zh && e.en && e.zh !== e.en" class="dict-text-en">
          {{ isZh ? e.en : e.zh }}
        </div>
        <div v-for="o in e.o" :key="o.id" class="dict-option">
          <span class="dict-option-arrow">▸</span>
          {{ isZh ? o.zh : o.en }}
        </div>
      </div>

      <div v-if="filtered.length > shown" class="dict-more-row">
        <q-btn no-caps outline @click="shown += 200">
          {{ $t('dict.showMore', { shown: Math.min(shown + 200, filtered.length) }) }}
        </q-btn>
      </div>
    </template>
  </q-page>
</template>

<style scoped lang="scss">
.dict-loading {
  opacity: 0.7;
  padding: 16px;
}

.dict-toolbar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.dict-search {
  flex: 1;
  min-width: 220px;
}

.dict-cat {
  min-width: 200px;
}

.dict-entry {
  border: 1px solid rgba(128, 128, 128, 0.25);
  border-radius: 6px;
  padding: 8px 12px;
  margin-bottom: 8px;
}

.dict-entry-head {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.dict-entry-id {
  font-family: monospace;
  font-size: 0.85em;
  opacity: 0.75;
}

.dict-entry-conds {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  margin: 2px 0;
}

.dict-more {
  opacity: 0.5;
  font-size: 0.8em;
}

.dict-text {
  white-space: pre-wrap;
  line-height: 1.5;
}

.dict-text-en {
  white-space: pre-wrap;
  line-height: 1.4;
  opacity: 0.5;
  font-size: 0.9em;
  font-style: italic;
}

.dict-option {
  padding-left: 8px;
  opacity: 0.9;
}

.dict-option-arrow {
  opacity: 0.5;
  margin-right: 4px;
}

.dict-more-row {
  display: flex;
  justify-content: center;
  padding: 12px;
}
</style>
