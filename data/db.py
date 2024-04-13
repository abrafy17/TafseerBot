import datetime
from config.config import get_mysql_connection
    

class DB():
    def __init__(self) -> None:
        self.db_connection = get_mysql_connection()
        self.cursor = self.db_connection.cursor()

    def save_translation_to_db(self, server_id: int, translation_key: str):
        cursor = self.db_connection.cursor()
        sql = "REPLACE INTO translations (server_id, translation_key) VALUES (%s, %s)"
        val = (server_id, translation_key)
        cursor.execute(sql, val)
        self.db_connection.commit()
        cursor.close()

    def load_translation_from_db(self, server_id: int):
        cursor = self.db_connection.cursor()
        sql = "SELECT translation_key FROM translations WHERE server_id = %s"
        val = (server_id,)
        cursor.execute(sql, val)
        result = cursor.fetchone()
        cursor.close()
        if result is not None:
            return result[0]
        else:
            return None
        
    def save_time_to_db(self, server_id: int, set_time: datetime.time):
        cursor = self.db_connection.cursor()
        sql = "REPLACE INTO time (server_id, set_time) VALUES (%s, %s)"
        val = (server_id, set_time)
        cursor.execute(sql, val)
        self.db_connection.commit()
        cursor.close()

    def load_time_from_db(self, server_id: int):
        cursor = self.db_connection.cursor()
        sql = "SELECT set_time FROM time WHERE server_id = %s"
        val = (server_id,)
        cursor.execute(sql, val)
        result = cursor.fetchone()
        cursor.close()
        if result is not None:
            return result[0]
        else:
            return None
        
    def save_quran_channel_to_db(self, server_id: int, quran_channel: int):
        cursor = self.db_connection.cursor()
        sql = "REPLACE INTO channel (server_id, quran_channel) VALUES (%s, %s)"
        val = (server_id, quran_channel)
        cursor.execute(sql, val)
        self.db_connection.commit()
        cursor.close()

    def drop_quran_channel_from_db(self, server_id: int):
        cursor = self.db_connection.cursor()
        sql = "UPDATE channel SET quran_channel = NULL WHERE server_id = %s"
        val = (server_id,)
        cursor.execute(sql, val)
        self.db_connection.commit()
        cursor.close()


    def load_quran_channel_from_db(self, server_id: int):
        cursor = self.db_connection.cursor()
        sql = "SELECT quran_channel FROM channel WHERE server_id = %s"
        val = (server_id,)
        cursor.execute(sql, val)
        result = cursor.fetchone()
        cursor.close()
        if result is not None:
            return result[0]
        else:
            return None
        
    def save_last_sent_time_to_db(self, server_id: int, last_sent_date: datetime.datetime):
        cursor = self.db_connection.cursor()
        sql = "REPLACE INTO lastsent(server_id, last_sent_date) VALUES (%s, %s)"
        val = (server_id, last_sent_date)
        cursor.execute(sql, val)
        self.db_connection.commit()
        cursor.close()

    def load_last_sent_time_from_db(self, server_id: int):
        cursor = self.db_connection.cursor()
        sql = "SELECT last_sent_date FROM lastsent WHERE server_id = %s"
        val = (server_id,)
        cursor.execute(sql, val)
        result = cursor.fetchone()
        cursor.close()
        if result is not None:
            return result[0]
        else:
            return None