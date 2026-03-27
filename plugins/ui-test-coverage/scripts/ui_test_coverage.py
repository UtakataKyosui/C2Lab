#!/usr/bin/env python3
"""
UI Test Coverage Analyzer

UIコンポーネントを静的解析し、最低限必要なテスト数を計算する。

計算式:
  正常系テスト数 = Π(正常系バリアント因子の値数)
  異常系パターン数 = Π(異常系因子の値数)
  合計最低テスト数 = 正常系テスト数 × 異常系パターン数

正常系バリアント: 必須 enum/union props（variant, size, type など）
異常系因子: boolean props, optional props, states, event handlers

使用方法:
  python ui_test_coverage.py [project_dir] [--output report.json] [--component <pattern>]
"""

import os
import re
import json
import sys
import argparse
import math
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────
# 拡張子の定義
# ─────────────────────────────────────────────
COMPONENT_EXTENSIONS = {".tsx", ".jsx", ".vue", ".svelte"}
TEST_EXTENSIONS = {".test.tsx", ".test.ts", ".test.jsx", ".test.js",
                   ".spec.tsx", ".spec.ts", ".spec.jsx", ".spec.js"}
E2E_DIR_PATTERNS = {"e2e", "cypress", "playwright"}

# ─────────────────────────────────────────────
# TypeScript型から値の数を推定
# ─────────────────────────────────────────────

def count_type_values(type_str: str) -> int:
    """TypeScript型定義から取りうる値の数を推定する。"""
    t = type_str.strip().rstrip(";").strip()

    # オプショナル型 (T | undefined, T | null, T?)
    if re.search(r'\|\s*(?:undefined|null)\b', t):
        # ベース型の値数 + 未指定の 1 ケース
        base = re.sub(r'\|\s*(?:undefined|null)\b', '', t).strip().strip('|').strip()
        return count_type_values(base) + 1

    # Union 型 ('a' | 'b' | 'c')
    if '|' in t:
        members = [m.strip() for m in t.split('|') if m.strip()]
        # リテラル型の場合はそのまま数える
        if all(re.match(r"^['\"].*['\"]$|^\d+$|^true$|^false$", m) for m in members):
            return len(members)
        # 型名の Union は各 2 として推定
        return sum(count_type_values(m) for m in members)

    # プリミティブ・一般型
    if t in ("boolean",):
        return 2
    if t in ("string", "number", "bigint"):
        return 2  # 正常値 / 異常値（空・境界値）
    if t in ("void", "never", "null", "undefined"):
        return 1
    if re.match(r"^['\"].*['\"]$", t):  # 文字列リテラル
        return 1
    if re.match(r"^\d+$", t):  # 数値リテラル
        return 1
    if t in ("true", "false"):
        return 1

    # 配列型 (T[])
    if t.endswith("[]") or t.startswith("Array<"):
        return 2  # 空配列 / 非空配列

    # React.ReactNode, ReactElement など描画可能型
    if re.match(r"^React\.", t) or t in ("ReactNode", "ReactElement", "JSX.Element"):
        return 2

    # フォールバック: 2 (正常 / 異常)
    return 2


# ─────────────────────────────────────────────
# 正常系 / 異常系 分類
# ─────────────────────────────────────────────

def classify_feature(type_str: str, optional: bool, is_state: bool = False) -> str:
    """
    prop/state を 'normal'（正常系バリアント）か 'error'（異常系・エッジケース）に分類する。

    正常系バリアント: required な enum/union props（variant, size, type など）
      → コンポーネントの「設定の組み合わせ」を表す。全値が等しく有効。

    異常系・エッジケース:
      - boolean 型（true = 無効・ロード・エラー状態）
      - optional props（省略ケース自体がエッジケース）
      - States（React useState 等のランタイム状態）
      - event handlers（型に => を含む）
      - Union に 'error'/'loading'/'disabled' 等のリテラルを含む型
    """
    t = type_str.strip().rstrip(";").strip()

    # React state → 常に異常系（ランタイム状態はエッジケース）
    if is_state:
        return "error"

    # boolean → 異常系
    if t == "boolean":
        return "error"

    # optional → 異常系（省略ケース = エッジケース）
    if optional:
        return "error"

    # Function type (event handler) → 異常系
    if "=>" in t:
        return "error"

    # Union に error/loading/disabled 系のリテラルを含む → 異常系
    error_literals = {
        "'error'", '"error"', "'loading'", '"loading"',
        "'disabled'", '"disabled"', "'failed'", '"failed"',
        "'warning'", '"warning"', "'pending'", '"pending"',
        "'inactive'", '"inactive"',
    }
    t_lower = t.lower()
    for ev in error_literals:
        if ev in t_lower:
            return "error"

    # デフォルト: 正常系バリアント（required な enum/union）
    return "normal"


