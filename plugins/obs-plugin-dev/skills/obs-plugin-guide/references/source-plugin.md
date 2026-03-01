# ソースプラグイン実装パターン（C/C++）

ソースプラグインは映像・音声の入力源を提供する。カメラ、スクリーンキャプチャ、
テキスト生成などが代表例。

## 基本構造

```c
// my-source.c
#include <obs-module.h>
#include <util/bmem.h>

// プラグイン内部データ構造
struct my_source_data {
    obs_source_t *source;
    uint32_t     width;
    uint32_t     height;
    // ... その他の状態
};

// ---- コールバック関数の実装 ----

static const char *my_source_get_name(void *unused)
{
    UNUSED_PARAMETER(unused);
    return obs_module_text("MySource.Name");
}

static void *my_source_create(obs_data_t *settings, obs_source_t *source)
{
    struct my_source_data *data = bzalloc(sizeof(struct my_source_data));
    data->source = source;
    data->width  = obs_data_get_int(settings, "width");
    data->height = obs_data_get_int(settings, "height");

    // 初期化処理...
    return data;
}

static void my_source_destroy(void *priv)
{
    struct my_source_data *data = priv;
    // リソース解放
    bfree(data);
}

static void my_source_update(void *priv, obs_data_t *settings)
{
    struct my_source_data *data = priv;
    data->width  = obs_data_get_int(settings, "width");
    data->height = obs_data_get_int(settings, "height");
}

static obs_properties_t *my_source_properties(void *unused)
{
    UNUSED_PARAMETER(unused);
    obs_properties_t *props = obs_properties_create();

    obs_properties_add_int(props, "width",  "Width",  1, 4096, 1);
    obs_properties_add_int(props, "height", "Height", 1, 4096, 1);

    return props;
}

static void my_source_get_defaults(obs_data_t *settings)
{
    obs_data_set_default_int(settings, "width",  1920);
    obs_data_set_default_int(settings, "height", 1080);
}

static uint32_t my_source_get_width(void *priv)
{
    struct my_source_data *data = priv;
    return data->width;
}

static uint32_t my_source_get_height(void *priv)
{
    struct my_source_data *data = priv;
    return data->height;
}

// 映像描画コールバック（毎フレーム呼ばれる）
static void my_source_render(void *priv, gs_effect_t *effect)
{
    struct my_source_data *data = priv;
    UNUSED_PARAMETER(effect);

    // gs_* 関数で描画処理
    // obs_source_draw() などを使ってテクスチャを描画
}

// ---- obs_source_info 構造体 ----

struct obs_source_info my_source_info = {
    .id             = "my_source",
    .type           = OBS_SOURCE_TYPE_INPUT,
    .output_flags   = OBS_SOURCE_VIDEO,
    .get_name       = my_source_get_name,
    .create         = my_source_create,
    .destroy        = my_source_destroy,
    .update         = my_source_update,
    .get_properties = my_source_properties,
    .get_defaults   = my_source_get_defaults,
    .video_render   = my_source_render,
    .get_width      = my_source_get_width,
    .get_height     = my_source_get_height,
};
```

## 音声ソースの場合

```c
struct obs_source_info my_audio_source_info = {
    .id           = "my_audio_source",
    .type         = OBS_SOURCE_TYPE_INPUT,
    .output_flags = OBS_SOURCE_AUDIO,  // 音声フラグ
    .get_name     = my_audio_source_get_name,
    .create       = my_audio_source_create,
    .destroy      = my_audio_source_destroy,
    // audio_render を実装
};
```

## obs_source_info の主要フラグ

| フラグ | 意味 |
|--------|------|
| `OBS_SOURCE_VIDEO` | 映像を出力する |
| `OBS_SOURCE_AUDIO` | 音声を出力する |
| `OBS_SOURCE_ASYNC` | 非同期映像フレームを使用 |
| `OBS_SOURCE_DO_NOT_DUPLICATE` | シーン複製時に複製しない |
| `OBS_SOURCE_CONTROLLABLE_MEDIA` | メディア制御 UI を表示 |

## テクスチャ操作

```c
// テクスチャの作成
gs_texture_t *tex = gs_texture_create(width, height, GS_BGRA, 1, NULL, GS_DYNAMIC);

// ピクセルデータの書き込み
uint8_t *ptr;
uint32_t linesize;
if (gs_texture_map(tex, &ptr, &linesize)) {
    // ptr にピクセルデータを書き込む
    gs_texture_unmap(tex);
}

// テクスチャの解放
gs_texture_destroy(tex);
```
