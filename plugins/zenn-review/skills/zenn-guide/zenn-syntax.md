# Zenn 固有構文 完全リファレンス

## メッセージブロック

情報・警告を目立たせるブロック要素。

```markdown
:::message
これは情報メッセージです。
:::

:::message alert
これは警告メッセージです。
:::
```

**構文ルール:**
- `:::message` で開始、`:::` で閉じる
- `alert` パラメータは任意（指定で警告スタイル）
- ブロック内にはMarkdown記法を使用可能
- ネストは不可

## アコーディオン（トグル）

```markdown
:::details タイトル
折りたたまれるコンテンツ
:::
```

**構文ルール:**
- `:::details` の後にスペースを挟んでタイトルを記述
- タイトルは必須
- ブロック内にはMarkdown記法を使用可能
- ネストは不可

## コードブロック

### 基本

````markdown
```language
code here
```
````

### ファイル名付き

````markdown
```language:filename.ext
code here
```
````

### diff 表示

````markdown
```diff language
- removed line
+ added line
```
````

**構文ルール:**
- 言語指定の後に `:ファイル名` でファイル名表示
- diff は `+` / `-` で追加/削除行を表示
- `diff` の後に言語名を指定するとシンタックスハイライト付きdiffになる

## 数式（KaTeX）

### インライン数式

```markdown
$a^2 + b^2 = c^2$ のように記述
```

### ブロック数式

```markdown
$$
e^{i\pi} + 1 = 0
$$
```

**構文ルール:**
- インライン: `$` で囲む
- ブロック: `$$` で囲む（前後に空行推奨）
- KaTeX 構文に従う

## 埋め込み（Embed）

### YouTube

```markdown
@[youtube](VIDEO_ID)
```

VIDEO_IDはURLではなく動画IDのみ（例: `dQw4w9WgXcQ`）

### X (Twitter)

```markdown
@[tweet](https://twitter.com/user/status/TWEET_ID)
```

### GitHub Gist

```markdown
@[gist](https://gist.github.com/user/GIST_ID)
```

### CodePen

```markdown
@[codepen](https://codepen.io/user/pen/PEN_ID)
```

### SlideShare

```markdown
@[slideshare](SLIDE_KEY)
```

### SpeakerDeck

```markdown
@[speakerdeck](SLIDE_ID)
```

### JSFiddle

```markdown
@[jsfiddle](https://jsfiddle.net/user/FIDDLE_ID)
```

### CodeSandbox

```markdown
@[codesandbox](SANDBOX_ID)
```

### StackBlitz

```markdown
@[stackblitz](PROJECT_ID)
```

### リンクカード

```markdown
@[card](https://example.com)
```

**構文ルール:**
- `@[サービス名](ID or URL)` の形式
- YouTubeはVIDEO_IDのみ（URLは不可）
- 各サービスごとにIDかURLかが決まっている

## 脚注

### 通常の脚注

```markdown
テキスト[^1]

[^1]: 脚注の内容
```

### インライン脚注（Zenn独自）

```markdown
テキスト^[脚注の内容をここに直接書く]
```

**構文ルール:**
- 通常の脚注: `[^番号]` で参照、`[^番号]: 内容` で定義
- インライン脚注: `^[内容]` で参照と定義を同時に記述
- 脚注の参照番号は一意であること

## 画像

### 基本

```markdown
![alt text](URL)
```

### サイズ指定

```markdown
![alt text](URL =250x)
```

**構文ルール:**
- 標準Markdown画像構文を使用
- `=幅x高さ` でサイズ指定（Zenn独自拡張）
- 高さは省略可能（`=250x` で幅250px、高さ自動）
- Zenn にアップロードした画像またはGyazo等の外部URLを使用

## テーブル

標準のMarkdownテーブル記法をサポート。

```markdown
| ヘッダ1 | ヘッダ2 |
|---------|---------|
| セル1   | セル2   |
```

## 区切り線

```markdown
---
```

フロントマターの `---` と混同しないよう注意。本文中では前後に空行を入れる。
