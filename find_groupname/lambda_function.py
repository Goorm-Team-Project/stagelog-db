import json
from fetch_group_info import fetch_groupname_info, get_connection

def lambda_handler(event, context):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        sql_fetch = """
            SELECT kopis_id, title, artist
            FROM events
            WHERE group_name IS NULL
            AND artist LIKE '%,%'
            LIMIT 100
        """
        cursor.execute(sql_fetch)
        rows = cursor.fetchall()
        
        if not rows:
            return {'statusCode': 200, 'body': '그룹명을 찾을 대상 공연이 없습니다.'}
        
        print(f"총 {len(rows)}개의 복수 출연진 공연 분석 시작...")
        
        batch_size = 10 
        update_count = 0
        
        for i in range(0, len(rows), batch_size):
            batch_rows = rows[i:i + batch_size]
            
            # GPT에 보낼 리스트 가공 (인덱스를 키로 사용하기 위해)
            group_input_list = []
            
            for row in batch_rows:
                group_input_list.append({
                    'title': row['title'],
                    'artist': row['artist']
                })
            
            print(f"Batch Processing {i} ~ {i+len(batch_rows)}...")
            
            ai_results = fetch_groupname_info(group_input_list)
            
            print(f"--- AI 응답 결과: {ai_results} ---")
            
            for idx_str, group_name in ai_results.items():
                try:
                    idx = int(idx_str)
                    
                    # 인덱스 범위 체크 (AI가 없는 번호를 뱉을 수도 있으므로)
                    if 0 <= idx < len(batch_rows):                    
                        target_event = batch_rows[idx]
                        
                        if group_name:
                            print(f"✅ 아이돌 그룹 식별 : {target_event['title']} ->  {group_name}")
                            cursor.execute(
                                "UPDATE events SET group_name = %s WHERE kopis_id = %s",
                                (group_name, target_event['kopis_id'])
                            )
                            update_count += 1
                        else:
                            # 그룹이 아닌 경우 계속 NULL로 두면 다음에 또 조회하므로,
                            # NONE 같은 값으로 마킹
                            # 다음 실행 때 WHERE group_name IS NULL 조건에서 빠질 수 있도록
                            cursor.execute(
                                "UPDATE events SET group_name = 'NONE' WHERE kopis_id = %s",
                                (target_event['kopis_id'])
                            )
                except ValueError:
                    continue # 키가 숫자가 아니면 패스
        conn.commit()
        print(f"분석 완료: {len(rows)}건, 그룹 매핑 성공 : {update_count}건")
        
    except Exception as e:
        conn.rollback()
        print(f"Error : {e}")
        return {'statusCode': 500, 'body': str(e)}
    
    finally:
        conn.close()
        
        

if __name__ == "__main__":
    lambda_handler(None, None)