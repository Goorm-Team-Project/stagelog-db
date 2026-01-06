import pymysql
from kopis_transform import transform_event_data


# --- [SQL 템플릿 정의] ---
# SQL: 중복된 kopis_id가 있으면 업데이트(Upsert)
UPSERT_EVENT_SQL = """
            INSERT INTO events (
                kopis_id, title, start_date, end_date, venue, 
                time, age, price, host, relate_url, 
                update_date, poster, artist
            ) VALUES (
                %(kopis_id)s, %(title)s, %(start_date)s, %(end_date)s, %(venue)s, 
                %(time)s, %(age)s, %(price)s, %(host)s, %(relate_url)s, 
                %(update_date)s, %(poster)s, %(artist)s
            )
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                end_date = VALUES(end_date),
                venue = VALUES(venue),
                time = VALUES(time),
                age = VALUES(age),
                price = VALUES(price),
                host = VALUES(host),
                relate_url = VALUES(relate_url),
                update_date = VALUES(update_date),
                poster = VALUES(poster),
                artist = VALUES(artist)
"""

# --- [DB 설정 정보] ---

#'cursorclass'
#DB엔진이 반환하는 행 데이터를 어떤 자료형으로 매핑할지 결정하는 옵션
#기본값은 튜플, 튜플 사용시 데이터에 튜플[0] 처럼 인덱스 번호로 접근해야해서 원하는 키 값에 접근하는데 어려움이 있음.
#딕셔너리 타입으로 바꿔줌으로써 딕셔너리['key'] 방식으로 원하는 값에 접근하기 편함.

#'charset'
#컴퓨터는 숫자로만 대화. 그래서 '공연'이라는 글자를 저장할 때, 특정 숫자와 매칭시키는 약속이 필요한데 그것이 charset(문자집합)
#utf8(3바이트): 기본적인 한글, 영어는 지원하지만 이모지를 저장하면 에러가 나거나 데이터 잘림
#utf8mb4(4바이트): utf-8의 확장판, 한글과 이모지까지 완벽하게 저장 가능

DB_CONFIG = {
    'host': 'localhost',        # MariaDB 주소
    'user': 'root',             # 사용자 이름
    'password': '1111',         # 비밀번호
    'db': 'stagelog',           # 데이터베이스 이름
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor 
}            

#정제된 transform_list를 MariaDB에 INSERT/UPDATE 합니다.
def load_to_mariadb(data_list):

    if not data_list:
        print("저장할 데이터가 없습니다.")
        return

    # DB 연결
    conn = pymysql.connect(**DB_CONFIG)
    
    try:
        with conn.cursor() as cursor:
                     
            # 대량 저장 실행
            cursor.executemany(UPSERT_EVENT_SQL, data_list)
            
        conn.commit()
        print(f"MariaDB 저장 완료: 총 {len(data_list)}건 반영되었습니다.")

    except Exception as e:
        print(f"MariaDB 저장 중 에러 발생: {e}")
        conn.rollback()
    
    finally:
        conn.close()

# --- [실행부] ---
if __name__ == "__main__":
    # 1. 데이터 변환 실행
    final_data = transform_event_data()
    
    # 2. MariaDB 저장 실행
    if final_data:
        load_to_mariadb(final_data)