# ─────────────────────────────────────────────
# Props 解析
# ─────────────────────────────────────────────

def extract_props_from_tsx(source: str) -> list[dict]:
    """TSX/JSX から Props インターフェース/type を解析して props リストを返す。"""
    props: list[dict] = []

    # interface XxxProps { ... } / type XxxProps = { ... }
    block_patterns = [
        r'(?:interface|type)\s+\w*[Pp]rops\s*(?:=\s*)?\{([^{}]+)\}',
        # FC<{ ... }> / memo<{ ... }> のインライン型
        r'(?:FC|FunctionComponent|memo)\s*<\s*\{([^{}]+)\}',
    ]
    # function Component({ ... }: { ... }) のデストラクチャ型
    block_patterns.append(r'function\s+\w+\s*\([^)]*\)\s*:\s*\{([^{}]+)\}')

    prop_re = re.compile(r'(\w+)\??\s*:\s*([^;,\n]+)')

    for pattern in block_patterns:
        for m in re.finditer(pattern, source, re.DOTALL):
            block = m.group(1)
            for pm in prop_re.finditer(block):
                name = pm.group(1).strip()
                type_str = pm.group(2).strip()
                # children, className, style など汎用 prop は除外
                if name in ("children", "className", "style", "id", "key", "ref"):
                    continue
                optional = "?" in pm.group(0).split(":")[0] or "undefined" in type_str
                values = count_type_values(type_str)
                props.append({
                    "name": name,
                    "type": type_str,
                    "optional": optional,
                    "values": values,
                    "category": classify_feature(type_str, optional),
                })

    # 重複除去（name で）
    seen: set[str] = set()
    unique: list[dict] = []
    for p in props:
        if p["name"] not in seen:
            seen.add(p["name"])
            unique.append(p)
    return unique


def extract_props_from_vue(source: str) -> list[dict]:
    """Vue SFC の defineProps / props: オプションを解析する。"""
    props: list[dict] = []

    # defineProps<{ ... }>() の型引数
    m = re.search(r'defineProps\s*<\s*\{([^{}]+)\}', source, re.DOTALL)
    if m:
        prop_re = re.compile(r'(\w+)\??\s*:\s*([^;,\n]+)')
        for pm in prop_re.finditer(m.group(1)):
            name = pm.group(1).strip()
            type_str = pm.group(2).strip()
            optional = "?" in pm.group(0).split(":")[0] or "undefined" in type_str
            props.append({
                "name": name,
                "type": type_str,
                "optional": optional,
                "values": count_type_values(type_str),
                "category": classify_feature(type_str, optional),
            })

    # defineProps({ name: { type: Boolean, ... } })
    if not props:
        runtime_m = re.search(r'defineProps\s*\(\s*(\{.+?\})\s*\)', source, re.DOTALL)
        if runtime_m:
            for pm in re.finditer(r"(\w+)\s*:\s*\{[^}]*type\s*:\s*(\w+)", runtime_m.group(1)):
                name = pm.group(1)
                ts_type = {"Boolean": "boolean", "String": "string",
                           "Number": "number", "Array": "T[]"}.get(pm.group(2), pm.group(2).lower())
                props.append({
                    "name": name,
                    "type": ts_type,
                    "optional": True,
                    "values": count_type_values(ts_type),
                    "category": classify_feature(ts_type, optional=True),
                })

    return props


