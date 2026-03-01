# フィルタープラグイン実装パターン（C/C++）

フィルタープラグインは既存のソースに適用するエフェクト処理。
グレースケール変換、ノイズ低減、クロマキーなどが代表例。

## 基本構造

```c
// my-filter.c
#include <obs-module.h>
#include <util/bmem.h>

struct my_filter_data {
    obs_source_t *context;   // フィルター自身のソース参照
    gs_effect_t  *effect;    // GLSL/HLSL エフェクト
    gs_eparam_t  *param_intensity;  // シェーダーパラメーター
    float intensity;
};

static const char *my_filter_get_name(void *unused)
{
    UNUSED_PARAMETER(unused);
    return obs_module_text("MyFilter.Name");
}

static void *my_filter_create(obs_data_t *settings, obs_source_t *context)
{
    struct my_filter_data *filter = bzalloc(sizeof(struct my_filter_data));
    filter->context = context;

    // エフェクトファイルをロード（data/ ディレクトリから）
    char *effect_path = obs_module_file("effects/my-effect.effect");
    obs_enter_graphics();
    filter->effect = gs_effect_create_from_file(effect_path, NULL);
    obs_leave_graphics();
    bfree(effect_path);

    if (!filter->effect) {
        my_filter_destroy(filter);
        return NULL;
    }

    filter->param_intensity = gs_effect_get_param_by_name(
        filter->effect, "intensity"
    );

    my_filter_update(filter, settings);
    return filter;
}

static void my_filter_destroy(void *data)
{
    struct my_filter_data *filter = data;

    obs_enter_graphics();
    gs_effect_destroy(filter->effect);
    obs_leave_graphics();

    bfree(filter);
}

static void my_filter_update(void *data, obs_data_t *settings)
{
    struct my_filter_data *filter = data;
    filter->intensity = (float)obs_data_get_double(settings, "intensity");
}

static obs_properties_t *my_filter_properties(void *unused)
{
    UNUSED_PARAMETER(unused);
    obs_properties_t *props = obs_properties_create();

    obs_properties_add_float_slider(
        props, "intensity", "Intensity", 0.0, 1.0, 0.01
    );

    return props;
}

static void my_filter_get_defaults(obs_data_t *settings)
{
    obs_data_set_default_double(settings, "intensity", 1.0);
}

// フィルター描画（前段のテクスチャを受け取り、エフェクトを適用）
static void my_filter_render(void *data, gs_effect_t *effect)
{
    struct my_filter_data *filter = data;

    if (!obs_source_process_filter_begin(filter->context, GS_RGBA,
                                        OBS_ALLOW_DIRECT_RENDERING)) {
        return;
    }

    // シェーダーパラメーターを設定
    gs_effect_set_float(filter->param_intensity, filter->intensity);

    obs_source_process_filter_end(filter->context, filter->effect, 0, 0);
}

// ---- obs_source_info 構造体（フィルター用） ----

struct obs_source_info my_filter_info = {
    .id             = "my_filter",
    .type           = OBS_SOURCE_TYPE_FILTER,  // フィルター種別
    .output_flags   = OBS_SOURCE_VIDEO,
    .get_name       = my_filter_get_name,
    .create         = my_filter_create,
    .destroy        = my_filter_destroy,
    .update         = my_filter_update,
    .get_properties = my_filter_properties,
    .get_defaults   = my_filter_get_defaults,
    .video_render   = my_filter_render,
};
```

## GLSL/HLSL エフェクトファイル

OBS はクロスプラットフォームシェーダーファイル（`.effect`）を使う:

```glsl
// data/effects/my-effect.effect
uniform float4x4 ViewProj;
uniform texture2d image;
uniform float intensity;

sampler_state textureSampler {
    Filter    = Linear;
    AddressU  = Clamp;
    AddressV  = Clamp;
};

struct VertData {
    float4 pos : POSITION;
    float2 uv  : TEXCOORD0;
};

VertData VSDefault(VertData v_in)
{
    VertData vert_out;
    vert_out.pos = mul(float4(v_in.pos.xyz, 1.0), ViewProj);
    vert_out.uv  = v_in.uv;
    return vert_out;
}

float4 PSMyEffect(VertData v_in) : TARGET
{
    float4 color = image.Sample(textureSampler, v_in.uv);
    // グレースケール変換の例
    float gray = dot(color.rgb, float3(0.299, 0.587, 0.114));
    color.rgb  = lerp(color.rgb, float3(gray, gray, gray), intensity);
    return color;
}

technique Draw
{
    pass
    {
        vertex_shader = VSDefault(v_in);
        pixel_shader  = PSMyEffect(v_in);
    }
}
```

## プラグインへの登録（plugin-main.c）

```c
extern struct obs_source_info my_filter_info;

bool obs_module_load(void)
{
    obs_register_source(&my_filter_info);
    return true;
}
```
