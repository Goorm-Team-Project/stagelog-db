import pymysql
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_ROOT_PASSWORD')
        self.db = os.getenv('DB_NAME')
        
    def get_connection(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        return pymysql.connect(
            host=self.host,
            password=self.password,
            user=self.user,
            db=self.db,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            ssl=ssl_context
        )
        
    def upsert_events(self, events_list):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                INSERT INTO events 
                (
                    kopis_id, title, artist, start_date, end_date, 
                    venue, age, poster, time, price, 
                    update_date, relate_url, host, genre
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                ON DUPLICATE KEY UPDATE
                    title       = VALUES(title),
                    artist      = VALUES(artist),
                    start_date  = VALUES(start_date),
                    end_date    = VALUES(end_date),
                    venue       = VALUES(venue),
                    age         = VALUES(age),
                    poster      = VALUES(poster),
                    time        = VALUES(time),
                    price       = VALUES(price),
                    update_date = VALUES(update_date),
                    relate_url  = VALUES(relate_url),
                    host        = VALUES(host),
                    genre       = VALUES(genre);
                """
        
                values = [
                    (
                    event['kopis_id'],
                    event['title'],
                    event['artist'],
                    event['start_date'],
                    event['end_date'],
                    event['venue'],
                    event['age'],
                    event['poster'],
                    event['time'],
                    event['price'],
                    event['update_date'],
                    event['relate_url'],
                    event['host'],
                    event['genre']
                    )
                    for event in events_list
                ]

                cursor.executemany(sql, values)
            
            conn.commit()
            print(f"로그 : {len(events_list)}건의 데이터 동기화 완료.")
        except Exception as e:
            conn.rollback()
            print(f"에러 : 데이터 저장 실패 - {e}")
        finally:
            conn.close()