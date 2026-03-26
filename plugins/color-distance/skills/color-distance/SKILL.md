---
name: color-distance
description: 色と色の距離を数値で測定するスキル。Delta E (CIE76/CIE94/CIEDE2000)・WCAG コントラスト比・RGB ユークリッド距離の計算手順と閾値判定を提供する。CSS/デザイントークン/Tailwind 設定ファイル編集時に自動発火。
globs:
  - "**/*.css"
  - "**/*.scss"
  - "**/*.sass"
  - "**/tailwind.config.*"
  - "**/*tokens*"
  - "**/*theme*"
---

# Color Distance — 色距離・アクセシビリティ測定スキル

ユーザーが 2 色の「離れ方（距離）」や「見やすさ（コントラスト）」を確認・設計するときに使うスキル。
**まずアクセシビリティ基準を満たすことを確認し、次に知覚的距離を計算する**という順序で進める。

---

## 色選択のワークフロー（推奨順序）

```
Step 1: WCAG 1.4.1 — 色だけで情報を伝えていないか確認
Step 2: WCAG 1.4.3/1.4.6 — テキスト・背景のコントラスト比
Step 3: WCAG 1.4.11 — UI コンポーネント・アイコンのコントラスト
Step 4: WCAG 2.4.7/2.4.11 — フォーカスインジケーターの視認性
Step 5: ΔE CIEDE2000 — パレット内の色の区別・識別性
Step 6: 色覚多様性シミュレーション — 全ユーザーへの配慮
```

---

## WCAG 達成基準 早見表

| SC | 名称 | レベル | 閾値 | 対象 |
|---|---|---|---|---|
| 1.4.1 | 色の使用 | A | 色だけで伝えない | テキスト・UI・グラフ |
| 1.4.3 | コントラスト（最小） | AA | テキスト 4.5:1 / 大テキスト 3:1 | 文字と背景 |
| 1.4.6 | コントラスト（拡張） | AAA | テキスト 7:1 / 大テキスト 4.5:1 | 文字と背景 |
| 1.4.11 | 非テキストのコントラスト | AA | 3:1 | UI 部品・グラフィック |
| 2.4.7 | フォーカスの可視性 | AA | 見えること | フォーカスリング |
| 2.4.11 | フォーカスの外観 | AA (2.2) | 3:1 + 最小面積 | フォーカスリング |

「大テキスト」= 18pt (24px) 以上、または 14pt (18.67px) 以上の太字。

---

## WCAG 1.4.1 — 色の使用（色だけで情報を伝えない）

**要件**: 色だけを唯一の視覚的手段として、情報・アクション・結果・区別を伝えてはならない。

### NG パターン → OK パターン

| NG | OK |
|---|---|
| エラーフィールドを赤枠だけで示す | 赤枠 + エラーアイコン + エラーテキスト |
| 「赤いボタンをクリック」と説明する | 「送信ボタン（赤）をクリック」と形状も示す |
| リンクを色だけで区別する | リンクに下線を付ける（またはホバー時に下線） |
| グラフの系列を色だけで区別する | 色 + 模様・形状・ラベルで区別 |
| 必須項目を赤いアスタリスクだけで示す | `* 必須` とテキストでも明示 |

### 色覚多様性（Color Vision Deficiency）

色盲の種類と影響を受ける色の組み合わせ:

| 種類 | 割合 | 混同しやすい色 |
|---|---|---|
| 第1色盲 Protanopia（赤欠如） | 男性の約1% | 赤 ↔ 黒/暗緑、赤 ↔ 緑 |
| 第2色盲 Deuteranopia（緑欠如） | 男性の約1% | 赤 ↔ 緑、橙 ↔ 黄緑 |
| 第1・第2色弱 Protanomaly/Deuteranomaly | 男性の約8% | 上記を薄く |
| 第3色盲 Tritanopia（青欠如） | 極めて稀 | 青 ↔ 緑、黄 ↔ 紫 |

**避けるべき色の組み合わせ**（成功/エラーの区別など）:
- 赤 (`#f00`) と緑 (`#0f0`) — 最も多い混同
- 赤 (`#f00`) と茶/橙 — Deuteranopia で識別困難
- 紫と青 — Tritanopia で識別困難

