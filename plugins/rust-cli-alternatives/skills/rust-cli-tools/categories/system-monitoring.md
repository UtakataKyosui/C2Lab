# System Monitoring Tools

## bottom (btm) — top / htop replacement

**top / htop の代替。カスタマイズ可能なTUIウィジェット、CPU/メモリ/ネットワーク/ディスク/温度/プロセス。**

```bash
# インストール
cargo install bottom           # コマンド名は btm
brew install bottom

# 起動
btm                            # デフォルト表示
btm --battery                  # バッテリー情報を表示
btm --celsius                  # 温度を摂氏で表示
btm --rate 500                 # 更新レート500ms（デフォルト1000ms）
```

**主なキーバインド**:
| キー | 動作 |
|------|------|
| `q` / `Ctrl+C` | 終了 |
| `?` | ヘルプ表示 |
| `/` | プロセス検索 |
| `dd` | 選択プロセスを終了 |
| `e` | CPU ウィジェットを展開 |
| `t` | ツリービューに切り替え |
| `m` | プロセスを PID/CPU/MEM でソート |
| `Tab` | ウィジェット間を移動 |

**設定ファイル**: `~/.config/bottom/bottom.toml`
```toml
[flags]
rate = 1000            # 更新間隔（ms）
temperature_type = "celsius"
default_widget_type = "proc"

[colors]
table_header_color = "LightBlue"
widget_title_color = "Gray"
```

---

## procs — ps replacement

**ps の代替。カラー出力、ツリービュー、ポート表示。**

```bash
# インストール
cargo install procs
brew install procs

# 基本使用
procs                          # 全プロセス一覧
procs nginx                    # キーワードで検索
procs --tree                   # プロセスツリー表示
procs --watch                  # リアルタイム更新（1秒間隔）
procs --watch-interval 2       # 2秒間隔で更新

# ソート
procs --sortd cpu              # CPU使用率でソート（降順）
procs --sorta pid              # PIDでソート（昇順）

# 表示カラム
procs --insert tcp             # TCPポートカラムを追加
procs --insert udp             # UDPポートカラムを追加
```

**設定ファイル**: `~/.config/procs/config.toml`
```toml
[[columns]]
kind = "Pid"
style = "BrightYellow"

[[columns]]
kind = "Username"

[[columns]]
kind = "Separator"

[[columns]]
kind = "CpuTime"
style = "BrightGreen"
```

---

## dust — du replacement

**du の代替。視覚的なバーチャート、サイズ順ソート済み。**

```bash
# インストール
cargo install du-dust          # コマンド名は dust
brew install dust

# 基本使用
dust                           # カレントディレクトリの使用量
dust /path                     # 指定ディレクトリ
dust -d 1                      # 深さ1まで表示
dust -d 2                      # 深さ2まで表示
dust -f                        # ファイルも表示（ディレクトリのみでなく）
dust -r                        # 逆順（小さいものが先）
dust -n 10                     # 上位10エントリのみ
dust -b                        # バーチャートなし（シンプルな数値のみ）
dust -x                        # 同一マウントポイント内のみ（他のfsを跨がない）

# 比較
du -sh * | sort -rh            →  dust -d 1
du -ah --max-depth=2           →  dust -d 2 -f
ncdu                           →  dust              # ncduより高速
```

---

## bandwhich — network monitoring

**プロセス別ネットワーク帯域幅モニタリング。**

```bash
# インストール
cargo install bandwhich
brew install bandwhich

# 基本使用（root権限が必要）
sudo bandwhich                 # インタラクティブ表示
bandwhich --raw                # 非インタラクティブ出力

# インターフェース指定
sudo bandwhich --interface eth0

# 解決を無効化（高速化）
sudo bandwhich --no-resolve
```

**表示内容**:
- **Processes**: プロセス別の送受信速度
- **Connections**: 接続別の送受信速度
- **Remote Addresses**: リモートホスト別の使用量

**注意**: macOS ではシステム権限が必要な場合があります。`sudo bandwhich` で実行。
