<script setup lang="ts">
import MutableStatDiv from 'src/components/MutableStatDiv.vue';
import ShipsDiv from 'src/components/ShipsDiv.vue';
import { appData } from 'src/AppData';
import { computed, ref } from 'vue';
import { onBeforeRouteUpdate, useRoute } from 'vue-router';
import { debugJson } from 'src/classes/utils';
import ShipSpriteDiv from 'src/components/ShipSpriteDiv.vue';
import FactionsDiv from 'src/components/listDiv/FactionsDiv.vue';

defineOptions({
  name: 'ShipPage',
});

const route = useRoute();
let id = ref(route.params.id as string);
onBeforeRouteUpdate(async (to) => {
  id.value = to.params.id as string;
});
const ship = computed(() => appData.getShipById(id.value));
const skins = computed(() => appData.getShipsByIds(ship.value?.skinIds ?? []));
const variants = computed(() =>
  appData.getShipsByIds(ship.value?.varinatIds ?? [])
);
</script>

<template>
  <q-page padding>
    <template v-if="ship === undefined">
      <h2>{{ $t('common.notFound', { name: 'Ship', id: id }) }}</h2>
    </template>
    <template v-else>
      <h4>
        {{ ship.getDisplayName($t) }}
      </h4>

      <div class="detail-intro-grid">
        <span class="detail-description">{{ ship.description }}</span>
        <div class="detail-sprite-wrapper">
          <ShipSpriteDiv :ship="ship" />
        </div>
      </div>

      <br /><br />

      <div class="detail-table-wrapper">
      <table>
        <colgroup>
          <col style="width: 21%" />
          <col style="width: 13%" />
          <col style="width: 20%" />
          <col style="width: 13%" />
          <col style="width: 20%" />
          <col style="width: 13%" />
        </colgroup>
        <thead>
          <tr>
            <th colspan="4" style="text-align: center">{{ $t('ship.logistics') }}</th>
            <th colspan="2" style="text-align: center">{{ $t('ship.combat') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{{ $t('ship.crCost') }}</td>
            <td style="text-align: right">{{ ship.crToDeploy }}%</td>
            <td>{{ $t('ship.suppliesPerMonth') }}</td>
            <td style="text-align: right">
              <MutableStatDiv
                :stat="ship.suppliesPerMonth"
                :add-is-good="false"
              />
            </td>
            <td>{{ $t('ship.hull') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.hitPoints" />
            </td>
          </tr>
          <tr>
            <td>{{ $t('ship.crRecovery') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.repairPercentPerDay" />%
            </td>
            <td>{{ $t('ship.cargo') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.cargo" />
            </td>
            <td>{{ $t('ship.armor') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.armorRating" />
            </td>
          </tr>
          <tr>
            <td>{{ $t('ship.deployCost') }}</td>
            <td style="text-align: right">
              <MutableStatDiv
                :stat="ship.suppliesToRecover"
                :add-is-good="false"
              />
            </td>
            <td>{{ $t('ship.maxCrew') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.maxCrew" />
            </td>
            <td>{{ $t('ship.defenseType') }}</td>
            <td style="text-align: right">
              {{ $t('shield.' + ship.shieldType.toLowerCase()) }}
            </td>
          </tr>
          <!-- ordnancePoints(部署点) 与 deployment cost 共用 suppliesToRecover 字段 -->
          <tr>
            <td>{{ $t('ship.ordnancePoints') }}</td>
            <td style="text-align: right">
              <MutableStatDiv
                :stat="ship.suppliesToRecover"
                :add-is-good="false"
              />
            </td>
            <td>{{ $t('ship.minCrew') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.minCrew" :add-is-good="false" />
            </td>
            <td>
              {{
                ship.hasShield()
                  ? $t('ship.shieldAngle')
                  : ship.hasPhase()
                  ? $t('ship.phaseActivation')
                  : ''
              }}
            </td>
            <td style="text-align: right">
              <MutableStatDiv v-if="ship.hasShield()" :stat="ship.shieldArc" />
              <MutableStatDiv
                v-else-if="ship.hasPhase()"
                :stat="ship.phaseCost"
                :add-is-good="false"
              />
            </td>
          </tr>
          <tr>
            <td>{{ $t('ship.peakTime') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.noCRLossSeconds" />
            </td>
            <td>{{ $t('ship.fuelCapacity') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.fuel" />
            </td>
            <td>
              {{
                ship.hasShield()
                  ? $t('ship.shieldUpkeep')
                  : ship.hasPhase()
                  ? $t('ship.phaseUpkeep')
                  : ''
              }}
            </td>
            <td style="text-align: right">
              <MutableStatDiv
                v-if="ship.hasShield()"
                :stat="ship.shieldUpkeep"
                :add-is-good="false"
              />
              <MutableStatDiv
                v-else-if="ship.hasPhase()"
                :stat="ship.phaseUpKeep"
                :add-is-good="false"
              />
            </td>
          </tr>
          <tr>
            <td></td>
            <td style="text-align: right"></td>
            <td>{{ $t('ship.maxBurn') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.maxBurn" />
            </td>
            <td>
              {{ ship.hasShield() ? $t('ship.shieldEfficiency') : '' }}
            </td>
            <td style="text-align: right">
              <MutableStatDiv
                v-if="ship.hasShield()"
                :stat="ship.fluxPerDamageAbsorbed"
                :add-is-good="false"
              />
            </td>
          </tr>
          <tr>
            <td></td>
            <td style="text-align: right"></td>
            <td>{{ $t('ship.fuelPerLY') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.fuelPerLY" :add-is-good="false" />
            </td>
            <td>{{ $t('ship.fluxCapacity') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.fluxCapacity" />
            </td>
          </tr>
          <tr>
            <td></td>
            <td style="text-align: right"></td>
            <td></td>
            <td style="text-align: right"></td>
            <td>{{ $t('ship.fluxDissipation') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.fluxDissipation" />
            </td>
          </tr>
          <tr>
            <td>{{ $t('ship.opPoints') }}</td>
            <td style="text-align: right">{{ ship.ordnancePoints }}</td>
            <td>{{ $t('ship.sensorProfile') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.sensorProfile" :add-is-good="false" />
            </td>
            <td>{{ $t('ship.maxSpeed') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.maxSpeed" />
            </td>
          </tr>
          <tr>
            <td></td>
            <td></td>
            <td>{{ $t('ship.sensorStrength') }}</td>
            <td style="text-align: right">
              <MutableStatDiv :stat="ship.sensorStrength" />
            </td>
            <td></td>
            <td style="text-align: right"></td>
          </tr>
          <tr>
            <td>{{ $t('ship.tacticalSystem') }}</td>
            <td colspan="5">
              <router-link
                v-if="ship.getSystem()"
                :to="{
                  name: 'ship_system',
                  params: { id: ship?.shipSystemId },
                }"
                >{{ ship.getSystem()?.name }}</router-link
              >
            </td>
            <td></td>
          </tr>
          <tr v-if="ship.hasSystem()">
            <td></td>
            <td colspan="5" style="white-space: pre-wrap">
              {{ ship.getSystemDescription($t) }}
            </td>
          </tr>
          <tr>
            <td>{{ $t('ship.specialSystem') }}</td>
            <td colspan="5">
              <router-link
                v-if="ship.getDefense()"
                :to="{
                  name: 'ship_system',
                  params: { id: ship?.shipDefenseId },
                }"
                >{{ ship.getDefense()?.name ?? $t('common.none') }}</router-link
              >
            </td>
          </tr>
          <tr v-if="ship.hasDefense()">
            <td></td>
            <td colspan="5" style="white-space: pre-wrap">
              {{ ship.getDefenseDescription($t) }}
            </td>
          </tr>
          <tr>
            <td>{{ $t('ship.slots') }}</td>
            <td colspan="5">{{ ship.getSlotDescription($t) }}</td>
          </tr>
          <tr>
            <td>{{ $t('ship.armament') }}</td>
            <td colspan="5">
              <span
                style="margin-right: 10px"
                v-for="weapon in ship.getWeapons()"
                :key="weapon.id"
              >
                {{ weapon.count }}x
                <router-link
                  v-if="weapon.id != weapon.name"
                  :to="{ name: 'weapon', params: { id: weapon.id } }"
                >
                  {{ weapon.name }}
                </router-link>
                <span v-else>{{ weapon.name }}</span>
              </span>
            </td>
          </tr>
          <tr>
            <td>{{ $t('ship.hullMods') }}</td>
            <td colspan="5">
              <span
                style="margin-right: 10px"
                v-for="shipMod in ship.getShipMods()"
                :key="shipMod.id"
              >
                <router-link
                  v-if="shipMod.id != shipMod.name"
                  :to="{ name: 'ship_mod', params: { id: shipMod.id } }"
                >
                  {{ shipMod.name }}
                </router-link>
                <span v-else>{{ shipMod.name }}</span>
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      </div>

      <br />
      <div class="detail-columns-2">
        <div style="display: grid; grid-template-columns: 1fr 1fr">
          <div>{{ $t('ship.value') }}</div>
          <div>{{ ship.baseValue }}</div>
        </div>
      </div>

      <br /><br />

      <template v-if="skins.length > 0">
        <h4>{{ $t('ship.skins') }}</h4>
        <ShipsDiv :ships="skins" />
      </template>

      <br /><br />

      <template v-if="variants.length > 0">
        <h4>{{ $t('ship.variants') }}</h4>
        <ShipsDiv :ships="variants" />
      </template>

      <br /><br />

      <template v-if="ship.factions.length > 0">
        <h4>{{ $t('ship.factions') }}</h4>
        <FactionsDiv :faction-values="ship.factions" img="crest" />
      </template>

      <br /><br />

      <pre v-if="appData.debug"><code>{{ debugJson(ship) }}</code></pre>
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

.detail-table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.detail-table-wrapper table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  min-width: 640px;
}

td {
  border: 1px solid;
}

th {
  border: 1px solid;
}

img {
  display: block;
}

.detail-columns-2 {
  column-count: 2;
}

// Responsive: mobile
@media (max-width: 600px) {
  .detail-intro-grid {
    grid-template-columns: 1fr;
  }

  .detail-sprite-wrapper {
    order: -1;
    margin-bottom: 10px;
    justify-content: flex-start;
  }

  .detail-columns-2 {
    column-count: 1;
  }
}
</style>