**シミュレーションツール**:
- Chrome DevTools → Rendering タブ → Emulate vision deficiencies
- Figma プラグイン: Able, Contrast, Color Blind
- CLI: `daltonize` (Python)
- Web: https://www.toptal.com/designers/colorfilter

---

## WCAG 1.4.3 / 1.4.6 — テキストのコントラスト比

### 計算式（WCAG 定義）

```
相対輝度 L = 0.2126*R_lin + 0.7152*G_lin + 0.0722*B_lin

ガンマ除去（線形化）:
  c_norm = c / 255
  c_lin  = c_norm / 12.92            if c_norm <= 0.03928
           ((c_norm + 0.055) / 1.055) ^ 2.4  otherwise

コントラスト比 = (L_明 + 0.05) / (L_暗 + 0.05)
```

### 判定基準

| 比率 | 判定 |
|---|---|
| ≥ 7.0 : 1 | AAA テキスト合格 |
| ≥ 4.5 : 1 | AA テキスト合格 |
| ≥ 4.5 : 1 | AAA 大テキスト合格 |
| ≥ 3.0 : 1 | AA 大テキスト合格 |
| < 3.0 : 1 | 不合格 |

---

## WCAG 1.4.11 — 非テキストのコントラスト（3:1）

**対象**: テキスト以外の UI コンポーネントとグラフィック要素。

### 対象・非対象

| 対象（3:1 必要） | 対象外（3:1 不要） |
|---|---|
| ボタン枠線（背景との境界） | 無効化されたコンポーネント |
| チェックボックス・ラジオボタン | ロゴ・装飾的な画像 |
| テキスト入力フィールドの枠線 | テキスト自体（1.4.3 が適用） |
| アイコン（情報を伝えるもの） | ブランドカラーが必須な場合 |
| グラフの線・データポイント | |
| フォーム要素の選択状態 | |

### 計算方法

非テキスト要素は **隣接する色との比率**を計算する。

```
例: 白背景(#fff)上の灰色ボタン枠線(#767676)
  L_白  = 1.0000
  L_灰  = 0.2159
  コントラスト = (1.0+0.05) / (0.2159+0.05) = 3.95:1 → AA 合格(≥3.0)

例: 白背景(#fff)上の薄い灰色枠線(#c0c0c0)
  L_灰  = 0.5271
  コントラスト = (1.0+0.05) / (0.5271+0.05) = 1.83:1 → 不合格
```

### 状態変化への注意

フォーカス・ホバー・選択・エラーなどの各**状態**でも 3:1 を満たすこと。

---

## WCAG 2.4.7 / 2.4.11 — フォーカスインジケーター

### 2.4.7 (AA): フォーカスの可視性
キーボード操作可能な要素は、フォーカス時に視覚的なインジケーターが見えること。
`outline: none` / `outline: 0` だけを設定し代替を用意しないのは違反。

### 2.4.11 (AA, WCAG 2.2): フォーカスの外観
フォーカスインジケーターが以下を満たすこと:
- **面積**: フォーカスリングの境界は要素外周の長さ × 2px 分の面積以上
- **コントラスト**: フォーカス色と背景色 ≥ 3:1、かつフォーカス色とフォーカス前の要素色 ≥ 3:1

```
例: 白背景(#fff)上の青フォーカスリング(#0ea5e9)
  L_青  = 0.2467
  コントラスト vs 白 = (1.0+0.05) / (0.2467+0.05) = 3.54:1 → 合格(≥3.0)
```

---

## 色距離の計算式

### RGB → 線形 RGB（ガンマ除去）

WCAG・CIE Lab 変換で必要。

```
c_norm = c / 255
c_lin  = c_norm / 12.92                      if c_norm <= 0.03928
         ((c_norm + 0.055) / 1.055) ^ 2.4    otherwise
```

### 線形 RGB → XYZ（D65 光源）

```
X = 0.4124564*R + 0.3575761*G + 0.1804375*B
Y = 0.2126729*R + 0.7151522*G + 0.0721750*B
Z = 0.0193339*R + 0.1191920*G + 0.9503041*B
```

### XYZ → CIE Lab

D65 白色点: Xn=0.95047, Yn=1.00000, Zn=1.08883

```
f(t): t^(1/3)               if t > 0.008856
      7.787*t + 16/116       otherwise

L* = 116 * f(Y/Yn) - 16
a* = 500 * (f(X/Xn) - f(Y/Yn))
b* = 200 * (f(Y/Yn) - f(Z/Zn))
```

