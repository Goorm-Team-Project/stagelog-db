import requests
import xmltodict
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from get_date_range import get_date_range
load_dotenv()



def get_performance_list(start_date, end_date):    
    # 1. API 요청 경로 (가이드 7페이지 참조)
    url = "http://www.kopis.or.kr/openApi/restful/pblprfr"
    
    # 2. 요청 파라미터 설정
    params = {
        'service': os.getenv('KOPIS_API_KEY'), 
        'stdate': start_date,    # 조회 시작일
        'eddate': end_date,      # 조회 종료일
        'cpage': 1,              # 현재 페이지
        'rows': 100,             # 한 번에 가져올 개수
        'shcate': 'CCCD'         # 장르코드: 대중음악
    }

    cpage = 1
    raw_data_list = [] 

    while(True):
            try:       
                
                # 3. 데이터 가져오기            
                response = requests.get(url, params=params)
                
                # 4. XML을 파이썬 딕셔너리로 변환
                cur_data_dict = xmltodict.parse(response.content)
                
                # 5. 변환된 데이터 list에 합치기
                raw_data_list.extend(cur_data_dict.get('dbs', {}).get('db', []))

                # 6. 한페이지의 데이터 개수 확인
                rows = len(cur_data_dict.get('dbs', {}).get('db', []))
                print(f"{cpage}페이지에서 {rows}개의 데이터를 가져왔습니다")

                if rows == 100:
                    cpage+=1                
                    params['cpage'] = cpage                      

                else:
                    break     
                    
                # 7. 보기 좋게 JSON 형태로 출력해보기
                # print(json.dumps(raw_data_list, indent=4, ensure_ascii=False))
                  
            except Exception as e:
                print(f"kopis_extract 에러 발생: {e}")
    os.environ['last_update'] = end_date
    print(f"kopis_extract : 총 {len(raw_data_list)}개의 데이터를 가져왔습니다.")
    return raw_data_list

'''
if __name__ == "__main__":
    startdate, endate = get_date_range(2)
    get_performance_list(startdate, endate)
    print(f"{os.getenv('last_update')}")
'''

