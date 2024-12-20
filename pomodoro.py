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
        print(f"Execute Error :( {e}")
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
        print(f"Execute Read Error :( {e}")
    finally:
        cursor.close()

client = discord.Client(intents=discord.Intents.all())
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

TOKEN = TOKEN

async def pomodoro_sys():
    print("Check Database>>>")
    now = datetime.now()

    th_time = now - timedelta(minutes=FOCUS_TIME)

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
                    await target.send(f"{FOCUS_TIME}蛻�′邨碁℃縺励∪縺励◆縲ゆｼ第�縺ｫ蜈･繧翫∪縺励ｇ縺�ｼ�")
                except Exception as e:
                    print(f"Error sending message to user {userid}: {e}")
            
                query = """
                    UPDATE Pomodoro SET start_at = %s, status=%s WHERE username = %s
                """

                params = (user[-2]+timedelta(minutes=BREAK_TIME), 0, userid)

                execute_param_query(query, params)

                query = """
                    INSERT INTO Pomodoro_history(username, minutes) values (%s, %s)
                """
                username = str(await client.fetch_user(int(userid)))
                params = (username, FOCUS_TIME)
                execute_param_query(query, params)
            else:
                target = await client.fetch_user(userid)

                try:
                    await target.send(f"{BREAK_TIME}蛻�′邨碁℃縺励∪縺励◆縲ゆｽ懈･ｭ縺ｫ謌ｻ繧翫∪縺励ｇ縺�ｼ�")
                except Error:
                    pass

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
    print('繝ｭ繧ｰ繧､繝ｳ縺励∪縺励◆')
    print("---------------------------")

    while True:
        await pomodoro_sys()
        await asyncio.sleep(60)

@client.event
async def on_voice_state_update(member, before, after):
    # 繝溘Η繝ｼ繝医ｄ繧ｫ繝｡繝ｩ縺ｮ迥ｶ諷九′螟峨ｏ縺｣縺溘□縺代↑繧臥┌隕�
    if before.channel == after.channel:
        return

    # 繝ｦ繝ｼ繧ｶ繝ｼ縺檎音螳壹�繝懊う繧ｹ繝√Ε繝阪Ν縺ｫ蜿ょ刈縺励◆縺ｨ縺阪�蜃ｦ逅�
    if after.channel is not None and after.channel.id == POMODORO_CH_ID:
        print("Join on VC!")

        target = await client.fetch_user(member.id)

        try:
            await target.send(f"繝昴Δ繝峨�繝ｭ繧ｿ繧､繝槭�繧帝幕蟋九＠縺ｾ縺励◆縲�{FOCUS_TIME}蛻�俣髮�ｸｭ縺励∪縺励ｇ縺�ｼ�")
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
                INSERT INTO Pomodoro(username, start_at, status) values (%s, %s, %s)
            """

            params = (member.id, datetime.now(), 1, )

            execute_param_query(query, params)
            print("Not Exist User, Insert to DB...!")


    # 繝ｦ繝ｼ繧ｶ繝ｼ縺檎音螳壹�繝懊う繧ｹ繝√Ε繝阪Ν縺九ｉ騾蜃ｺ縺励◆縺ｨ縺阪�蜃ｦ逅�
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

