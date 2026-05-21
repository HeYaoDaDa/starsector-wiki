export const enum ShieldType {
  NONE = 'NONE',
  FRONT = 'FRONT',
  OMNI = 'OMNI',
  PHASE = 'PHASE',
}

export const enum HullSize {
  FIGHTER = 'FIGHTER',
  FRIGATE = 'FRIGATE',
  DESTROYER = 'DESTROYER',
  CRUISER = 'CRUISER',
  CAPITAL_SHIP = 'CAPITAL_SHIP',
}

export const enum WeaponType {
  BALLISTIC = 'BALLISTIC',
  ENERGY = 'ENERGY',
  MISSILE = 'MISSILE',
  LAUNCH_BAY = 'LAUNCH_BAY',
  UNIVERSAL = 'UNIVERSAL',
  HYBRID = 'HYBRID',
  SYNERGY = 'SYNERGY',
  COMPOSITE = 'COMPOSITE',
  BUILT_IN = 'BUILT_IN',
  DECORATIVE = 'DECORATIVE',
  SYSTEM = 'SYSTEM',
  STATION_MODULE = 'STATION_MODULE',
}

export const enum WeaponSize {
  SMALL = 'SMALL',
  MEDIUM = 'MEDIUM',
  LARGE = 'LARGE',
}

export function compareWeaponSize(a: WeaponSize, b: WeaponSize) {
  return (WeaponSizeValueMap.get(a) ?? 'a').localeCompare(
    WeaponSizeValueMap.get(b) ?? 'a'
  );
}

const WeaponSizeValueMap = new Map([
  [WeaponSize.SMALL, 'a'],
  [WeaponSize.MEDIUM, 'b'],
  [WeaponSize.LARGE, 'c'],
]);
