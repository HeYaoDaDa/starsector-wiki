<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { appData } from 'src/AppData';
import {
  Bilingual,
  DialogueOption,
  DialogueStep,
  Quest,
  QuestScene,
} from 'src/classes/model/Quest';

defineOptions({
  name: 'QuestDialogue',
});

interface Props {
  quest: Quest;
  scene: QuestScene;
}
const props = defineProps<Props>();

const { t, locale } = useI18n();

/** 路径栈: 访问过的步骤 + 说话人 */
interface PathEntry {
  stepId: string;
  speakerId: string | null;
  chosenLabel?: Bilingual;
}
const path = ref<PathEntry[]>([]);

const entryIndex = ref<number>(0);

const entryStepId = computed(
  () => props.scene.entries[entryIndex.value] ?? props.scene.entries[0]
);

const currentStepId = ref<string>(entryStepId.value);

const step = computed<DialogueStep | undefined>(
  () => props.scene.steps[currentStepId.value]
);

const atEntry = computed(() => path.value.length === 0);

const isZh = computed(() => locale.value === 'zh');

function primary(text: Bilingual): string {
  return isZh.value ? text.zh : text.en;
}
function secondary(text: Bilingual): string {
  return isZh.value ? text.en : text.zh;
}

/** 步骤说话人: 场景默认 + 中枢覆盖；响应步骤沿用来源步骤的说话人 */
function speakerFor(stepId: string, fallback: string | null): string | null {
  if (stepId.startsWith('T:')) {
    const trig = stepId.slice(2);
    const override = props.scene.speakerOverrides[trig];
    if (override !== undefined) {
      return override;
    }
  }
  if (stepId.startsWith('S:')) {
    return props.scene.speaker;
  }
  return fallback;
}

const speaker = computed(() => {
  const entry = path.value[path.value.length - 1];
  if (!entry) {
    return null;
  }
  return entry.speakerId;
});

const speakerName = computed(() => {
  const id = speaker.value;
  if (!id) {
    return t('quest.narrator');
  }
  const c = props.quest.characters.find((it) => it.id === id);
  return c ? primary(c.name) : id;
});

watch(
  () => props.scene.id,
  () => {
    path.value = [];
    entryIndex.value = 0;
    currentStepId.value = entryStepId.value;
  }
);

function selectEntry(index: number) {
  entryIndex.value = index;
  path.value = [];
  currentStepId.value = entryStepId.value;
}

function entryLabel(index: number): string {
  const sid = props.scene.entries[index];
  const st = props.scene.steps[sid];
  if (st && st.texts.length > 0) {
    const text = primary(st.texts[0]);
    return text.replace(/\s+/g, ' ').slice(0, 28) + (text.length > 28 ? '…' : '');
  }
  return sid.slice(2);
}

function pushStep(stepId: string, chosenLabel?: Bilingual) {
  const parent = path.value[path.value.length - 1];
  const entry: PathEntry = {
    stepId,
    speakerId: speakerFor(stepId, parent?.speakerId ?? props.scene.speaker),
    chosenLabel,
  };
  path.value.push(entry);
  currentStepId.value = stepId;
}

function chooseOption(option: DialogueOption) {
  if (!option.target) {
    return;
  }
  pushStep(option.target, { en: option.en, zh: option.zh });
}

function continueTo(stepId: string) {
  pushStep(stepId);
}

function goBack(index: number) {
  path.value = path.value.slice(0, index + 1);
  currentStepId.value = path.value[index].stepId;
}

function reset() {
  path.value = [];
  currentStepId.value = entryStepId.value;
}

// -- 文本中的 $变量 高亮 ----------------------------------------------------
const VAR_RE = /\$[A-Za-z_][A-Za-z0-9_.]*/g;

interface TextSegment {
  kind: 'text' | 'var';
  value: string;
}

function splitVars(text: string): TextSegment[] {
  const out: TextSegment[] = [];
  let last = 0;
  for (const m of text.matchAll(VAR_RE)) {
    const idx = m.index ?? 0;
    if (idx > last) {
      out.push({ kind: 'text', value: text.slice(last, idx) });
    }
    out.push({ kind: 'var', value: m[0] });
    last = idx + m[0].length;
  }
  if (last < text.length) {
    out.push({ kind: 'text', value: text.slice(last) });
  }
  return out;
}

