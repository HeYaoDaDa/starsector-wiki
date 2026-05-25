<script setup lang="ts">
import ShipsDiv from 'src/components/ShipsDiv.vue';
import { appData } from 'src/AppData';
import { computed, ref } from 'vue';
import { onBeforeRouteUpdate, useRoute } from 'vue-router';
import { debugJson } from 'src/classes/utils';
import FactionsDiv from 'src/components/listDiv/FactionsDiv.vue';

defineOptions({
  name: 'ShipModPage',
});

const route = useRoute();
let id = ref(route.params.id as string);
onBeforeRouteUpdate(async (to) => {
  id.value = to.params.id as string;
});

const shipMod = computed(() => {
  return appData.getShipModById(id.value);
});
const ships = computed(() => {
  return appData.getShipsByIds(shipMod.value?.shipIds ?? []);
});
const variantShips = computed(() => {
  return appData.getShipsByIds(shipMod.value?.variantIds ?? []);
});
</script>

<template>
  <q-page>
    <template v-if="shipMod === undefined">
      <h2>ShipMod id:{{ id }} not found.</h2>
    </template>
    <template v-else>
      <h4>
        {{ shipMod.name }}
      </h4>

      <div class="detail-intro-grid" style="grid-template-columns: 3fr 2fr">
        <span class="detail-description">{{ shipMod.description }}</span>
        <div class="detail-sprite-wrapper">
          <div style="margin: auto">
            <img
              style="background-color: black"
              decoding="async"
              :src="shipMod.icon"
            />
          </div>
        </div>
      </div>

      <br /><br />

      <div>
        <div style="display: grid; grid-template-columns: 1fr 9fr">
          <div>{{ $t('hullMod.designType') }}</div>
          <div>{{ shipMod.manufacturer ?? $t('common.generic') }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 9fr">
          <div>{{ $t('hullMod.shipSize') }}</div>
          <div>{{ $t('hullMod.opCost') }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 9fr">
          <div>{{ $t('hullMod.frigate') }}</div>
          <div>{{ shipMod.frigateCost }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 9fr">
          <div>{{ $t('hullMod.destroyer') }}</div>
          <div>{{ shipMod.destroyerCost }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 9fr">
          <div>{{ $t('hullMod.cruiser') }}</div>
          <div>{{ shipMod.cruiserCost }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 9fr">
          <div>{{ $t('hullMod.capital') }}</div>
          <div>{{ shipMod.capitalCost }}</div>
        </div>
      </div>

      <br /><br />

      <template v-if="ships.length > 0">
        <h4>{{ $t('hullMod.usedByHulls') }}</h4>
        <ShipsDiv :ships="ships" />
      </template>

      <br /><br />

      <template v-if="variantShips.length > 0">
        <h4>{{ $t('hullMod.usedByVariants') }}</h4>
        <ShipsDiv :ships="variantShips" />
      </template>

      <br /><br />

      <template v-if="shipMod.factions.length > 0">
        <h4>{{ $t('hullMod.factions') }}</h4>
        <FactionsDiv :faction-values="shipMod.factions" img="crest" />
      </template>

      <br /><br />

      <pre v-if="appData.debug"><code>{{ debugJson(shipMod) }}</code></pre>
    </template>
  </q-page>
</template>