---

### Delta E CIE76（簡易・高速）

```
ΔE76 = sqrt((L₂-L₁)² + (a₂-a₁)² + (b₂-b₁)²)
```

| ΔE | 人間の知覚 |
|---|---|
| 0–1 | 知覚不能（同一色に見える） |
| 1–2 | わずかに気づく（並べると分かる） |
| 2–10 | 明確な差（一目で違う） |
| 11–49 | 大きく異なる色 |
| ≥ 50 | 補色レベルの対極 |

青系で誤差が大きいため簡易チェック向け。

---

### Delta E CIE94（産業向け）

```
C₁* = sqrt(a₁²+b₁²),  C₂* = sqrt(a₂²+b₂²)
ΔL* = L₂ - L₁
ΔC* = C₂* - C₁*
ΔH* = sqrt(max(0, ΔE76² - ΔL*² - ΔC*²))

SC = 1 + 0.045*C₁*
SH = 1 + 0.015*C₁*

ΔE94 = sqrt(ΔL*² + (ΔC*/SC)² + (ΔH*/SH)²)
```

印刷・UI デザイン向け。CIE76 より均一な知覚を反映。

---

### Delta E CIEDE2000（最高精度）

```
主な補正:
  - L* 中間域の知覚均一化
  - a* 軸の回転補正（青緑境界の歪み修正）
  - 色相差の重み付け（RT 回転項）

SL = 1 + 0.015*(L'_avg-50)² / sqrt(20+(L'_avg-50)²)
SC = 1 + 0.045*C'_avg
SH = 1 + 0.015*C'_avg*T
RT = sin(2*Δθ) * RC   (青系回転補正)

ΔE00 = sqrt((ΔL'/SL)² + (ΔC'/SC)² + (ΔH'/SH)² + RT*(ΔC'/SC)*(ΔH'/SH))
```

現在最も正確。UI デザインレビュー・ブランドカラー管理に推奨。

**パレット内の色識別性の目安**:

| ΔE00 | 推奨用途 |
|---|---|
| ≥ 10 | 状態色（成功/警告/エラー/情報）の区別 |
| ≥ 5 | UI 要素間の明確な区別 |
| 2–5 | 隣接要素の微妙なグラデーション |
| < 2 | ほぼ同一色（意図的でない場合は修正） |

---

### RGB ユークリッド距離（最簡易）

```
d = sqrt((R₂-R₁)² + (G₂-G₁)² + (B₂-B₁)²)
正規化: d / 441.7 * 100  [%]
```

精度は低い。プログラム上のクイックチェックのみ。

---

## 使用シーン別の推奨指標

| シーン | 推奨指標 | 閾値 |
|---|---|---|
| テキスト・背景の視認性（AA） | WCAG コントラスト比 | ≥ 4.5:1（通常）/ ≥ 3:1（大テキスト） |
| テキスト・背景の視認性（AAA） | WCAG コントラスト比 | ≥ 7:1（通常）/ ≥ 4.5:1（大テキスト） |
| ボタン枠線・入力欄・アイコン | WCAG コントラスト比 1.4.11 | ≥ 3:1 |
| フォーカスリング | WCAG コントラスト比 2.4.11 | ≥ 3:1 |
| 状態色の区別（成功/エラー等） | ΔE CIEDE2000 + 1.4.1 確認 | ≥ 10 |
| パレット内の色識別 | ΔE CIEDE2000 | ≥ 5 |
| 印刷・ブランドカラー管理 | ΔE CIE94 / CIEDE2000 | — |
| 簡易プロトタイピング | RGB ユークリッド距離 | — |

---

## APCA — WCAG 3.0 草案（参考情報）

**APCA** (Advanced Perceptual Contrast Algorithm) は WCAG 3.0 で採用予定の新しいコントラスト測定アルゴリズム。

- 従来の輝度差比率ではなく、**人間の視覚神経の知覚特性**に基づく
- Lc（Lightness Contrast）値で表現。フォント・サイズ・ウェイトに応じた閾値テーブルを使う

**Lc 値の目安**:

