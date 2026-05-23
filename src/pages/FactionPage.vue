<script setup lang="ts">
import { appData } from 'src/AppData';
import { computed, ref } from 'vue';
import { onBeforeRouteUpdate, useRoute } from 'vue-router';
import { debugJson } from 'src/classes/utils';
import ShipsDiv from 'src/components/ShipsDiv.vue';
import WeaponsDiv from 'src/components/listDiv/WeaponsDiv.vue';
import ShipModsDiv from 'src/components/listDiv/ShipModsDiv.vue';
import PlanetsDiv from 'src/components/listDiv/PlanetsDiv.vue';
import PersonsDiv from 'src/components/listDiv/PersonsDiv.vue';

defineOptions({
  name: 'FactionPage',
});

const route = useRoute();
let id = ref(route.params.id as string);
onBeforeRouteUpdate(async (to) => {
  id.value = to.params.id as string;
});

const faction = computed(() => {
  return appData.getFactionById(id.value);
});
</script>

<template>
  <q-page>
    <template v-if="faction === undefined">
      <h2>Faction id:{{ id }} not found.</h2>
    </template>
    <template v-else>
      <h4>
        {{ faction.displayName }}
      </h4>

      <div class="detail-intro-grid" style="grid-template-columns: 3fr 2fr">
        <span class="detail-description">{{ faction.description }}</span>
        <div class="detail-sprite-wrapper">
          <div style="margin: auto">
            <img decoding="async" :src="faction.logo" />
          </div>
        </div>
      </div>

      <br /><br />

      <div>
        <div style="display: grid; grid-template-columns: 1fr 6fr">
          <div>{{ $t('faction.name') }}</div>
          <div>{{ faction.displayNameLong }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 6fr">
          <div>{{ $t('faction.personNamePrefix') }}</div>
          <div>{{ faction.personNamePrefix }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 6fr">
          <div>{{ $t('faction.shipNamePrefix') }}</div>
          <div>{{ faction.shipNamePrefix }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 6fr">
          <div>{{ $t('faction.relationship') }}</div>
          <div>
            <q-btn
              v-for="[
                factionId,
                relationship,
              ] in faction.relationshipMap.entries()"
              :key="factionId"
              :to="{ name: 'faction', params: { id: factionId } }"
            >
              <img
                style="width: 64px; height: 40px"
                :src="appData.getFactionById(factionId)?.logo"
              />
              {{ appData.getFactionById(factionId)?.displayName }} :
              {{ Math.floor(relationship * 100) }}
            </q-btn>
          </div>
        </div>
      </div>

      <br /><br />

      <template v-if="faction.planets.length > 0">
        <h4>{{ $t('faction.colonies') }}</h4>
        <PlanetsDiv :planet-values="faction.planets" />
      </template>

      <br /><br />

      <template v-if="faction.persons.length > 0">
        <h4>{{ $t('faction.persons') }}</h4>
        <PersonsDiv :person-values="faction.persons" />
      </template>

      <br /><br />
      <template v-if="faction.knownShipIds.length > 0">
        <h4>{{ $t('faction.ships') }}</h4>
        <ShipsDiv
          :ships="
            appData.getShipsByIds(
              faction.knownShipIds.map((it) => it + '_Hull')
            )
          "
        />
      </template>

      <br /><br />
      <template v-if="faction.knownFighterIds.length > 0">
        <h4>{{ $t('faction.fighters') }}</h4>
        <ShipsDiv
          :ships="
            appData.getShipsByIds(
              faction.knownFighterIds.map((it) => it.replace('_wing', '_Hull'))
            )
          "
        />
      </template>

      <br /><br />
      <template v-if="faction.knownWeaponIds.length > 0">
        <h4>{{ $t('faction.weapons') }}</h4>
        <WeaponsDiv :weaponValues="faction.knownWeaponIds" />
      </template>

      <br /><br />
      <template v-if="faction.knownHullModIds.length > 0">
        <h4>{{ $t('faction.hullMods') }}</h4>
        <ShipModsDiv :shipModValues="faction.knownHullModIds" />
      </template>

      <br /><br />

      <pre v-if="appData.debug"><code>{{ debugJson(faction) }}</code></pre>
    </template>
  </q-page>
</template>
