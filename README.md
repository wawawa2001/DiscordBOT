# PomodoroBOT
このプロジェクトは、Flaskを使用したWebアプリケーションとDiscord Botを組み合わせたポモドーロタイマーシステムです。以下に、アプリケーションの概要、設定方法、および使用手順を説明します。

---

## 主な機能

### 1. Webアプリケーション
- `Flask` を利用したシンプルなウェブインターフェース。
- ポモドーロ履歴 (`Pomodoro_history`) と進行中のポモドーロタスク (`Pomodoro`) の表示。
- ユーザーやタスクの削除機能。
- 合計作業時間の集計と表示。

### 2. Discord Bot
- 指定されたボイスチャネルに参加したユーザーにポモドーロタイマーを自動的に開始。
- タイマーの進行に応じて、集中時間と休憩時間をDiscord DMで通知。
- チャネル退出時に作業時間を記録。

---

## 動作イメージ

### VCチャンネルに入る
![スクリーンショット 2024-12-20 172449](https://github.com/user-attachments/assets/b8873c6a-c0b0-4f30-9ad7-cc909afa35a7)

### タイマー開始メッセージがDMで届く
![スクリーンショット 2024-12-20 172521](https://github.com/user-attachments/assets/adaedb07-3fae-4cf7-bf32-df1d5e545df4)

### 休憩と開始時間をDMで知らせてくれる。（集中時間と休憩時間はsettings.pyで変更可能）
<img width="839" alt="image" src="https://github.com/user-attachments/assets/cb660798-ad52-4d02-8dec-c5ba844456e9" />

### トータル利用時間
![スクリーンショット 2024-12-20 215126](https://github.com/user-attachments/assets/c88cf3f6-72c4-4e0f-bcbb-32f0cb535793)

### 現在の入室者
![スクリーンショット 2024-12-20 215202](https://github.com/user-attachments/assets/cf64a15f-48b6-4385-8a3d-534dc2342d55)

### 入室ログ
![スクリーンショット 2024-12-20 215240](https://github.com/user-attachments/assets/1c677319-cc30-440d-9d28-887c159309cc)



## 必要な環境

1. **Python 3.8以降**
2. **ライブラリ**
   - Flask
   - discord.py
   - mysql-connector-python

3. **MySQLデータベース**

4. **設定ファイル**
   - `settings.py` ファイルで以下の情報を定義:
     ```python
     HOSTNAME = "ホスト名"
     USERNAME = "ユーザー名"
     PASSWORD = "パスワード"
     DBNAME = "データベース名"
     TOKEN = "Discord Botのトークン"
     POMODORO_CH_ID = 123456789012345678  # 対象のボイスチャネルID
     ```

---

## データベース構成

### テーブル1: `Pomodoro`
| カラム名      | データ型       | 説明                       |
|---------------|----------------|----------------------------|
| id            | int            | NOT NULL, AUTO_INCREMENT   |
| username      | VARCHAR(255)   | DiscordのユーザーID       |
| start_at      | DATETIME       | タイマーの開始時刻        |
| status        | TINYINT        | 状態 (1: 作業中, 0: 休憩中) |

### テーブル2: `Pomodoro_history`
| カラム名      | データ型       | 説明                       |
|---------------|----------------|----------------------------|
| id            | int            | NOT NULL, AUTO_INCREMENT   |
| username      | VARCHAR(255)   | DiscordのユーザーID       |
| minutes       | INT            | 作業時間 (分)             |

---

## セットアップ手順

1. 必要なライブラリをインストール:
   ```bash
   pip install -r requirements.txt
   ```

2. データベースをセットアップ:
   - MySQLにログインし、必要なテーブルを作成:
     ```sql
     CREATE TABLE Pomodoro (
         id INT AUTO_INCREMENT PRIMARY KEY,
         username VARCHAR(255) NOT NULL,
         start_at DATETIME NOT NULL,
         status TINYINT NOT NULL
     );

     CREATE TABLE Pomodoro_history (
         username VARCHAR(255) NOT NULL,
         minutes INT NOT NULL
     );
     ```

3. `settings.py` ファイルを作成し、環境変数を設定。

4. アプリケーションを起動:
   - Flaskサーバー:
     ```bash
     python pomodoro.py
     ```
   - Discord Bot:
     ```bash
     python3 server.py
     ```

---

## 使用方法

### Webアプリケーション
1. ブラウザで `/home` にアクセス。
2. `Pomodoro_history` で過去の作業履歴を確認。
3. `Pomodoro_process` で進行中のタスクを確認。
4. 必要に応じてタスクや履歴を削除。
5. `Pomodoro_total_time` でユーザーごとの合計作業時間を表示。

### Discord Bot
1. 対象のボイスチャネルに参加すると、タイマーが自動的に開始されます。
2. 25分経過すると通知が送信され、5分の休憩が開始されます。
3. チャネル退出時には作業時間が記録されます。

---

## 注意事項
- WebアプリケーションとDiscord Botは同じデータベースを共有しています。
- タイマーの進行は1分単位で監視されます。
- データベース接続に問題がある場合は、エラーがコンソールに出力されます。

---