// -- 条件的人类可读化 --------------------------------------------------------
const STAGE_RE = /^\$sdtu_stage\s*==\s*(\S+)$/;
const NEG_FLAG_RE = /^(!?)\$(\S+)$/;
const FACTION_RE = /^\$faction\.id\s*==\s*(\S+)$/;
const PLAYER_COMMISSION_RE = /^\$player\.fcm_faction\s*==\s*(\S+)$/;
const PLAYER_COMMISSION_NE_RE = /^\$player\.fcm_faction\s*!=\s*(\S+)$/;
const COMMISSION_ID_RE = /^\$player\.commissionFactionId\s*==\s*(\S+)$/;
const MARKET_RE = /^\$market\.id\s*==\s*(\S+)$/;
const MENU_RE = /^\$menuState\s*==\s*main$/;
const PROB_RE = /^RollProbability\s+([\d.]+)/;
const DAYS_RE = /^\$global\.daysSinceStart\s*>\s*(\d+)$/;
const PERSON_RE = /^\$id\s*==\s*(\S+)$/;
const REP_GTE_RE = /^RepGTE\s+\S+\s+(\S+)$/;
const REP_LTE_RE = /^RepLTE\s+\S+\s+(\S+)$/;
const REP_GTE_FACTION_RE = /^RepGTE\s+(\S+)\s+(\S+)$/;
const REP_LTE_FACTION_RE = /^RepLTE\s+(\S+)\s+(\S+)$/;
const HOSTILE_RE = /^\$faction\.isHostile$/;

interface CondChip {
  label: string;
  known: boolean;
}

/** 把一条原始条件翻译为可读文本（通用条件 + 任务 flag 术语表 + 原样兜底） */
function describeCondition(raw: string): CondChip {
  const c = raw.trim();
  if (!c) {
    return { label: '', known: true };
  }

  // 阶段条件
  const stageM = c.match(STAGE_RE);
  if (stageM) {
    return { label: t('quest.stageHint', { stage: stageM[1] }), known: true };
  }

  // 通用市场/势力/人物条件
  const neg = c.startsWith('!');
  const body = neg ? c.slice(1) : c;
  const applyNeg = (label: string, known = true): CondChip => ({
    label: neg ? t('cond.negated', { text: label }) : label,
    known,
  });

  if (MENU_RE.test(body) || body === '$hasMarket') {
    return applyNeg(t('cond.marketMenu'));
  }
  const probM = body.match(PROB_RE);
  if (probM) {
    return {
      label: t('cond.random', { pct: Math.round(parseFloat(probM[1]) * 100) }),
      known: true,
    };
  }
  const daysM = body.match(DAYS_RE);
  if (daysM) {
    return applyNeg(t('cond.daysSince', { days: daysM[1] }));
  }
  const facM = body.match(FACTION_RE);
  if (facM) {
    const fac = appData.getFactionById(facM[1]);
    return applyNeg(t('cond.marketFaction', { name: fac?.displayName ?? facM[1] }));
  }
  const comM = body.match(PLAYER_COMMISSION_RE) ?? body.match(COMMISSION_ID_RE);
  if (comM) {
    const fac = appData.getFactionById(comM[1]);
    return applyNeg(t('cond.playerCommission', { name: fac?.displayName ?? comM[1] }));
  }
  const comNeM = body.match(PLAYER_COMMISSION_NE_RE);
  if (comNeM) {
    const fac = appData.getFactionById(comNeM[1]);
    return applyNeg(
      t('cond.negated', { text: t('cond.playerCommission', { name: fac?.displayName ?? comNeM[1] }) })
    );
  }
  const mktM = body.match(MARKET_RE);
  if (mktM) {
    const planet = appData
      .sortdPlanet()
      .find((p) => !p.isSubStation && p.market && p.market.id === mktM[1]);
    return applyNeg(t('cond.market', { name: planet?.name ?? mktM[1] }));
  }
  const perM = body.match(PERSON_RE);
  if (perM) {
    const person = appData.getPersonById(perM[1]);
    const name = person
      ? `${person.firstName} ${person.lastName}`.trim() || perM[1]
      : perM[1];
    return applyNeg(t('cond.person', { name }));
  }
  if (body === 'PersonIsDefaultMarketPost') {
    return { label: t('cond.marketPost'), known: true };
  }
  if (HOSTILE_RE.test(body)) {
    return applyNeg(t('cond.hostile'), false);
  }
  if (body === '$encounteredAlready') {
    return neg
      ? { label: t('cond.encountered'), known: false }
      : { label: t('cond.negated', { text: t('cond.encountered') }), known: false };
  }
  const repGteM = body.match(REP_GTE_FACTION_RE);
  if (repGteM) {
    const fac = appData.getFactionById(repGteM[1]);
    return {
      label: t('cond.repGTE', { faction: fac?.displayName ?? repGteM[1], level: repGteM[2] }),
      known: false,
    };
  }
  const repLteM = body.match(REP_LTE_FACTION_RE);
  if (repLteM) {
    const fac = appData.getFactionById(repLteM[1]);
    return {
      label: t('cond.repLTE', { faction: fac?.displayName ?? repLteM[1], level: repLteM[2] }),
      known: false,
    };
  }
  const repSimple = body.match(REP_GTE_RE) ?? body.match(REP_LTE_RE);
  if (repSimple) {
    return { label: c, known: false };
  }

  // 单一 flag：查任务术语表
  const flagM = body.match(NEG_FLAG_RE);
  if (flagM) {
    const flag = '$' + flagM[2];
    const gloss = props.quest.flags[flag];
    if (gloss) {
      return applyNeg(primary(gloss));
    }
  }

  return { label: c, known: false };
}