| Lc 絶対値 | 用途 |
|---|---|
| 90 以上 | 本文・重要コンテンツ |
| 75 以上 | 見出し・UI テキスト |
| 60 以上 | 大きな見出し（24px 以上） |
| 45 以上 | 装飾的・補足テキスト |
| 30 以上 | プレースホルダー・非アクティブ |

**現時点での注意**: WCAG 2.x のコントラスト比が法的・規制要件の基準。APCA は補足参考として用いる。

---

## 実装コードスニペット

### JavaScript

```javascript
// RGB → 相対輝度
function relativeLuminance(r, g, b) {
  return [r, g, b].reduce((acc, c, i) => {
    const n = c / 255;
    const lin = n <= 0.03928 ? n / 12.92 : ((n + 0.055) / 1.055) ** 2.4;
    return acc + lin * [0.2126, 0.7152, 0.0722][i];
  }, 0);
}

// WCAG コントラスト比（1.4.3 / 1.4.11 共通）
function wcagContrast(rgb1, rgb2) {
  const l1 = relativeLuminance(...rgb1);
  const l2 = relativeLuminance(...rgb2);
  const [bright, dark] = l1 > l2 ? [l1, l2] : [l2, l1];
  return (bright + 0.05) / (dark + 0.05);
}

// WCAG 判定（テキスト用）
function checkTextContrast(rgb1, rgb2, isLargeText = false) {
  const ratio = wcagContrast(rgb1, rgb2);
  const aa = isLargeText ? 3.0 : 4.5;
  const aaa = isLargeText ? 4.5 : 7.0;
  return {
    ratio: ratio.toFixed(2),
    AA: ratio >= aa,
    AAA: ratio >= aaa,
  };
}

// WCAG 1.4.11 判定（非テキスト）
function checkNonTextContrast(componentRgb, adjacentRgb) {
  const ratio = wcagContrast(componentRgb, adjacentRgb);
  return { ratio: ratio.toFixed(2), pass: ratio >= 3.0 };
}

// RGB → Lab
function rgbToLab(r, g, b) {
  const lin = [r, g, b].map(c => {
    const n = c / 255;
    return n <= 0.03928 ? n / 12.92 : ((n + 0.055) / 1.055) ** 2.4;
  });
  const X = 0.4124564*lin[0] + 0.3575761*lin[1] + 0.1804375*lin[2];
  const Y = 0.2126729*lin[0] + 0.7151522*lin[1] + 0.0721750*lin[2];
  const Z = 0.0193339*lin[0] + 0.1191920*lin[1] + 0.9503041*lin[2];
  const f = t => t > 0.008856 ? t ** (1/3) : 7.787*t + 16/116;
  const [fx, fy, fz] = [f(X/0.95047), f(Y/1.0), f(Z/1.08883)];
  return [116*fy - 16, 500*(fx-fy), 200*(fy-fz)];
}

// Delta E CIE76
function deltaE76(rgb1, rgb2) {
  const [L1,a1,b1] = rgbToLab(...rgb1);
  const [L2,a2,b2] = rgbToLab(...rgb2);
  return Math.sqrt((L2-L1)**2 + (a2-a1)**2 + (b2-b1)**2);
}

// Delta E CIE94
function deltaE94(rgb1, rgb2) {
  const [L1,a1,b1] = rgbToLab(...rgb1);
  const [L2,a2,b2] = rgbToLab(...rgb2);
  const C1 = Math.sqrt(a1**2 + b1**2);
  const C2 = Math.sqrt(a2**2 + b2**2);
  const dL = L2 - L1, dC = C2 - C1;
  const dH = Math.sqrt(Math.max(0, (L2-L1)**2 + (a2-a1)**2 + (b2-b1)**2 - dL**2 - dC**2));
  const SC = 1 + 0.045*C1, SH = 1 + 0.015*C1;
  return Math.sqrt(dL**2 + (dC/SC)**2 + (dH/SH)**2);
}

// 使用例
const blue = [29, 78, 216];
const white = [255, 255, 255];
console.log("Text AA:", checkTextContrast(blue, white));
console.log("Non-text:", checkNonTextContrast(blue, white));
console.log("ΔE94:", deltaE94(blue, white).toFixed(1));
```

### Python

