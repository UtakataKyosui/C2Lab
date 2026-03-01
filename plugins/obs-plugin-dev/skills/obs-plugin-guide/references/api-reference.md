# OBS API リファレンス

## 主要ヘッダーファイル

| ヘッダー | 内容 |
|---------|------|
| `obs-module.h` | モジュール必須マクロ・関数（必須インクルード） |
| `obs.h` | OBS コアAPI（ソース・シーン・出力管理） |
| `obs-properties.h` | プロパティUI定義API |
| `obs-data.h` | 設定データ（JSON/Key-Value） |
| `media-io/video-io.h` | 映像フォーマット定義 |
| `media-io/audio-io.h` | 音声フォーマット定義 |
| `graphics/graphics.h` | グラフィックスAPI（テクスチャ・エフェクト） |
| `util/bmem.h` | メモリ管理（bzalloc/bfree） |
| `util/darray.h` | 動的配列 |

## obs-module.h の主要マクロ

```c
// モジュール宣言（必須）
OBS_DECLARE_MODULE()

// ロケールの自動読み込み
OBS_MODULE_USE_DEFAULT_LOCALE("plugin-id", "en-US")

// ロケール文字列取得
const char *text = obs_module_text("Key.Name");

// プラグインのデータディレクトリからファイルパス取得
char *path = obs_module_file("effects/my.effect");
// 使い終わったら bfree(path)
```

## ソース管理 API（obs.h）

```c
// ソース登録
void obs_register_source(const struct obs_source_info *info);

// ソースの参照カウント
obs_source_t *obs_source_get_ref(obs_source_t *source);
void          obs_source_release(obs_source_t *source);

// ソースのサイズ取得
uint32_t obs_source_get_width(obs_source_t *source);
uint32_t obs_source_get_height(obs_source_t *source);

// ソースの名前
const char *obs_source_get_name(const obs_source_t *source);

// フィルター処理（フィルタープラグイン内で使用）
bool obs_source_process_filter_begin(obs_source_t *filter,
                                     enum gs_color_format format,
                                     enum obs_allow_direct_render direct);
void obs_source_process_filter_end(obs_source_t *filter,
                                   gs_effect_t *effect,
                                   uint32_t width, uint32_t height);
```

## プロパティ API（obs-properties.h）

```c
// プロパティコンテナ生成
obs_properties_t *obs_properties_create(void);

// 各種プロパティ追加
obs_property_t *obs_properties_add_bool(obs_properties_t *props,
    const char *name, const char *description);

obs_property_t *obs_properties_add_int(obs_properties_t *props,
    const char *name, const char *description,
    int min, int max, int step);

obs_property_t *obs_properties_add_float_slider(obs_properties_t *props,
    const char *name, const char *description,
    double min, double max, double step);

obs_property_t *obs_properties_add_text(obs_properties_t *props,
    const char *name, const char *description,
    enum obs_text_type type);  // OBS_TEXT_DEFAULT / OBS_TEXT_PASSWORD / OBS_TEXT_MULTILINE

obs_property_t *obs_properties_add_list(obs_properties_t *props,
    const char *name, const char *description,
    enum obs_combo_type type,    // OBS_COMBO_TYPE_EDITABLE / OBS_COMBO_TYPE_LIST
    enum obs_combo_format format); // OBS_COMBO_FORMAT_INT / OBS_COMBO_FORMAT_STRING

// リストに選択肢を追加
obs_property_list_add_string(obs_property_t *prop, const char *name, const char *val);
obs_property_list_add_int(obs_property_t *prop, const char *name, long long val);

// プロパティの解放（OBS が自動的に行う場合が多い）
obs_properties_destroy(obs_properties_t *props);
```

## 設定データ API（obs-data.h）

```c
// 値の取得
bool        obs_data_get_bool(obs_data_t *data, const char *name);
long long   obs_data_get_int(obs_data_t *data, const char *name);
double      obs_data_get_double(obs_data_t *data, const char *name);
const char *obs_data_get_string(obs_data_t *data, const char *name);

// デフォルト値の設定
void obs_data_set_default_bool(obs_data_t *data, const char *name, bool val);
void obs_data_set_default_int(obs_data_t *data, const char *name, long long val);
void obs_data_set_default_double(obs_data_t *data, const char *name, double val);
void obs_data_set_default_string(obs_data_t *data, const char *name, const char *val);
```

## グラフィックス API（graphics/graphics.h）

```c
// グラフィックスコンテキストへの入退出
void obs_enter_graphics(void);
void obs_leave_graphics(void);

// テクスチャ操作
gs_texture_t *gs_texture_create(uint32_t width, uint32_t height,
    enum gs_color_format color_format, uint32_t levels,
    const uint8_t **data, uint32_t flags);
void gs_texture_destroy(gs_texture_t *tex);
bool gs_texture_map(gs_texture_t *tex, uint8_t **ptr, uint32_t *linesize);
void gs_texture_unmap(gs_texture_t *tex);

// エフェクト操作
gs_effect_t *gs_effect_create_from_file(const char *file, char **error_string);
void         gs_effect_destroy(gs_effect_t *effect);
gs_eparam_t *gs_effect_get_param_by_name(gs_effect_t *effect, const char *name);
void         gs_effect_set_float(gs_eparam_t *param, float val);
void         gs_effect_set_texture(gs_eparam_t *param, gs_texture_t *val);
```

## ログ API

```c
// ログ出力（blog = "Beholder log"）
blog(LOG_INFO,    "メッセージ: %s", value);
blog(LOG_WARNING, "警告: %d", code);
blog(LOG_ERROR,   "エラー: %s", error_msg);
blog(LOG_DEBUG,   "デバッグ情報");
```

## メモリ管理 API（util/bmem.h）

```c
void *bzalloc(size_t size);   // ゼロ初期化アロケート
void *brealloc(void *ptr, size_t size);
void  bfree(void *ptr);

char *bstrdup(const char *str);   // 文字列複製
char *bstrdup_n(const char *str, size_t n);
```