function condChips(conditions: string[]): CondChip[] {
  const out: CondChip[] = [];
  for (const raw of conditions) {
    const chip = describeCondition(raw);
    if (chip.label) {
      out.push(chip);
    }
  }
  return out;
}
</script>

<template>
  <div class="quest-dialogue">
    <!-- 多入口选择 -->
    <div v-if="props.scene.entries.length > 1" class="dlg-entries">
      <span class="dlg-cond-label">{{ $t('quest.selectEntry') }}:</span>
      <q-chip
        v-for="(_, i) in props.scene.entries"
        :key="i"
        dense
        clickable
        :color="i === entryIndex ? 'primary' : 'grey-6'"
        :text-color="i === entryIndex ? 'white' : undefined"
        @click="selectEntry(i)"
      >
        {{ i + 1 }}. {{ entryLabel(i) }}
      </q-chip>
    </div>

    <!-- 路径导航 -->
    <div class="dlg-path">
      <template v-for="(entry, i) in path" :key="i">
        <q-chip
          v-if="entry.chosenLabel"
          dense
          size="sm"
          clickable
          color="primary"
          text-color="white"
          @click="goBack(i)"
        >
          {{ primary(entry.chosenLabel) }}
        </q-chip>
        <q-chip v-else dense size="sm" clickable outline @click="goBack(i)">
          {{ i === 0 ? $t('quest.reset') : '…' }}
        </q-chip>
      </template>
      <q-space />
      <q-btn
        v-if="path.length > 0"
        dense
        flat
        no-caps
        icon="restart_alt"
        :label="$t('quest.reset')"
        @click="reset"
      />
    </div>

    <template v-if="step === undefined">
      <div class="dlg-dead-end">{{ $t('quest.deadEnd') }}</div>
    </template>

    <template v-else>
      <!-- 场景触发条件（入口处显示） -->
      <div
        v-if="atEntry && (step.entryConditions?.length ?? 0) > 0"
        class="dlg-entry-conds"
      >
        <span class="dlg-cond-label">{{ $t('quest.entryConditions') }}:</span>
        <q-chip
          v-for="(chip, ci) in condChips(step.entryConditions ?? [])"
          :key="ci"
          dense
          size="sm"
          :color="chip.known ? 'accent' : 'grey-6'"
          text-color="white"
        >
          {{ chip.label }}
        </q-chip>
      </div>

      <!-- 说话人 -->
      <div class="dlg-speaker">
        <q-avatar size="24px" class="bg-primary text-white">{{
          speakerName.charAt(0)
        }}</q-avatar>
        <span>{{ speakerName }}</span>
      </div>

      <!-- 文本块 -->
      <div v-for="(block, bi) in step.texts" :key="bi" class="dlg-text-block">
        <div v-if="block.conditions.length > 0" class="dlg-conditions">
          <span class="dlg-cond-label">{{ $t('quest.conditions') }}:</span>
          <q-chip
            v-for="(chip, ci) in condChips(block.conditions)"
            :key="ci"
            dense
            size="sm"
            :color="chip.known ? 'accent' : 'grey-6'"
            text-color="white"
          >
            {{ chip.label }}
          </q-chip>
        </div>
        <div class="dlg-text" :class="{ 'dlg-text-small': block.small }">
          <template v-for="(seg, si) in splitVars(primary(block))" :key="si">
            <span v-if="seg.kind === 'var'" class="dlg-var" :title="$t('quest.varHint', { name: seg.value })">{{
              seg.value
            }}</span>
            <template v-else>{{ seg.value }}</template>
          </template>
        </div>
        <div class="dlg-text-en" v-if="block.en !== block.zh">
          <template v-for="(seg, si) in splitVars(secondary(block))" :key="'e' + si">
            <span v-if="seg.kind === 'var'" class="dlg-var dlg-var-en" :title="$t('quest.varHint', { name: seg.value })">{{
              seg.value
            }}</span>
            <template v-else>{{ seg.value }}</template>
          </template>
        </div>
        <div v-if="block.effects.length > 0" class="dlg-effects">
          <span class="dlg-cond-label">{{ $t('quest.effects') }}:</span>
          <q-chip v-for="(e, ei) in block.effects" :key="ei" dense size="sm" outline>
            {{ e }}
          </q-chip>
        </div>
      </div>

      <!-- 玩家选项 -->
      <div v-if="step.options.length > 0" class="dlg-options">
        <div class="dlg-options-label">{{ $t('quest.speaker') }}: {{ $t('nav.persons') }} ▾</div>
        <q-btn
          v-for="(opt, oi) in step.options"
          :key="opt.id + oi"
          class="dlg-option"
          no-caps
          align="left"
          :disable="!opt.target"
          @click="chooseOption(opt)"
        >
          <div class="dlg-option-content">
            <div class="dlg-option-text">
              {{ primary(opt) }}
              <span v-if="opt.num" class="dlg-option-num">{{ opt.num }}</span>
            </div>
            <div v-if="opt.en !== opt.zh" class="dlg-option-en">{{ secondary(opt) }}</div>
            <div v-if="opt.conditions.length > 0" class="dlg-conditions">
              <q-chip
                v-for="(chip, ci) in condChips(opt.conditions)"
                :key="ci"
                dense
                size="sm"
                :color="chip.known ? 'accent' : 'grey-6'"
                text-color="white"
              >
                {{ chip.label }}
              </q-chip>
            </div>
          </div>
        </q-btn>
      </div>

      <!-- 自动继续 -->
      <div v-else-if="step.next.length > 0" class="dlg-options">
        <q-btn
          v-for="nid in step.next"
          :key="nid"
          class="dlg-option"
          no-caps
          color="primary"
          @click="continueTo(nid)"
        >
          {{ $t('quest.continue') }} →
          <span class="dlg-option-next-id">{{ nid.slice(2) }}</span>
        </q-btn>
      </div>

      <!-- 结束标记 -->
      <div v-else class="dlg-dead-end">
        <template v-if="step.end">{{ $t('quest.end') }}</template>
        <template v-else-if="step.menuReturn">{{ $t('quest.menuReturn') }}</template>
        <template v-else>{{ $t('quest.deadEnd') }}</template>
      </div>

      <!-- 阶段提示 -->
      <div v-if="step.stageHints.length > 0" class="dlg-stage-hints">
        <q-chip
          v-for="h in step.stageHints"
          :key="h"
          dense
          size="sm"
          color="secondary"
          text-color="white"
        >
          {{ $t('quest.stageHint', { stage: h }) }}
        </q-chip>
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
.quest-dialogue {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dlg-path {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.dlg-entries {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.dlg-entry-conds {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  padding: 6px 10px;
  border: 1px dashed rgba(128, 128, 128, 0.35);
  border-radius: 6px;
}

.dlg-speaker {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  opacity: 0.9;
}

.dlg-text-block {
  border-left: 3px solid rgba(128, 128, 128, 0.4);
  padding: 4px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dlg-text {
  white-space: pre-wrap;
  line-height: 1.6;
}

.dlg-text-small {
  opacity: 0.75;
  font-size: 0.92em;
}

.dlg-text-en {
  white-space: pre-wrap;
  line-height: 1.5;
  opacity: 0.5;
  font-size: 0.92em;
  font-style: italic;
}

.dlg-var {
  font-family: monospace;
  background: rgba(255, 152, 0, 0.18);
  border-radius: 3px;
  padding: 0 3px;
  color: #ffb74d;
}

.dlg-var-en {
  color: #ffb74d;
}

.dlg-conditions,
.dlg-effects {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 2px;
}

.dlg-cond-label {
  font-size: 0.8em;
  opacity: 0.6;
}

.dlg-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
}

.dlg-options-label {
  font-size: 0.85em;
  opacity: 0.6;
}

.dlg-option {
  text-align: left;
}

.dlg-option-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  align-items: flex-start;
  width: 100%;
}

.dlg-option-text {
  font-weight: 500;
}

.dlg-option-num {
  opacity: 0.5;
  margin-left: 6px;
  font-size: 0.8em;
}

.dlg-option-en {
  opacity: 0.5;
  font-size: 0.88em;
  font-style: italic;
}

.dlg-option-next-id {
  opacity: 0.6;
  font-family: monospace;
  font-size: 0.8em;
  margin-left: 8px;
}

.dlg-dead-end {
  opacity: 0.7;
  padding: 8px;
  font-style: italic;
}

.dlg-stage-hints {
  margin-top: 4px;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
</style>
