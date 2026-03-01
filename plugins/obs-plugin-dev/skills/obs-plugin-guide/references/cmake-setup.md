# CMakeLists.txt 詳細設定

## 最小構成（C プラグイン）

```cmake
cmake_minimum_required(VERSION 3.16)
project(my-obs-plugin VERSION 0.1.0)

# OBS SDK を検索
find_package(libobs REQUIRED)

# MODULE: dlopen でロードされる共有ライブラリ
add_library(my-obs-plugin MODULE
    src/plugin-main.c
    src/my-source.c
)

# OBS::libobs にリンク
target_link_libraries(my-obs-plugin
    PRIVATE OBS::libobs
)

# C99 を要求
target_compile_features(my-obs-plugin PRIVATE c_std_99)
```

## obs-plugintemplate ベースの標準構成

obs-plugintemplate を使う場合、`cmake/` 配下のヘルパーが利用できる:

```cmake
cmake_minimum_required(VERSION 3.16)
project(my-obs-plugin VERSION 0.1.0)

# OBS ビルドシステムのパスを設定（OBS ソースと一緒にビルドする場合）
set(OBS_CMAKE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
list(APPEND CMAKE_MODULE_PATH "${OBS_CMAKE_PATH}")

# OBS SDK
find_package(libobs REQUIRED)
find_package(obs-frontend-api QUIET)  # UIコンポーネントを使う場合

add_library(my-obs-plugin MODULE)

target_sources(my-obs-plugin PRIVATE
    src/plugin-main.c
    src/my-source.c
)

target_link_libraries(my-obs-plugin
    PRIVATE
    OBS::libobs
)

# OBS::obs-frontend-api が見つかった場合のみリンク
if(TARGET OBS::obs-frontend-api)
    target_link_libraries(my-obs-plugin
        PRIVATE OBS::obs-frontend-api
    )
    target_compile_definitions(my-obs-plugin PRIVATE ENABLE_FRONTEND_API)
endif()

# ロケールファイルのインストール
install(DIRECTORY data/locale
    DESTINATION "${CMAKE_INSTALL_DATAROOTDIR}/obs/obs-plugins/my-obs-plugin"
)

# プラグイン本体のインストール
install(TARGETS my-obs-plugin
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}/obs-plugins"
)
```

## C++ プラグインの場合

```cmake
add_library(my-obs-plugin MODULE
    src/plugin-main.cpp
    src/my-filter.cpp
)

target_link_libraries(my-obs-plugin
    PRIVATE OBS::libobs
)

# C++17 を要求
target_compile_features(my-obs-plugin PRIVATE cxx_std_17)
```

## FetchContent で OBS SDK を取得

ソースが手元にない場合、CMake の FetchContent を使う:

```cmake
include(FetchContent)

FetchContent_Declare(
    libobs
    GIT_REPOSITORY https://github.com/obsproject/obs-studio.git
    GIT_TAG        30.0.0
    SOURCE_SUBDIR  cmake
)
FetchContent_MakeAvailable(libobs)
```

## ビルドコマンド

```bash
# ビルドディレクトリを作成して設定
cmake -B build -DCMAKE_BUILD_TYPE=RelWithDebInfo

# ビルド
cmake --build build --parallel

# インストール
cmake --install build
```

## OBS SDK の検索パスを手動指定

```bash
cmake -B build \
    -Dlibobs_DIR=/path/to/obs-studio/cmake \
    -DCMAKE_BUILD_TYPE=Debug
```