def extract_props_from_svelte(source: str) -> list[dict]:
    """Svelte コンポーネントの export let を解析する。"""
    props: list[dict] = []
    # export let name: Type = default;
    for m in re.finditer(r'export\s+let\s+(\w+)\s*(?::\s*([^=;]+))?', source):
        name = m.group(1)
        type_str = (m.group(2) or "string").strip()
        props.append({
            "name": name,
            "type": type_str,
            "optional": True,
            "values": count_type_values(type_str),
            "category": classify_feature(type_str, optional=True),
        })
    return props


# ─────────────────────────────────────────────
# State 解析
# ─────────────────────────────────────────────

def extract_states_from_tsx(source: str) -> list[dict]:
    """useState / useReducer / Zustand store などから state 変数を抽出する。"""
    states: list[dict] = []

    # const [name, setXxx] = useState<Type>(...)
    for m in re.finditer(
        r'const\s+\[(\w+),\s*\w+\]\s*=\s*use(?:State|Reducer)\s*[<(]([^)>]*)[)>]',
        source
    ):
        name = m.group(1)
        type_str = m.group(2).strip() or "any"
        states.append({
            "name": name,
            "type": type_str,
            "values": count_type_values(type_str),
            "category": "error",  # states は常に異常系（ランタイム状態）
        })

    return states


def extract_states_from_vue(source: str) -> list[dict]:
    """ref() / reactive() から state を抽出する。"""
    states: list[dict] = []

    # const name = ref<Type>(...)
    for m in re.finditer(r'const\s+(\w+)\s*=\s*ref\s*[<(]([^)>]*)[)>]', source):
        name = m.group(1)
        type_str = m.group(2).strip() or "any"
        states.append({
            "name": name,
            "type": type_str,
            "values": count_type_values(type_str),
            "category": "error",
        })

    return states


def extract_states_from_svelte(source: str) -> list[dict]:
    """let 宣言（非 export）を state として扱う。"""
    states: list[dict] = []

    script_m = re.search(r'<script[^>]*>(.*?)</script>', source, re.DOTALL)
    if script_m:
        for m in re.finditer(r'(?<!export\s)let\s+(\w+)\s*(?::\s*([^=;]+))?', script_m.group(1)):
            name = m.group(1)
            type_str = (m.group(2) or "any").strip()
            states.append({
                "name": name,
                "type": type_str,
                "values": count_type_values(type_str),
                "category": "error",
            })
    return states


# ─────────────────────────────────────────────
# イベントハンドラ解析
# ─────────────────────────────────────────────

def extract_events_from_tsx(source: str) -> list[str]:
    """JSX から on[A-Z]xxx 形式のイベントハンドラ名を抽出する。"""
    return list(set(re.findall(r'\b(on[A-Z][a-zA-Z]+)\b', source)))


def extract_events_from_vue(source: str) -> list[str]:
    """Vue テンプレートから @event / v-on:event を抽出する。"""
    return list(set(re.findall(r'(?:@|v-on:)(\w+)', source)))


def extract_events_from_svelte(source: str) -> list[str]:
    """Svelte テンプレートから on:event を抽出する。"""
    return list(set(re.findall(r'on:(\w+)', source)))


# ─────────────────────────────────────────────
# 条件分岐レンダリング解析
# ─────────────────────────────────────────────

def count_conditional_branches(source: str, ext: str) -> int:
    """JSX/テンプレート内の条件分岐（ternary / && / v-if など）の数を数える。"""
    count = 0

    if ext in (".tsx", ".jsx"):
        # ternary: xxx ? <Comp> / xxx ? (
        count += len(re.findall(r'\?\s*(?:<[A-Z]|\()', source))
        # && rendering: {condition && <Comp>}
        count += len(re.findall(r'&&\s*<[A-Z]', source))

    elif ext == ".vue":
        count += len(re.findall(r'\bv-if\b|\bv-else-if\b|\bv-show\b', source))

    elif ext == ".svelte":
        count += len(re.findall(r'\{#if\b|\{:else\b', source))

    return count


# ─────────────────────────────────────────────
# コンポーネント名抽出
# ─────────────────────────────────────────────

