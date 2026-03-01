# C 言語ユニットテスト実装例

## OBS API のモック

OBS をインストールせずにテストするため、必要な関数をモックで実装する。

### mock_obs.h

```c
// test/mock_obs.h
#pragma once
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// 型定義
typedef void obs_source_t;
typedef void obs_data_t;

// ---- obs-module.h のモック ----
#define OBS_DECLARE_MODULE()
#define OBS_MODULE_USE_DEFAULT_LOCALE(plugin_id, locale)
#define UNUSED_PARAMETER(p) ((void)(p))

#define LOG_ERROR   100
#define LOG_WARNING 200
#define LOG_INFO    300
#define LOG_DEBUG   400

// blog() をprintf に置き換え
static inline void mock_blog(int level, const char *format, ...)
{
    const char *prefix = level <= LOG_ERROR ? "[ERROR]" :
                         level <= LOG_WARNING ? "[WARN]" :
                         level <= LOG_INFO ? "[INFO]" : "[DEBUG]";
    va_list args;
    printf("%s ", prefix);
    va_start(args, format);
    vprintf(format, args);
    va_end(args);
    printf("\n");
}
#define blog mock_blog

// obs_module_text() のモック
static inline const char *obs_module_text(const char *lookup_string)
{
    return lookup_string;  // キーをそのまま返す
}

// obs_module_file() のモック
static inline char *obs_module_file(const char *file)
{
    // テスト用: カレントディレクトリからのパスを返す
    char *path = malloc(256);
    snprintf(path, 256, "test/data/%s", file);
    return path;
}

// ---- obs-data.h のモック ----
typedef struct {
    const char *name;
    union {
        long long int_val;
        double       double_val;
        const char  *string_val;
        int          bool_val;
    };
    int type; // 0=int, 1=double, 2=string, 3=bool
} mock_data_entry;

#define MAX_MOCK_ENTRIES 32

typedef struct {
    mock_data_entry entries[MAX_MOCK_ENTRIES];
    int count;
} mock_obs_data;

static inline void mock_obs_data_set_int(mock_obs_data *d, const char *name, long long val)
{
    d->entries[d->count].name    = name;
    d->entries[d->count].int_val = val;
    d->entries[d->count].type    = 0;
    d->count++;
}

static inline long long obs_data_get_int(obs_data_t *data, const char *name)
{
    mock_obs_data *d = (mock_obs_data *)data;
    for (int i = 0; i < d->count; i++) {
        if (strcmp(d->entries[i].name, name) == 0 && d->entries[i].type == 0) {
            return d->entries[i].int_val;
        }
    }
    return 0;
}

static inline void obs_data_set_default_int(obs_data_t *data, const char *name, long long val)
{
    // テストでは無視（必要なら記録する）
    (void)data; (void)name; (void)val;
}

// ---- util/bmem.h のモック ----
static inline void *bzalloc(size_t size) { return calloc(1, size); }
static inline void bfree(void *ptr)       { free(ptr); }
static inline char *bstrdup(const char *s) { return s ? strdup(s) : NULL; }
```

### テストファイルの構成例

```c
// test/test_my_source.c
#include "test_utils.h"
#include "mock_obs.h"

// テスト対象のソースを直接インクルード
// （obs-module.h の代わりに mock_obs.h を使用）
#include "../src/my-source.c"

// ---------- テストケース ----------

void test_source_create_valid_settings(void)
{
    mock_obs_data settings = {0};
    mock_obs_data_set_int(&settings, "width",  1920);
    mock_obs_data_set_int(&settings, "height", 1080);

    void *data = my_source_create((obs_data_t *)&settings, NULL);
    ASSERT_NOT_NULL(data);

    struct my_source_data *src = data;
    ASSERT_EQ(src->width,  1920);
    ASSERT_EQ(src->height, 1080);

    my_source_destroy(data);
}

void test_source_get_dimensions(void)
{
    mock_obs_data settings = {0};
    mock_obs_data_set_int(&settings, "width",  640);
    mock_obs_data_set_int(&settings, "height", 480);

    void *data = my_source_create((obs_data_t *)&settings, NULL);
    ASSERT_NOT_NULL(data);

    uint32_t w = my_source_get_width(data);
    uint32_t h = my_source_get_height(data);
    ASSERT_EQ(w, 640);
    ASSERT_EQ(h, 480);

    my_source_destroy(data);
}

void test_source_update(void)
{
    mock_obs_data init_settings = {0};
    mock_obs_data_set_int(&init_settings, "width", 1280);
    mock_obs_data_set_int(&init_settings, "height", 720);

    void *data = my_source_create((obs_data_t *)&init_settings, NULL);
    ASSERT_NOT_NULL(data);

    // 設定を変更
    mock_obs_data new_settings = {0};
    mock_obs_data_set_int(&new_settings, "width", 1920);
    mock_obs_data_set_int(&new_settings, "height", 1080);
    my_source_update(data, (obs_data_t *)&new_settings);

    ASSERT_EQ(my_source_get_width(data),  1920);
    ASSERT_EQ(my_source_get_height(data), 1080);

    my_source_destroy(data);
}

// ---------- main ----------

int main(void)
{
    RUN_TEST(test_source_create_valid_settings);
    RUN_TEST(test_source_get_dimensions);
    RUN_TEST(test_source_update);

    PRINT_RESULTS();
    return 0;
}
```

### CMake でのテストビルド

```cmake
# test/CMakeLists.txt
add_executable(test_my_source
    test_my_source.c
)

target_include_directories(test_my_source
    PRIVATE
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# テストの登録
enable_testing()
add_test(NAME test_my_source COMMAND test_my_source)
```

```bash
# テスト実行
cmake -B build-test
cmake --build build-test
ctest --build-and-test . build-test --test-command ctest --verbose
```

## フィルタープラグインのテスト例

```c
void test_filter_intensity_clamp(void)
{
    // intensity は 0.0 〜 1.0 の範囲であることを確認
    mock_obs_data settings = {0};
    mock_obs_data_set_double(&settings, "intensity", 2.5);  // 範囲外

    void *data = my_filter_create((obs_data_t *)&settings, NULL);
    ASSERT_NOT_NULL(data);

    struct my_filter_data *filter = data;
    // クランプが機能しているか確認
    ASSERT_TRUE(filter->intensity >= 0.0f && filter->intensity <= 1.0f);

    my_filter_destroy(data);
}
```
