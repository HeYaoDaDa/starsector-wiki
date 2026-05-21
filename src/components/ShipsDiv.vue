<script setup lang="ts">
import { Ship } from 'src/classes/model/ship';
import ShipSpriteDiv from './ShipSpriteDiv.vue';
import { computed, ref } from 'vue';
import { appData } from 'src/AppData';
import { compareShip } from 'src/classes/utils';
import { useQuasar } from 'quasar';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

defineOptions({
  name: 'ShipsDiv',
});

interface Props {
  ships: (Ship | string)[];
  hiddenOptions?: boolean;
}
const { ships, hiddenOptions = false } = defineProps<Props>();
const $q = useQuasar();

const includeFilters = ref<string[]>(['type:normal']);
const excludeFilters = ref<string[]>([]);
const rowTypeOptions = computed(() => [
  { label: t('filter.type.normal'), value: 'normal' },
  { label: t('filter.type.station'), value: 'station' },
  { label: t('filter.type.module'), value: 'module' },
]);

const allShips = computed(() =>
  ships
    .map((it) => (typeof it === 'string' ? appData.getShipById(it) : it))
    .filter((it) => it !== undefined)
    .sort(compareShip)
);

const finalShips = computed(() => {
  let result = allShips.value;

  // 应用包含条件 - 必须满足所有包含条件（且关系）
  if (includeFilters.value && includeFilters.value.length > 0) {
    result = result.filter((ship) => {
      return includeFilters.value.every((filter) => matchesFilter(ship, filter));
    });
  }

  // 应用排除条件 - 只要匹配任一排除条件就排除（或关系）
  if (excludeFilters.value && excludeFilters.value.length > 0) {
    result = result.filter((ship) => {
      return !excludeFilters.value.some((filter) => matchesFilter(ship, filter));
    });
  }

  return result;
});

// 为包含条件下拉框生成选项（基于当前已筛选的结果）
const includeFilterOptions = computed(() => {
  // 使用当前筛选结果作为基础
  const baseShips = finalShips.value;
  return generateFilterOptions(baseShips, includeFilters.value, excludeFilters.value);
});

// 为排除条件下拉框生成选项（基于当前已筛选的结果）
const excludeFilterOptions = computed(() => {
  // 使用当前筛选结果作为基础
  const baseShips = finalShips.value;
  return generateFilterOptions(baseShips, excludeFilters.value, includeFilters.value);
});

function generateFilterOptions(ships: Ship[], selectedFilters: string[], oppositeFilters: string[]) {
  const options: Array<{
    label: string;
    value: string;
    chipLabel: string;
    disable: boolean;
  }> = [];

  // 类型选项
  rowTypeOptions.value.forEach((opt) => {
    const filterValue = `type:${opt.value}`;

    // 计算符合这个条件的船只数量
    let count = 0;
    if (opt.value === 'station') count = ships.filter((s) => s.station).length;
    else if (opt.value === 'module') count = ships.filter((s) => s.isModule).length;
    else if (opt.value === 'normal') count = ships.filter((s) => !s.station && !s.isModule).length;

    // 检查是否在当前或对面的下拉框中被选中
    const isSelected = selectedFilters && selectedFilters.includes(filterValue);
    const isSelectedInOpposite = oppositeFilters && oppositeFilters.includes(filterValue);

    options.push({
      label: t('filter.optionFormat', { category: t('filter.label.type'), name: opt.label, count }),
      value: filterValue,
      chipLabel: t('filter.chipFormat', { category: t('filter.label.type'), name: opt.label }),
      // 禁用条件：(未被当前选中且数量为0) 或 (被对面选中)
      disable: (!isSelected && count === 0) || isSelectedInOpposite,
    });
  });

  // 大小选项
  const sizes = Array.from(new Set(allShips.value.map((it) => it.size)));
  sizes.forEach((size) => {
    const label = t('size.' + size.toLowerCase());
    const filterValue = `size:${size}`;

    const count = ships.filter((s) => s.size === size).length;
    const isSelected = selectedFilters && selectedFilters.includes(filterValue);
    const isSelectedInOpposite = oppositeFilters && oppositeFilters.includes(filterValue);

    options.push({
      label: t('filter.optionFormat', { category: t('filter.label.size'), name: label, count }),
      value: filterValue,
      chipLabel: t('filter.chipFormat', { category: t('filter.label.size'), name: label }),
      disable: (!isSelected && count === 0) || isSelectedInOpposite,
    });
  });

  // 设计类型选项
  const manufacturers = Array.from(
    new Set(allShips.value.map((it) => it.manufacturer ?? null))
  ).sort((a, b) => {
    const left = a ?? '';
    const right = b ?? '';
    return left.localeCompare(right);
  });

  manufacturers.forEach((manufacturer) => {
    const label = manufacturer && manufacturer.length > 0 ? manufacturer : t('common.unknown');
    const filterValue = `manufacturer:${manufacturer ?? 'null'}`;

    const count = ships.filter((s) => (s.manufacturer ?? null) === manufacturer).length;
    const isSelected = selectedFilters && selectedFilters.includes(filterValue);
    const isSelectedInOpposite = oppositeFilters && oppositeFilters.includes(filterValue);

    options.push({
      label: t('filter.optionFormat', { category: t('filter.label.designType'), name: label, count }),
      value: filterValue,
      chipLabel: t('filter.chipFormat', { category: t('filter.label.designType'), name: label }),
      disable: (!isSelected && count === 0) || isSelectedInOpposite,
    });
  });

  return options;
}