def extract_component_name(source: str, file_path: Path) -> str:
    """ソースからコンポーネント名を抽出する。"""
    # export default function/class Name
    m = re.search(r'export\s+default\s+(?:function|class)\s+(\w+)', source)
    if m:
        return m.group(1)
    # const Name: FC = ...
    m = re.search(r'(?:export\s+)?const\s+(\w+)\s*(?::\s*(?:FC|React\.FC|FunctionComponent))?'
                  r'\s*(?:<[^>]+>)?\s*=\s*(?:\([^)]*\)|[^=])\s*=>', source)
    if m:
        return m.group(1)
    # ファイル名から
    return file_path.stem.replace("-", "").replace("_", "")


# ─────────────────────────────────────────────
# コンポーネント解析エントリポイント
# ─────────────────────────────────────────────

def analyze_component(file_path: Path) -> dict[str, Any]:
    """コンポーネントファイルを解析して特徴量を返す。"""
    ext = file_path.suffix

    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        return {"error": str(e)}

    name = extract_component_name(source, file_path)

    if ext in (".tsx", ".jsx"):
        props = extract_props_from_tsx(source)
        states = extract_states_from_tsx(source)
        events = extract_events_from_tsx(source)
    elif ext == ".vue":
        props = extract_props_from_vue(source)
        states = extract_states_from_vue(source)
        events = extract_events_from_vue(source)
    elif ext == ".svelte":
        props = extract_props_from_svelte(source)
        states = extract_states_from_svelte(source)
        events = extract_events_from_svelte(source)
    else:
        props, states, events = [], [], []

    conditional_branches = count_conditional_branches(source, ext)

    # 全因子リスト（props + states）を正常系 / 異常系に分類
    all_factors = [
        *[{**p, "source": "prop"} for p in props if p["values"] > 1],
        *[{**s, "source": "state"} for s in states if s["values"] > 1],
    ]

    normal_factors = [f for f in all_factors if f["category"] == "normal"]
    error_factors  = [f for f in all_factors if f["category"] == "error"]

    # 正常系バリアント数: 各正常系因子の値数の直積
    normal_combinations = math.prod(f["values"] for f in normal_factors) if normal_factors else 1
    # 異常系パターン数: 各異常系因子の値数の直積（「全て正常値」パターンを含む）
    error_combinations  = math.prod(f["values"] for f in error_factors)  if error_factors  else 1

    # 合計最低テスト数
    min_tests = normal_combinations * error_combinations

    # 内訳: 純正常系 vs 異常系を含むテスト
    # error_combinations には「全因子が正常値」の 1 パターンが含まれるため
    pure_normal_tests = normal_combinations * 1
    error_case_tests  = min_tests - pure_normal_tests

    # 計算式文字列
    def factor_label(f: dict) -> str:
        return f"{f['name']}({f['values']})"

    normal_formula = " × ".join(factor_label(f) for f in normal_factors) or "1"
    error_formula  = " × ".join(factor_label(f) for f in error_factors)  or "1"

    if normal_factors or error_factors:
        calculation = (
            f"正常系: {normal_formula} = {normal_combinations}"
            f" | 異常系パターン: {error_formula} = {error_combinations}"
            f" | 合計: {normal_combinations} × {error_combinations} = {min_tests}"
            f" (純正常系 {pure_normal_tests} + 異常系含む {error_case_tests})"
        )
    else:
        calculation = f"1 (no variations) = {min_tests}"

    return {
        "file": str(file_path),
        "name": name,
        "analysis": {
            "props": props,
            "states": states,
            "events": events,
            "conditionalBranches": conditional_branches,
        },
        "minTests": {
            "count": min_tests,
            "normalTests": pure_normal_tests,
            "errorTests": error_case_tests,
            "normalFactors": [{"name": f["name"], "values": f["values"]} for f in normal_factors],
            "errorFactors":  [{"name": f["name"], "values": f["values"]} for f in error_factors],
            "calculation": calculation,
        },
    }


# ─────────────────────────────────────────────
# テストファイル解析
# ─────────────────────────────────────────────

