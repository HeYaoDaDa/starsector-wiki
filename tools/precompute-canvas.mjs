/**
 * tools/precompute-canvas.mjs
 * 构建时预计算所有武器和舰船的 CanvasResult
 * 消除运行时图片加载 + 数学计算的开销
 *
 * 自动读取 manifest.json，为所有版本和 locale 生成 canvas-cache.json
 * 用法: node tools/precompute-canvas.mjs
 */
import { readFileSync, writeFileSync, readdirSync, existsSync, statSync, copyFileSync, mkdirSync } from 'fs';
import { imageSize } from 'image-size';
import path from 'path';
import { fileURLToPath } from 'url';

// 预加载所有图片尺寸到内存 Map，避免反复 readFileSync
const _dimCache = new Map();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const PUBLIC_DATA = path.join(ROOT, 'public', 'data');
const GRAPHICS_DIR = path.join(ROOT, 'public');

// ── 读取 PNG 尺寸 ──
function dim(spritePath) {
  if (!spritePath) return { w: 0, h: 0 };
  if (_dimCache.has(spritePath)) return _dimCache.get(spritePath);
  const p = path.join(GRAPHICS_DIR, spritePath);
  if (!existsSync(p)) { _dimCache.set(spritePath, { w: 0, h: 0 }); return { w: 0, h: 0 }; }
  try {
    const buf = readFileSync(p);
    const d = imageSize(buf);
    const r = { w: d.width, h: d.height };
    _dimCache.set(spritePath, r);
    return r;
  } catch {
    _dimCache.set(spritePath, { w: 0, h: 0 });
    return { w: 0, h: 0 };
  }
}

// ── computeCanvasSprites（纯数学，移植自 CanvasSprite.ts）──
function computeCanvasSprites(...sprites) {
  let r = { left: 0, right: 0, top: 0, bottom: 0 };
  for (const s of sprites) r = addSprite(r, s);
  return r;
}
function addSprite(r, s) {
  let top = s.h / 2, bot = s.h / 2, left = s.w / 2, right = s.w / 2;
  top -= s.cy; bot += s.cy; left += s.cx; right -= s.cx;
  if (s.deg % 360 !== 0) {
    const d = Math.max(
      Math.sqrt(top ** 2 + right ** 2),
      Math.sqrt(right ** 2 + bot ** 2),
      Math.sqrt(bot ** 2 + left ** 2),
      Math.sqrt(left ** 2 + top ** 2),
    );
    top = bot = left = right = d;
  }
  top += s.ty; bot -= s.ty; left -= s.tx; right += s.tx;
  return {
    left:   Math.max(r.left,   left),
    right:  Math.max(r.right,  right),
    top:    Math.max(r.top,    top),
    bottom: Math.max(r.bottom, bot),
  };
}

// ── 预计算武器 CanvasResult ──
function computeWeaponCanvas(wpn, hard) {
  const key  = hard ? 'hardPoint' : 'turret';
  const spr  = wpn[key + 'Sprite'];
  if (!spr) return null;

  const under = wpn[key + 'UnderSprite'];
  const gun   = wpn[key + 'GunSprite'];
  const offsets = hard ? (wpn.hardPointOffsets || []) : (wpn.turretOffsets || []);
  const showMissile = (wpn.renderHints || []).includes('RENDER_LOADED_MISSILES')
    || (wpn.renderHints || []).includes('RENDER_LOADED_MISSILES_UNLESS_HIDDEN');

  const parts = [];

  if (under) { const d = dim(under); parts.push({ w: d.w, h: d.h, cx: 0, cy: 0, tx: 0, ty: 0, deg: 0 }); }
  if (gun)   { const d = dim(gun);   parts.push({ w: d.w, h: d.h, cx: 0, cy: 0, tx: 0, ty: 0, deg: 0 }); }

  const sd = dim(spr);
  parts.push({ w: sd.w, h: sd.h, cx: 0, cy: 0, tx: 0, ty: 0, deg: 0 });

  if (showMissile && offsets.length > 0 && wpn.projSpriteName) {
    const pd = dim(wpn.projSpriteName);
    for (let i = 0; i < offsets.length; i += 2) {
      const top = hard
        ? offsets[i] - sd.h / 4
        : offsets[i];
      parts.push({ w: pd.w, h: pd.h, cx: 0, cy: 0, tx: offsets[i + 1], ty: top, deg: 0 });
    }
  }

  const r = computeCanvasSprites(...parts);
  if (hard) { r.top += sd.h / 4; r.bottom -= sd.h / 4; }
  return r;
}

