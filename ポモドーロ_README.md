
# Discordポモドーロタイマーボット

このDiscordボットは、ユーザーが特定のボイスチャネルに参加すると、ポモドーロタイマーを開始し、休憩や作業のリマインダーを送信するシステムです。ポモドーロセッションの履歴はMySQLデータベースに保存されます。

## 機能
- ユーザーが特定のボイスチャネルに参加すると、ポモドーロタイマーが25分で開始されます。
- 25分後に休憩のリマインダーを送信し、5分後に作業を再開するようにリマインドします。
- ポモドーロタイマーの状態をデータベースに更新します。
- ポモドーロセッションの履歴（時間）をデータベースに保存します。
- ユーザーがボイスチャネルから退出すると、セッションがクリーンアップされます。

## イメージ画面

#### ボイスチャンネルに参加

<img width="241" alt="image" src="https://github.com/user-attachments/assets/2a30e1ff-cecb-43d8-9a97-a7df989019d0" />

#### ボットからのメッセージ
<img width="621" alt="スクリーンショット 2024-12-20 16 29 40" src="https://github.com/user-attachments/assets/80efd4fa-c770-4d50-b171-a01964dcbb9c" />

## 必要条件

- Python 3.7以上
- 必要なライブラリ:
    - `discord.py`
    - `mysql-connector-python`
    - `asyncio`
- MySQLデータベースが必要です。以下のテーブルを作成してください：
    - `Pomodoro`
    - `Pomodoro_history`

## データベース設定

### `Pomodoro` テーブルの作成
```sql
CREATE TABLE Pomodoro (
    username VARCHAR(255) PRIMARY KEY,
    start_at DATETIME,
    status INT
);
```

### `Pomodoro_history` テーブルの作成
```sql
CREATE TABLE Pomodoro_history (
    username VARCHAR(255),
    minutes INT,
    PRIMARY KEY (username, minutes)
);
```

## インストール手順

1. リポジトリをクローンするか、Pythonスクリプトファイルをダウンロードします。
2. 必要なPythonライブラリをインストールします：
    ```bash
    pip install discord mysql-connector-python
    ```
3. `settings.py` ファイルを作成し、以下の定数を設定します：
    ```python
    HOSTNAME = 'your-database-host'
    USERNAME = 'your-database-username'
    PASSWORD = 'your-database-password'
    DBNAME = 'your-database-name'
    TOKEN = 'your-discord-bot-token'
    POMODORO_CH_ID = 
    ```

4. ボットを実行します：
    ```bash
    python3 bot.py
    ```

## 使用方法

- ユーザーが特定のボイスチャネル（ID: `POMODORO_CH_ID`）に参加すると、ボットは25分のポモドーロタイマーを開始し、25分後にリマインダーを送信します。
- 25分後、ボットはユーザーに休憩を取るようリマインダーを送信します。
- 5分後、作業に戻るようリマインダーを送信します。
- ボットは、ポモドーロセッションの開始時間をMySQLデータベースに保存し、`Pomodoro_history`テーブルにセッションの時間を記録します。

## ライセンス

このプロジェクトはオープンソースで、MITライセンスの下で提供されています。
