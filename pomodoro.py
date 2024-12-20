import discord
from discord.ext import commands
import asyncio
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

from settings import *

hostname = HOSTNAME
username = USERNAME
password = PASSWORD
dbname = DBNAME


def create_connection(hostname, username, password, dbname):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=password,
            database=dbname,
            port=3306,
        )
    except Error as e:
        print("Connection Error :(")
    
    return connection

def execute_param_query(query, params):
    connection = create_connection(hostname, username, password, dbname)
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
    except Error as e:
        print("Execute Error :(")
    finally:
        cursor.close()

def execute_read_query(query, params=None):
    connection = create_connection(hostname, username, password, dbname)
    cursor = connection.cursor()

    result = None
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print("Execute Error :(")
    finally:
        cursor.close()

client = discord.Client(intents=discord.Intents.all())
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

TOKEN = TOKEN

async def pomodoro_sys():
    print("Check Database>>>")
    now = datetime.now()

    th_time = now - timedelta(minutes=25)

    query = """
        SELECT * FROM Pomodoro WHERE start_at < %s;
    """

    params = (th_time, )

    result = execute_read_query(query, params)

    if result != []:
        for user in result:
            userid = user[1]

            if user[-1] == 1:
                target = await client.fetch_user(userid)

                try:
                    await target.send("25分が経過しました。休憩に入りましょう！")
                except Error:
                    pass
            
                print("25")
                query = """
                    UPDATE Pomodoro SET start_at = %s, status=%s WHERE username = %s
                """

                params = (user[-2]+timedelta(minutes=5), 0, userid)

                execute_param_query(query, params)

                query = """
                    INSERT INTO Pomodoro_history(username, minutes) values (%s, %s)
                """
                username = str(await client.fetch_user(int(userid)))
                params = (username, 25)
                execute_param_query(query, params)
            else:
                target = await client.fetch_user(userid)

                try:
                    await target.send("5分が経過しました。作業に戻りましょう！")
                except Error:
                    pass

                print("5")
                now = datetime.now()
                query = """
                    UPDATE Pomodoro SET start_at = %s, status=%s WHERE username = %s
                """

                params = (now, 1, userid)

                execute_param_query(query, params)

@client.event
async def on_ready():
    print()
    print("---------------------------")
    print('ログインしました')
    print("---------------------------")

    while True:
        await pomodoro_sys()
        await asyncio.sleep(60)

@client.event
async def on_voice_state_update(member, before, after):
    # ミュートやカメラの状態が変わっただけなら無視
    if before.channel == after.channel:
        return

    # ユーザーが特定のボイスチャネルに参加したときの処理
    if after.channel is not None and after.channel.id == POMODORO_CH_ID:
        print("Join on VC!")

        target = await client.fetch_user(member.id)

        try:
            await target.send("ポモドーロタイマーを開始しました。25分間集中しましょう！")
        except Error:
            pass    

        query = """
            SELECT * FROM Pomodoro WHERE username = %s
        """

        params = (member.id, )

        result = execute_read_query(query, params)

        if result != []:
            query = """
                UPDATE Pomodoro SET start_at = %s, status=%s WHERE username = %s
            """

            now = datetime.now()
            params = (now, 1, member.id)
            execute_param_query(query, params)
            print("Exists User, Update DB...!")

        else:
            query = """
                INSERT INTO Pomodoro(username) values (%s)
            """

            params = (member.id, )

            execute_param_query(query, params)
            print("Not Exist User, Insert to DB...!")


    # ユーザーが特定のボイスチャネルから退出したときの処理
    if before.channel is not None and before.channel.id == POMODORO_CH_ID:

        query = """
            SELECT * FROM Pomodoro WHERE username = %s
        """
        params = (member.id, )

        result = execute_read_query(query, params)

        if result != []:
            if result[0][-1] == 1:

                seconds = (datetime.now() - result[0][-2]).seconds
                minutes = int(seconds / 60)

                query = """
                    INSERT INTO Pomodoro_history(username, minutes) values (%s, %s)
                """

                username = str(await client.fetch_user(int(member.id)))
                
                params = (username, minutes)

                if minutes > 0:
                    execute_param_query(query, params)

        query = """
            DELETE FROM Pomodoro WHERE username = %s
        """

        params = (member.id, )

        execute_param_query(query, params)

        print("Out of VC...")

        

client.run(TOKEN)

