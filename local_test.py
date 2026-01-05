from database import DatabaseManager
from test_data import test_events

def test_db_insertion():
    db = DatabaseManager()
    
    print("데이터 삽입 시도")
    db.upsert_events(test_events)

    
if __name__ == "__main__":
    test_db_insertion()