<script setup lang="ts">
import { appData } from 'src/AppData';
import { computed, ref } from 'vue';
import { onBeforeRouteUpdate, useRoute } from 'vue-router';
import { debugJson } from 'src/classes/utils';
import PlanetsDiv from 'src/components/listDiv/PlanetsDiv.vue';

defineOptions({
  name: 'MarketConditionPage',
});

const route = useRoute();
let id = ref(route.params.id as string);
onBeforeRouteUpdate(async (to) => {
  id.value = to.params.id as string;
});

const marketCondition = computed(() => {
  return appData.getMarketConditionById(id.value);
});
</script>

<template>
  <q-page>
    <template v-if="marketCondition === undefined">
      <h2>MarketCondition id:{{ id }} not found.</h2>
    </template>
    <template v-else>
      <h4>
        {{ marketCondition.name }}
      </h4>

      <div class="detail-intro-grid" style="grid-template-columns: 3fr 2fr">
        <span class="detail-description">{{ marketCondition.desc }}</span>
        <div class="detail-sprite-wrapper">
          <div style="margin: auto">
            <img decoding="async" :src="marketCondition.icon" />
          </div>
        </div>
      </div>

      <br /><br />

      <div class="detail-columns-2">
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('marketCondition.order') }}</div>
          <div>{{ marketCondition.order }}</div>
        </div>
      </div>

      <br /><br />

      <template v-if="marketCondition.planets.length > 0">
        <h4>{{ $t('marketCondition.colonies') }}</h4>
        <PlanetsDiv :planet-values="marketCondition.planets" />
      </template>

      <br /><br />

      <pre
        v-if="appData.debug"
      ><code>{{ debugJson(marketCondition) }}</code></pre>
    </template>
  </q-page>
</template>