function matchesFilter(ship: Ship, filter: string): boolean {
  const [category, value] = filter.split(':');

  if (category === 'type') {
    if (value === 'station') return ship.station;
    if (value === 'module') return ship.isModule;
    if (value === 'normal') return !ship.station && !ship.isModule;
  } else if (category === 'size') {
    return ship.size === value;
  } else if (category === 'manufacturer') {
    const manufacturerValue = value === 'null' ? null : value;
    return (ship.manufacturer ?? null) === manufacturerValue;
  }

  return false;
}


</script>

<template>
  <div v-if="!hiddenOptions" class="filter-toolbar">
    <div class="filter-row">
      <div class="filter-group">
        <div class="filter-item">
          <div class="filter-item-label">{{ $t('filter.include') }}</div>
          <q-select v-model="includeFilters" :options="includeFilterOptions" multiple emit-value map-options use-chips
            dense options-dense :behavior="$q.screen.lt.sm ? 'dialog' : 'menu'" clearable clear-icon="close"
            :placeholder="$t('filter.includePlaceholder')">
            <template v-slot:selected-item="scope">
              <q-chip removable dense @remove="scope.removeAtIndex(scope.index)" :tabindex="scope.tabindex"
                color="primary" text-color="white">
                {{ scope.opt.chipLabel || scope.opt.label }}
              </q-chip>
            </template>
          </q-select>
        </div>
        <div class="filter-item">
          <div class="filter-item-label">{{ $t('filter.exclude') }}</div>
          <q-select v-model="excludeFilters" :options="excludeFilterOptions" multiple emit-value map-options use-chips
            dense options-dense :behavior="$q.screen.lt.sm ? 'dialog' : 'menu'" clearable clear-icon="close"
            :placeholder="$t('filter.excludePlaceholder')">
            <template v-slot:selected-item="scope">
              <q-chip removable dense @remove="scope.removeAtIndex(scope.index)" :tabindex="scope.tabindex"
                color="negative" text-color="white">
                {{ scope.opt.chipLabel || scope.opt.label }}
              </q-chip>
            </template>
          </q-select>
        </div>
      </div>
    </div>
  </div>

  <div v-if="!hiddenOptions" class="result-count">
    {{ $t('filter.results', { count: finalShips.length }) }}
  </div>

  <div class="card-item-list-page">
    <q-btn no-caps flat class="card-item" style="align-self: stretch" v-for="ship in finalShips" :key="ship.id"
      :to="{ name: 'ship', params: { id: ship.id } }">
      <div class="card-item-content">
        <ShipSpriteDiv :ship="ship" />
              <span> {{ ship.getDisplayName(t) }} </span>
      </div>
    </q-btn>
  </div>
</template>