```python
import math

def relative_luminance(r, g, b):
    def lin(c):
        n = c / 255
        return n / 12.92 if n <= 0.03928 else ((n + 0.055) / 1.055) ** 2.4
    return 0.2126*lin(r) + 0.7152*lin(g) + 0.0722*lin(b)

def wcag_contrast(c1, c2):
    l1, l2 = relative_luminance(*c1), relative_luminance(*c2)
    bright, dark = (l1, l2) if l1 > l2 else (l2, l1)
    return (bright + 0.05) / (dark + 0.05)

def check_text_contrast(c1, c2, large_text=False):
    ratio = wcag_contrast(c1, c2)
    aa, aaa = (3.0, 4.5) if large_text else (4.5, 7.0)
    return {"ratio": f"{ratio:.2f}", "AA": ratio >= aa, "AAA": ratio >= aaa}

def check_non_text_contrast(component, adjacent):
    ratio = wcag_contrast(component, adjacent)
    return {"ratio": f"{ratio:.2f}", "pass": ratio >= 3.0}

def rgb_to_lab(r, g, b):
    def lin(c):
        n = c / 255
        return n / 12.92 if n <= 0.03928 else ((n + 0.055) / 1.055) ** 2.4
    rl, gl, bl = lin(r), lin(g), lin(b)
    X = 0.4124564*rl + 0.3575761*gl + 0.1804375*bl
    Y = 0.2126729*rl + 0.7151522*gl + 0.0721750*bl
    Z = 0.0193339*rl + 0.1191920*gl + 0.9503041*bl
    def f(t): return t**(1/3) if t > 0.008856 else 7.787*t + 16/116
    fx, fy, fz = f(X/0.95047), f(Y/1.0), f(Z/1.08883)
    return 116*fy - 16, 500*(fx-fy), 200*(fy-fz)

def delta_e94(c1, c2):
    L1,a1,b1 = rgb_to_lab(*c1)
    L2,a2,b2 = rgb_to_lab(*c2)
    C1 = math.sqrt(a1**2 + b1**2)
    C2 = math.sqrt(a2**2 + b2**2)
    dL, dC = L2-L1, C2-C1
    de76_sq = (L2-L1)**2 + (a2-a1)**2 + (b2-b1)**2
    dH = math.sqrt(max(0, de76_sq - dL**2 - dC**2))
    SC, SH = 1+0.045*C1, 1+0.015*C1
    return math.sqrt(dL**2 + (dC/SC)**2 + (dH/SH)**2)

# 使用例
blue, white = (29, 78, 216), (255, 255, 255)
print("Text AA:", check_text_contrast(blue, white))
print("Non-text:", check_non_text_contrast(blue, white))
print(f"ΔE94: {delta_e94(blue, white):.1f}")
```

---

## 入力フォーマット対応

| フォーマット | 例 | 変換 |
|---|---|---|
| HEX 6桁 | `#1a2b3c` | `parseInt(hex.slice(1,3), 16)` |
| HEX 3桁 | `#abc` | → `#aabbcc` に展開 |
| RGB 関数 | `rgb(26, 43, 60)` | 数値を直接抽出 |
| HSL 関数 | `hsl(210, 40%, 17%)` | HSL → RGB 変換 |
| CSS 名前色 | `red`, `white` | CSS 仕様の対応表を参照 |

---

## よくある質問

**Q: WCAG と ΔE どちらを使えばいい？**
→ テキスト・UI の視認性は **WCAG コントラスト比**（法的要件）。パレット内の色の「区別しやすさ」には **ΔE CIEDE2000**（知覚的距離）。

**Q: 赤と緑のボタンでOK/NGを区別したい**
→ 色盲ユーザー（男性の約8%）が区別できない。アイコン（✓/✗）・テキスト・形状の違いを必ず加える（WCAG 1.4.1）。

**Q: WCAG 2.x と WCAG 3.0/APCA どちらを使う？**
→ 現行の法的要件は **WCAG 2.x**（2.1 または 2.2）。APCA は補足参考として活用できるが、準拠判定には使わない。

**Q: ダークモードでも確認が必要？**
→ 必要。ライトモード・ダークモード双方で各 SC を満たすこと。背景色が変わると同じ要素色でもコントラスト比が変わる。

**Q: プレースホルダーテキストにも 4.5:1 が必要？**
→ プレースホルダーはテキストに該当するため 4.5:1 が必要（ただし、プレースホルダーをラベルの代替にしてはならない）。