def count_tests_in_file(file_path: Path) -> dict[str, int]:
    """テストファイル内の it/test/describe の数をカウントする。"""
    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {"tests": 0, "describes": 0}

    tests = len(re.findall(r'\bit\s*\(|\btest\s*\(', source))
    describes = len(re.findall(r'\bdescribe\s*\(', source))
    return {"tests": tests, "describes": describes}


def is_e2e_file(file_path: Path) -> bool:
    """E2E テストファイルかどうかを判定する。"""
    parts = set(file_path.parts)
    return bool(parts & E2E_DIR_PATTERNS)


# ─────────────────────────────────────────────
# プロジェクト全体解析
# ─────────────────────────────────────────────

SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", ".nuxt",
    "coverage", ".cache", "out", ".turbo", "vendor", "__stories__",
}

# Storybook / story ファイルはコンポーネントとして解析しない
SKIP_FILE_SUFFIXES = {".stories.tsx", ".stories.jsx", ".stories.ts", ".stories.js",
                      ".story.tsx", ".story.jsx", ".story.ts", ".story.js"}


def find_files(root: Path, extensions: set[str],
               exclude_test: bool = False) -> list[Path]:
    """再帰的にファイルを探索する。"""
    result: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # スキップディレクトリを除外
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            path = Path(dirpath) / fname
            # 複合拡張子（.test.tsx 等）チェック
            suffixes = "".join(path.suffixes)
            single_ext = path.suffix
            is_test = any(suffixes.endswith(e) for e in TEST_EXTENSIONS)
            is_story = any(suffixes.endswith(e) for e in SKIP_FILE_SUFFIXES)
            if exclude_test and (is_test or is_story):
                continue
            if single_ext in extensions or any(suffixes.endswith(e) for e in extensions):
                result.append(path)
    return result


def detect_test_frameworks(package_json: dict) -> dict[str, list[str]]:
    """package.json から使用中のテストFWを検出する。"""
    all_deps: dict[str, str] = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        all_deps.update(package_json.get(key, {}))

    unit = []
    e2e = []

    if "vitest" in all_deps:
        unit.append("vitest")
    if "jest" in all_deps or "@jest/core" in all_deps:
        unit.append("jest")
    if "@testing-library/react" in all_deps or "@testing-library/vue" in all_deps:
        unit.append("testing-library")

    if "playwright" in all_deps or "@playwright/test" in all_deps:
        e2e.append("playwright")
    if "cypress" in all_deps:
        e2e.append("cypress")

    # scripts.test / scripts.e2e からも推定
    scripts: dict[str, str] = package_json.get("scripts", {})
    for key, val in scripts.items():
        if "vitest" in val and "vitest" not in unit:
            unit.append("vitest")
        if "jest" in val and "jest" not in unit:
            unit.append("jest")
        if "playwright" in val and "playwright" not in e2e:
            e2e.append("playwright")
        if "cypress" in val and "cypress" not in e2e:
            e2e.append("cypress")

    return {"unit": unit, "e2e": e2e}