// ── 对一个版本进行预计算（locale 无关，结果可复用）──
function precomputeVersion(version) {
  console.log(`\n=== Precomputing: ${version} ===`);

  const verDir = path.join(PUBLIC_DATA, version);
  if (!existsSync(verDir)) { console.log(`  Version dir not found: ${verDir}`); return; }

  // 扫描 locale 目录
  const availableLocales = [];
  for (const name of readdirSync(verDir)) {
    const lp = path.join(verDir, name);
    if (existsSync(lp) && statSync(lp).isDirectory() && existsSync(path.join(lp, 'data.json'))) {
      availableLocales.push(name);
    }
  }
  if (availableLocales.length === 0) {
    console.log(`  No data.json found for ${version}, skipping.`);
    return;
  }

  const firstLocale = availableLocales[0];
  const dataPath = path.join(verDir, firstLocale, 'data.json');
  console.log(`  Reading: ${dataPath}`);

  const all = JSON.parse(readFileSync(dataPath, 'utf8'));

  // 按类型分类
  const weapons = [];
  const ships   = [];
  for (let i = 0; i < all.length; i++) {
    const x = all[i];
    if (!x || !x.jsonType) continue;
    if (x.jsonType === 'WEAPON') weapons.push(x);
    else if (x.jsonType === 'SHIP') ships.push(x);
  }
  console.log(`  Weapons: ${weapons.length}, Ships: ${ships.length}`);

  // ── 预计算武器 ──
  const wCache = {};
  for (const w of weapons) {
    const t = computeWeaponCanvas(w, false);
    if (t) wCache[w.id] = t;
    const h = computeWeaponCanvas(w, true);
    if (h) wCache[w.id + '_hard'] = h;
  }
  console.log(`  Weapon cache: ${Object.keys(wCache).length} entries`);

  // ── 预计算舰船（递归）──
  const sCache = {};
  const shipById = {};
  for (const s of ships) shipById[s.id] = s;

  function shipCanvas(shipId) {
    if (sCache[shipId]) return sCache[shipId];
    const ship = shipById[shipId];
    if (!ship) return null;

    const sd = dim(ship.sprite);
    if (!sd.w && !sd.h) {
      // 没有 sprite 的船（如某些模块/装饰），返回零尺寸
      sCache[shipId] = { left: 0, right: 0, top: 0, bottom: 0 };
      return sCache[shipId];
    }

    const parts = [{
      w: sd.w, h: sd.h,
      cx: ship.center.left - sd.w / 2 + (ship.moduleAnchor?.x ?? 0),
      cy: ship.center.bottom - sd.h / 2 + (ship.moduleAnchor?.y ?? 0),
      tx: 0, ty: 0, deg: 0,
    }];

    // 武器槽位
    const weaponIdMap = ship.weaponIdMap || {};
    const allSlots = ship.allWeaponSlots || [];
    const slotMap = {};
    for (const slot of allSlots) slotMap[slot.id] = slot;

    for (const [slotId, weaponId] of Object.entries(weaponIdMap)) {
      if (!weaponId) continue;
      const wcrKey = slotMap[slotId]?.hardPoint ? weaponId + '_hard' : weaponId;
      const cr = wCache[wcrKey];
      if (!cr) continue;
      const slot = slotMap[slotId];
      if (!slot) continue;
      const h = cr.top + cr.bottom;
      const w = cr.left + cr.right;
      parts.push({
        w, h,
        cx: cr.left - w / 2,
        cy: -(cr.top - h / 2),
        tx: slot.location.x,
        ty: slot.location.y,
        deg: slot.angle,
      });
    }

    // 模块（递归）
    const moduleIdMap = ship.moduleIdMap || {};
    for (const [slotId, variantId] of Object.entries(moduleIdMap)) {
      if (!variantId) continue;
      const mc = shipCanvas(variantId);
      if (!mc) continue;
      const slot = slotMap[slotId];
      if (!slot) continue;
      const h = mc.top + mc.bottom;
      const w = mc.left + mc.right;
      parts.push({
        w, h,
        cx: mc.left - w / 2,
        cy: -(mc.top - h / 2),
        tx: slot.location.x,
        ty: slot.location.y,
        deg: slot.angle,
      });
    }

    const result = computeCanvasSprites(...parts);
    sCache[shipId] = result;
    return result;
  }

  for (const s of ships) {
    if (s.emptyHullVariant) {
      shipCanvas(s.id);
    }
  }
  // 也计算 variants（它们可能被武器引用）
  for (const s of ships) {
    if (!s.emptyHullVariant) {
      shipCanvas(s.id);
    }
  }

  console.log(`  Ship cache: ${Object.keys(sCache).length} entries`);

  // ── 写入所有 locale ──
  const output = {
    version,
    ships: sCache,
    weapons: wCache,
  };
  const json = JSON.stringify(output);

  for (const loc of availableLocales) {
    const outDir = path.join(verDir, loc);
    const outPath = path.join(outDir, 'canvas-cache.json');
    writeFileSync(outPath, json);
    const kb = (statSync(outPath).size / 1024).toFixed(1);
    console.log(`  Written: ${loc}/canvas-cache.json (${kb} KB)`);
  }
}

// ── 主流程：遍历所有版本 ──
function main() {
  const manifestPath = path.join(PUBLIC_DATA, 'manifest.json');
  if (!existsSync(manifestPath)) {
    console.error('manifest.json not found');
    process.exit(1);
  }
  const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
  const versions = manifest.versions || [];
  if (versions.length === 0) {
    console.error('No versions in manifest');
    process.exit(1);
  }

  for (const v of versions) {
    precomputeVersion(v.version);
  }
  console.log('\nAll done.');
}

main();
