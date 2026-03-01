# OBS プラグインのデバッグ方法

## ログ出力（`blog()`）

最も基本的なデバッグ手段。OBS のログに出力される:

```c
// C/C++
#include <obs-module.h>

blog(LOG_INFO,    "プラグインのバージョン: %s", "0.1.0");
blog(LOG_WARNING, "設定が見つかりません: %s", key_name);
blog(LOG_ERROR,   "初期化失敗: %d", error_code);
blog(LOG_DEBUG,   "create() called, width=%d height=%d", w, h);
```

OBS のログは以下に出力される:
- Linux: `~/.config/obs-studio/logs/`
- macOS: `~/Library/Logs/obs-studio/`
- Windows: `%APPDATA%\obs-studio\logs\`

## GDB によるデバッグ（Linux/macOS）

### OBS をデバッガ下で起動

```bash
# デバッグビルドのプラグインをインストール後
gdb --args obs

# GDB 内でブレークポイントを設定
(gdb) break my_source_create
(gdb) break my_source_destroy
(gdb) run

# OBS 起動後、プラグインがロードされたらブレークポイントに到達
```

### プラグインがロードされる前にブレークを設定

```bash
# obs_module_load にブレークポイント
(gdb) break obs_module_load
(gdb) run

# ロード後のシンボルが見える
(gdb) info functions my_source
```

### LLDB（macOS）

```bash
lldb -- obs

(lldb) breakpoint set --name my_source_create
(lldb) run
```

## Valgrind によるメモリリーク検出（Linux）

```bash
# OBS を Valgrind 下で起動
valgrind --leak-check=full \
         --track-origins=yes \
         --suppressions=/path/to/obs.supp \
         obs

# または特定のシナリオだけテスト
valgrind --leak-check=full obs --scene test-scene
```

### よくあるメモリリークパターン

```c
// 悪い例: create でメモリ確保、destroy で解放忘れ
static void *my_source_create(obs_data_t *settings, obs_source_t *source)
{
    struct my_data *data = bzalloc(sizeof(struct my_data));
    data->name = bstrdup(obs_data_get_string(settings, "name"));
    return data;
    // data->name が解放されない!
}

// 良い例: destroy で全リソースを解放
static void my_source_destroy(void *priv)
{
    struct my_data *data = priv;
    bfree(data->name);  // 文字列を解放
    bfree(data);         // 構造体本体を解放
}
```

## AddressSanitizer (ASan) の使用

```bash
# CMake でビルド時に ASan を有効化
cmake -B build \
    -DCMAKE_C_FLAGS="-fsanitize=address -g" \
    -DCMAKE_CXX_FLAGS="-fsanitize=address -g" \
    -DCMAKE_BUILD_TYPE=Debug

cmake --build build

# ASan 有効で OBS を起動
ASAN_OPTIONS=detect_leaks=1 obs
```

## ThreadSanitizer (TSan)

OBS はマルチスレッドなので、競合状態の検出に有効:

```bash
cmake -B build \
    -DCMAKE_C_FLAGS="-fsanitize=thread -g" \
    -DCMAKE_BUILD_TYPE=Debug

cmake --build build
TSAN_OPTIONS="second_deadlock_stack=1" obs
```

## プラグインの単体テスト

OBS プロセスを起動せずにテストする方法:

```c
// test/test_my_source.c
#include <stdio.h>
#include <assert.h>

// OBS ヘッダーをモックで代替
#include "mock_obs.h"

#include "../src/my-source.c"

void test_create_destroy(void)
{
    // モック設定データ
    mock_obs_data_t settings = {0};
    mock_obs_data_set_int(&settings, "width", 1920);
    mock_obs_data_set_int(&settings, "height", 1080);

    void *data = my_source_create((obs_data_t *)&settings, NULL);
    assert(data != NULL);

    my_source_destroy(data);
    printf("PASS: test_create_destroy\n");
}

int main(void)
{
    test_create_destroy();
    return 0;
}
```

## OBS ログレベルの有効化

```bash
# デバッグレベルのログを有効化（--verbose フラグ）
obs --verbose

# または環境変数
OBS_LOG_LEVEL=DEBUG obs
```

## クラッシュダンプの解析

```bash
# コアダンプを有効化
ulimit -c unlimited

# クラッシュ後のコアを解析
gdb obs core.dump
(gdb) bt  # バックトレース表示
(gdb) info locals
```