def run_analysis(project_dir: str, component_pattern: str | None = None) -> dict[str, Any]:
    """プロジェクトディレクトリを解析してレポートを生成する。"""
    root = Path(project_dir).resolve()

    # package.json 読み込み
    pkg_path = root / "package.json"
    package_json: dict = {}
    if pkg_path.exists():
        try:
            package_json = json.loads(pkg_path.read_text())
        except json.JSONDecodeError:
            pass

    frameworks = detect_test_frameworks(package_json)

    # コンポーネントファイル探索
    component_files = find_files(root, COMPONENT_EXTENSIONS, exclude_test=True)

    if component_pattern:
        import fnmatch
        component_files = [f for f in component_files
                           if fnmatch.fnmatch(str(f), component_pattern)]

    # テストファイル探索
    test_files = find_files(root, COMPONENT_EXTENSIONS | {".ts", ".js"}, exclude_test=False)
    test_files = [f for f in test_files if any("".join(f.suffixes).endswith(e) for e in TEST_EXTENSIONS)]

    unit_test_files = [f for f in test_files if not is_e2e_file(f)]
    e2e_test_files = [f for f in test_files if is_e2e_file(f)]

    # コンポーネント解析
    components_data: list[dict] = []
    for cf in sorted(component_files):
        data = analyze_component(cf)
        # ファイルパスを相対パスに変換
        try:
            data["file"] = str(cf.relative_to(root))
        except ValueError:
            pass
        components_data.append(data)

    # テストカウント
    unit_summary = {"files": 0, "tests": 0, "describes": 0}
    unit_file_data: list[dict] = []
    for tf in sorted(unit_test_files):
        counts = count_tests_in_file(tf)
        unit_summary["files"] += 1
        unit_summary["tests"] += counts["tests"]
        unit_summary["describes"] += counts["describes"]
        try:
            rel = str(tf.relative_to(root))
        except ValueError:
            rel = str(tf)
        unit_file_data.append({"file": rel, **counts})

    e2e_summary = {"files": 0, "tests": 0, "describes": 0}
    e2e_file_data: list[dict] = []
    for tf in sorted(e2e_test_files):
        counts = count_tests_in_file(tf)
        e2e_summary["files"] += 1
        e2e_summary["tests"] += counts["tests"]
        e2e_summary["describes"] += counts["describes"]
        try:
            rel = str(tf.relative_to(root))
        except ValueError:
            rel = str(tf)
        e2e_file_data.append({"file": rel, **counts})

    # 集計
    total_min_tests = sum(c.get("minTests", {}).get("count", 0) for c in components_data)
    total_actual_unit = unit_summary["tests"]
    total_actual_e2e = e2e_summary["tests"]
    total_actual = total_actual_unit + total_actual_e2e

    gap = total_actual - total_min_tests
    coverage_pct = round(total_actual / total_min_tests * 100, 1) if total_min_tests > 0 else 0.0

    # 不足上位コンポーネント（minTests が多い順）
    top_missing = sorted(
        [
            {
                "file": c["file"],
                "name": c.get("name", ""),
                "minTests": c.get("minTests", {}).get("count", 0),
                "calculation": c.get("minTests", {}).get("calculation", ""),
            }
            for c in components_data
            if c.get("minTests", {}).get("count", 0) > 1
        ],
        key=lambda x: x["minTests"],
        reverse=True,
    )[:20]

    return {
        "projectRoot": str(root),
        "frameworks": frameworks,
        "components": components_data,
        "testFiles": {
            "unit": unit_file_data,
            "e2e": e2e_file_data,
        },
        "summary": {
            "components": {
                "total": len(component_files),
                "analyzed": len(components_data),
            },
            "minTests": {
                "total": total_min_tests,
                "topComplexComponents": top_missing,
            },
            "actualTests": {
                "unit": total_actual_unit,
                "e2e": total_actual_e2e,
                "total": total_actual,
            },
            "gap": {
                "delta": gap,
                "coveragePercent": coverage_pct,
                "status": "sufficient" if gap >= 0 else "insufficient",
            },
        },
    }


# ─────────────────────────────────────────────
# CLI エントリポイント
# ─────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="UIコンポーネントの最低テスト数を計算してカバレッジギャップをレポートする"
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="解析対象のプロジェクトディレクトリ（デフォルト: カレントディレクトリ）",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="JSON レポートの出力ファイルパス（省略時は stdout）",
    )
    parser.add_argument(
        "--component", "-c",
        default=None,
        help="解析対象コンポーネントの glob パターン（省略時は全コンポーネント）",
    )
    parser.add_argument(
        "--summary-only", "-s",
        action="store_true",
        help="サマリーのみ出力する（components 詳細を除く）",
    )

    args = parser.parse_args()

    result = run_analysis(args.project_dir, args.component)

    if args.summary_only:
        output = {
            "projectRoot": result["projectRoot"],
            "frameworks": result["frameworks"],
            "summary": result["summary"],
        }
    else:
        output = result

    json_str = json.dumps(output, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(json_str, encoding="utf-8")
        print(f"レポートを {args.output} に出力しました。", file=sys.stderr)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
