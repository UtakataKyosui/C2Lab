# Networking Tools

## xh — curl / httpie replacement

**curl / httpie の代替。HTTPie 互換構文、HTTP/2 デフォルト、高速。**

```bash
# インストール
cargo install xh
brew install xh

# 基本使用
xh GET https://api.example.com/users
xh https://api.example.com/users        # GET はデフォルト

# HTTP メソッド
xh POST https://api.example.com/users name=Alice email=alice@example.com
xh PUT https://api.example.com/users/1 name=Bob
xh DELETE https://api.example.com/users/1
xh PATCH https://api.example.com/users/1 active=true

# ヘッダー
xh GET https://api.example.com 'Authorization:Bearer TOKEN'
xh GET https://api.example.com 'X-Custom-Header:value'

# クエリパラメータ
xh GET https://api.example.com/search q==rust limit==10  # == でクエリパラメータ

# JSON (デフォルト)
xh POST https://api.example.com/users name=Alice age:=30  # := で数値/bool
xh POST https://api.example.com/data items:='["a","b"]'   # := でJSON配列

# フォームデータ
xh --form POST https://api.example.com/upload file@image.png

# ファイルダウンロード
xh --output file.json https://api.example.com/data
xh --download https://example.com/file.zip

# 認証
xh -a user:pass https://api.example.com   # Basic Auth
xh --bearer TOKEN https://api.example.com # Bearer Token

# HTTPS
xh --verify=no https://localhost:8443     # SSL検証を無効化

# セッション
xh --session session.json POST https://api.example.com/login user=alice pass=secret
xh --session session.json https://api.example.com/profile  # セッションを再利用

# デバッグ
xh --verbose GET https://api.example.com  # リクエスト/レスポンスを詳細表示
xh --offline GET https://api.example.com  # 実際には送信しない（ドライラン）
```

**curl との比較**:
```bash
# curl
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","age":30}'

# xh（はるかにシンプル）
xh POST https://api.example.com/users name=Alice age:=30
```

---

## miniserve — HTTP server

**`python -m http.server` の代替。ファイルアップロード、認証、TLS、QRコード。**

```bash
# インストール
cargo install miniserve
brew install miniserve

# 基本使用
miniserve .                    # カレントディレクトリをサーブ
miniserve /path/to/dir         # 指定ディレクトリをサーブ
miniserve -p 3000 .            # ポート3000で起動（デフォルト8080）
miniserve -i 0.0.0.0 .         # 全インターフェースでリッスン

# 機能
miniserve --upload-files .     # ファイルアップロードを許可
miniserve --mkdir .            # ディレクトリ作成を許可
miniserve --qrcode .           # QRコードを表示（モバイルアクセス用）
miniserve --enable-tar .       # tar アーカイブダウンロードを有効化
miniserve --enable-zip .       # zip アーカイブダウンロードを有効化

# セキュリティ
miniserve --auth user:password .   # Basic 認証
miniserve --tls-cert cert.pem --tls-key key.pem .  # TLS 有効化

# ファイルフィルタ
miniserve --hidden .           # 隠しファイルを表示
miniserve --no-symlinks .      # シンボリックリンクを非表示

# テーマ
miniserve --theme squirrel .   # テーマ指定（archlinux, squirrel, monokai等）
```

**クイックシェア**:
```bash
# ローカルネットワークでファイルを素早く共有
miniserve --qrcode /path/to/share
# QRコードをスマートフォンで読み取れば即アクセス
```
