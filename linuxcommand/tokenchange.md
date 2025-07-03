## Bot設定ファイル Token／Password更新作業手順書（改訂版）

> **対象サービス**
> small-bots／small-service／codras ほか、Excel 管理表に記載のすべての Bot

---

### 0. 事前準備

| 前提条件                                      | 確認内容                                            |
| ----------------------------------------- | ----------------------------------------------- |
| 新 Token／Password が **作業ウィンドウ内で切替可能** か    | 運用・開発・利用者の連絡体制を確立し、切替タイミングを合意済みであること            |
| **Bot 名・systemd ユニット名・設定ファイル絶対パス** が一覧化済み | Excel の管理台帳（small-bots、small-service、codras）で確認 |

---

#### 0.1 バックアップと取得

1. **サーバー側バックアップ**
   *例：仮パス `/path/to/config/config.yaml`*

   ```bash
   sudo cp -p /path/to/config/config.yaml /path/to/config/config.yaml_bk
   ```

2. **ローカル取得**

   * `scp` あるいは VS Code Remote-SSH でダウンロード
   * 文字コード UTF-8／改行コード LF を確認

---

### 1. 作業ウィンドウ開始：サービス停止

```bash
sudo systemctl stop <bot>.service
```

> 停止対象は **1 サービスずつ**。
> 依存関係がある場合は停止順序を Excel 台帳で要確認。

---

### 2. ローカル編集：Token／Password 置換

| 手法   | ツール                 | 留意点                          |
| ---- | ------------------- | ---------------------------- |
| 一括置換 | VS Code 検索＆置換（正規表現） | YAML インデントを保持、`:` の後ろに半角スペース |

> 編集後は `sha256sum` で旧ファイルとハッシュ比較し、差分を可視化。

---

### 3. 設定ファイルアップロード＆整合性確認

*例：仮パス `/path/to/config/config.yaml`*

```bash
# パーミッション調整（必要時）
sudo chmod 664 /path/to/config/config.yaml

# 差分確認
diff -u /path/to/config/config.yaml_bk /path/to/config/config.yaml
```

> 差分が意図通りであることを **画面共有またはスクリーンショット** でダブルチェック。

---

### 4. サービス再起動

```bash
sudo systemctl restart <bot>.service
sudo systemctl status  <bot>.service
```

リアルタイムログ監視：

```bash
journalctl -u <bot>.service -n 100 -f
```

---

### 5. 検証チェックリスト

| チェック項目     | 手順                                            | 合格基準               |
| ---------- | --------------------------------------------- | ------------------ |
| プロセス起動     | `systemctl status`                            | `active (running)` |
| 認証エラーなし    | `journalctl -u <bot>.service \| grep -i auth` | エラー 0 行            |
| エンドツーエンド動作 | Bot を実行し通知／処理を確認                              | 期待レスポンス            |
| 旧 Token 失効 | 旧 Token で API 呼び→ HTTP 401/403                | 401 または 403        |

---

### 6. 完了報告

1. **運用チャネルへ報告**

   * 実施日時・担当者・対象ホスト／サービス
   * 検証結果（チェックリスト添付）
2. **管理台帳更新**

   * 「完了」ステータス
   * 新 Token 末尾 4 文字（識別用）

---

### 7. ロールバック手順（参考）

1. バックアップファイルを戻す

   ```bash
   sudo cp -p /path/to/config/config.yaml_bk /path/to/config/config.yaml
   ```
2. `systemctl restart <bot>.service`
3. 検証チェックリストを再実施し、正常復旧を確認

---

\* 本手順書は ITIL Change Management の軽微変更（Standard Change）に該当。事前承認済みでも、**実行後の検証と記録** は必須とする。
