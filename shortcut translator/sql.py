import datetime
import sqlite3


class DataBase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.database_connection = None
        self.cursor = None

    def connect(self):
        self.database_connection = sqlite3.connect(self.db_name)
        self.cursor = self.database_connection.cursor()

    def create_table_if_not_exists(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS data (
                id integer PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL UNIQUE ON CONFLICT IGNORE,
                translation VARCHAR(255),
                time_created DATETIME,
                tag VARCHAR(255)
            )
            """
        )

    def disconnect(self):
        self.cursor.close()

    def query_save(self, name, translation):
        self.cursor.execute(
            """
            INSERT INTO data (name, translation, time_created) VALUES(?, ?, ?)
            """,
            (name, translation, datetime.datetime.now())
        )
        self.database_connection.commit()

    def check_word(self, name):
        self.cursor.execute(
            "SELECT translation FROM data WHERE name=?",
            (name,)
        )
        result = self.cursor.fetchone()
        if result:
            result = result[0]
        return result


if __name__ == "__main__":
    db = DataBase("s_translator.db")
    db.connect()
    db.create_table_if_not_exists()
    db.disconnect()
