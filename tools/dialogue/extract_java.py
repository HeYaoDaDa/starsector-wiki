#!/usr/bin/env python3
"""Extract quest stage data from mission classes in starfarer.api.jar.

Reads the class constant pool (no decompilation needed) to pull:
- Stage enum names (TheUsurpers$Stage etc.)
- Stage briefing / next-step strings
- Global flags referenced by the mission

With --cn, the same class is read from the CN build's jar and the
Chinese strings are reported alongside (the official CN localization
translates newer mission classes in-place).

Usage:
    python3 extract_java.py <en_game_root> [<cn_game_root>] <mission_class>...
    python3 extract_java.py ~/Games/starsector-0985a-en ~/Games/starsector-0985a-cn askonia.TheUsurpers askonia.SDSevenSons
"""

from __future__ import annotations

import json
import re
import struct
import sys
import zipfile


def read_utf8_constants(class_bytes: bytes) -> list[str]:
    """Read CONSTANT_Utf8 entries from a .class file, in pool order."""
    if class_bytes[:4] != b'\xca\xfe\xba\xbe':
        raise ValueError('not a class file')
    pos = 8
    count = struct.unpack_from('>H', class_bytes, pos)[0]
    pos += 2
    out: list[str] = []
    i = 1
    while i < count:
        tag = class_bytes[pos]
        pos += 1
        if tag == 1:  # Utf8
            length = struct.unpack_from('>H', class_bytes, pos)[0]
            pos += 2
            raw = class_bytes[pos:pos + length]
            pos += length
            # java "modified utf-8": handle the common cases
            text = raw.decode('utf-8', errors='replace')
            out.append(text)
        elif tag in (7, 8, 16, 19, 20):  # single-u2 refs
            pos += 2
        elif tag == 15:  # MethodHandle
            pos += 3
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):  # u4 / two-u2
            pos += 4
        elif tag in (5, 6):  # long/double take two slots
            pos += 8
            i += 1
        else:
            raise ValueError(f'unknown constant tag {tag} at {pos}')
        i += 1
    return out


def class_path(mission: str) -> str:
    return f'com/fs/starfarer/api/impl/campaign/missions/{mission.replace(".", "/")}.class'


def extract_mission(jar_path: str, mission: str) -> dict:
    z = zipfile.ZipFile(jar_path)
    base = mission.split('.')[-1]
    pkg = mission.rsplit('.', 1)[0].replace('.', '/')

    result: dict = {'mission': mission, 'stages': [], 'flags': [], 'texts': []}

    # stage enum values
    enum_name = f'com/fs/starfarer/api/impl/campaign/missions/{pkg}/{base}$Stage.class'
    try:
        strings = read_utf8_constants(z.read(enum_name))
        stages = []
        for s in strings:
            if re.fullmatch(r'[A-Z][A-Z0-9_]*', s) and s not in ('Stage',):
                stages.append(s)
        # dedupe preserving order
        seen = set()
        result['stages'] = [s for s in stages if not (s in seen or seen.add(s))]
    except KeyError:
        pass

    strings = read_utf8_constants(z.read(class_path(mission)))

    # memory flags like $sdtu_meetHyder
    flags = []
    for s in strings:
        for m in re.finditer(r'\$[A-Za-z_][A-Za-z0-9_.]*', s):
            f = m.group(0)
            if f not in flags:
                flags.append(f)
    result['flags'] = flags

    # prose-ish strings: briefing/next-step texts (contain a space + period)
    texts = []
    for s in strings:
        if ' ' not in s or len(s) < 20:
            continue
        if s.startswith(('$', 'com/', 'java/', 'L', '(')) or '/' in s:
            continue
        if re.match(r'^[A-Za-z]:', s):  # length-prefix artifact, strip it
            s = s[1:]
        if re.search(r'[a-z]{3} [a-z]+', s) and s.rstrip().endswith('.'):
            texts.append(s)
    result['texts'] = texts
    return result


def extract_mission_cn(jar_path: str, mission: str) -> dict:
    """Chinese strings from the CN build's class (same class name in api jar)."""
    z = zipfile.ZipFile(jar_path)
    result: dict = {'mission': mission, 'stages': [], 'flags': [], 'texts': []}
    try:
        strings = read_utf8_constants(z.read(class_path(mission)))
    except KeyError:
        return result
    result['texts'] = [
        s for s in strings
        if re.search(r'[\u4e00-\u9fff]', s) and len(s) > 6
    ]
    return result


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    args = [a.rstrip('/') for a in sys.argv[1:]]
    cn_root = None
    if args[0].endswith('-cn'):
        cn_root = args.pop(0)
    en_root = args.pop(0)
    jar = f'{en_root}/starfarer.api.jar'
    out = {}
    for mission in args:
        m = extract_mission(jar, mission)
        if cn_root:
            m['cn'] = extract_mission_cn(f'{cn_root}/starfarer.api.jar', mission)
        out[mission] = m
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
