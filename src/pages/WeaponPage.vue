<script setup lang="ts">
import ShipsDiv from 'src/components/ShipsDiv.vue';
import { appData } from 'src/AppData';
import { computed, ref } from 'vue';
import { onBeforeRouteUpdate, useRoute } from 'vue-router';
import { debugJson } from 'src/classes/utils';
import WeaponSpriteDiv from 'src/components/WeaponSpriteDiv.vue';
import FactionsDiv from 'src/components/listDiv/FactionsDiv.vue';

defineOptions({
  name: 'WeaponPage',
});

const route = useRoute();
let id = ref(route.params.id as string);
onBeforeRouteUpdate(async (to) => {
  id.value = to.params.id as string;
});

const weapon = computed(() => {
  return appData.getWeaponById(id.value);
});
const ships = computed(() => {
  return appData.getShipsByIds(weapon.value?.shipIds ?? []);
});
const variantShips = computed(() => {
  return appData.getShipsByIds(weapon.value?.variantIds ?? []);
});
</script>

<template>
  <q-page>
    <template v-if="weapon === undefined">
      <h2>ShipSystem id:{{ id }} not found.</h2>
    </template>
    <template v-else>
      <h4>
        {{ weapon.name }}
      </h4>

      <div class="detail-intro-grid">
        <span class="detail-description">{{ weapon.description }}</span>
        <div class="detail-sprite-wrapper">
          <WeaponSpriteDiv :weapon="weapon" />
        </div>
      </div>

      <br /><br />

      <div class="detail-columns-3">
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.primaryRole') }}</div>
          <div>{{ weapon.primaryRoleStr }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.mountType') }}</div>
          <div>{{ `${weapon.size}, ${weapon.mountType}` }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.ordnancePoints') }}</div>
          <div>{{ weapon.ordnancePoint }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.range') }}</div>
          <div>{{ weapon.maxRange }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.damage') }}</div>
          <div>
            {{ weapon.damagePerShot
            }}{{ weapon.burstSize > 1 ? ' x ' + weapon.burstSize : '' }}
          </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.dps') }}</div>
          <div>{{ weapon.dps }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.sustainedDps') }}</div>
          <div>{{ weapon.sustainedDps }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.empDamage') }}</div>
          <div>{{ weapon.empPerShot }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.empDps') }}</div>
          <div>{{ weapon.empPerSecond }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.fluxPerSecond') }}</div>
          <div>{{ weapon.fluxPerSecond }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.sustainedFluxPerSecond') }}</div>
          <div>{{ weapon.sustainedFluxPerSecond }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.fluxPerDamage') }}</div>
          <div>{{ weapon.fluxPerDamage }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.description') }}</div>
          <div>{{ weapon.customPrimary }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.damageType') }}</div>
          <div style="white-space: pre-wrap">
            {{
              weapon.damageType.displayName +
              '\n' +
              weapon.damageType.description
            }}
          </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.speed') }}</div>
          <div>{{ weapon.speedStr }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.tracking') }}</div>
          <div>{{ weapon.trackingStr }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.accuracy') }}</div>
          <div>{{ weapon.accuracyStr }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.turnRate') }}</div>
          <div>{{ weapon.turnRateStr }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.maxAmmo') }}</div>
          <div>{{ weapon.maxAmmo }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.reloadTime') }}</div>
          <div>{{ weapon.reloadTime }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.reloadSize') }}</div>
          <div>{{ weapon.reloadSize }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.refireDelay') }}</div>
          <div>{{ weapon.reFireDelay }}</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('weapon.description') }}</div>
          <div>{{ weapon.customAncillary }}</div>
        </div>
      </div>

      <br /><br />

      <template v-if="ships.length > 0">
        <h4>{{ $t('weapon.usedByHulls') }}</h4>
        <ShipsDiv :ships="ships" />
      </template>

      <br /><br />

      <template v-if="variantShips.length > 0">
        <h4>{{ $t('weapon.usedByVariants') }}</h4>
        <ShipsDiv :ships="variantShips" />
      </template>

      <br /><br />

      <template v-if="weapon.factions.length > 0">
        <h4>{{ $t('weapon.factions') }}</h4>
        <FactionsDiv :faction-values="weapon.factions" img="crest" />
      </template>

      <br /><br />

      <pre v-if="appData.debug"><code>{{ debugJson(weapon) }}</code></pre>
    </template>
  </q-page>
</template>

<style lang="scss" scoped>
.detail-intro-grid {
  display: grid;
  grid-template-columns: 3fr 1fr;
  gap: 10px;
}

.detail-description {
  text-align: left;
  vertical-align: top;
  white-space: pre-wrap;
}

.detail-sprite-wrapper {
  display: flex;
  justify-content: center;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.detail-columns-3 {
  column-count: 3;
}

@media (max-width: 600px) {
  .detail-intro-grid {
    grid-template-columns: 1fr;
  }

  .detail-sprite-wrapper {
    order: -1;
    margin-bottom: 10px;
    justify-content: flex-start;
  }

  .detail-columns-3 {
    column-count: 1;
  }
}
</style>
