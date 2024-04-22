import datetime
import asyncio
import configparser

import aiomysql

config = configparser.ConfigParser()
config.read('config.ini')

host = config['MySQL']['host']
user = config['MySQL']['user']
password = config['MySQL']['password']
database = config['MySQL']['database']

loop = asyncio.get_event_loop()

class DBHandler:
    def __init__(self, table_name: str, column1: str, column2: str, default_value, key):
        self.table_name = table_name
        self.column1 = column1
        self.column2 = column2
        self.default_value = default_value
        self.key = key
    
    @classmethod
    async def create_connection(cls):
        connection = await aiomysql.connect(host=host, user=user, password=password, db=database, loop=loop, autocommit=True)
        return connection
    
    async def get_data(self):
        try:
            connection = await self.create_connection()
        except:
            return self.default_value
        
        try:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SELECT {self.column2} "
                                     f"FROM {self.table_name} "
                                     f"WHERE {self.column1} = {self.key}")
                result = await cursor.fetchone()
                connection.close()

                if result is None:
                    return self.default_value
                
                return result[0]
        except:
            connection.close()
            return self.default_value
        
    async def update_data(self, value):
        connection = await self.create_connection()
        async with connection.cursor() as cursor:
            create_sql = f"INSERT INTO {self.table_name} ({self.column1}, {self.column2}) " \
                         "VALUES (%s, %s) " \
                         f"ON DUPLICATE KEY UPDATE {self.column1}=%s, {self.column2}=%s"
            
            await cursor.execute(create_sql, (self.key, value, self.key, value))
            connection.close()

    async def delete_data(self):
        connection = await self.create_connection()
        async with connection.cursor() as cursor:
            delete_sql = f"DELETE FROM {self.table_name} WHERE {self.column1}=%s"
            await cursor.execute(delete_sql, self.key)
            connection.close() 

class ServerSetTranslation(DBHandler):
    def __init__(self, server_id: int):
        super().__init__(
            table_name=config['MySQL']['server_translations_table_name'],
            column1='server_id',
            column2='translation',
            default_value='en.sahih',
            key=server_id
        )

    async def save(self, translation):
        return await self.update_data(translation)
    
    async def load(self) -> str:
        return await self.get_data()
    
class DailyQuranTime(DBHandler):
    def __init__(self, server_id: int):
        super().__init__(
            table_name=config['MySQL']['server_time_table_name'],
            column1='server_id',
            column2='time',
            default_value='',
            key=server_id
        )

    async def save(self, time):
        return await self.update_data(time)

    async def load(self) -> str:
        return await self.get_data()
    
class DailyQuranChannel(DBHandler):
    def __init__(self, server_id: int):
        super().__init__(
            table_name=config['MySQL']['server_channel_table_name'],
            column1='server_id',
            column2='channel',
            default_value='',
            key=server_id
        )

    async def load(self) -> str:
        return await self.get_data()

    async def save(self, channel):
        return await self.update_data(channel)

    async def delete(self):
        return await self.delete_data()


