import requests
import xmltodict
import json
import os
from kopis_parser import get_performance_id_list
from dotenv import load_dotenv

load_dotenv()

#공연 세부정보 API조회
def get_performance_detail(performance_id):
    url = f'http://www.kopis.or.kr/openApi/restful/pblprfr/{performance_id}'
    params = {
        'service': os.getenv('KOPIS_API_KEY')
    }

    try:
        #api 요청
        response = requests.get(url, params=params)
        #데이터 파싱
        data_dict = xmltodict.parse(response.content)
        #데이터 추출
        detail = data_dict.get('dbs', {}).get('db', [])        

    except Exception as e:
        print(f"상세조회 에러 {e}")
        return None
        
    return detail
    
#공연 세부정보 리스트화
def get_performance_detail_list(start_date, end_date):
    performance_id_list = get_performance_id_list(start_date, end_date)
    performance_detail_list = []

    try:
        for performance_id in performance_id_list:
            detail = get_performance_detail(performance_id)
            if detail:
               performance_detail_list.append(detail)
            
        
    except Exception as e:
        print(f"세부사항 리스트를 얻어오는데 실패 : {e}")

    print(f"kopis_detail : 총 {len(performance_detail_list)}개의 공연 세부사항을 가져왔습니다.")    
    return performance_detail_list


        
'''
if __name__ == "__main__":
    detail_list = get_performance_detail_list()
    print(json.dumps(detail_list, indent=4, ensure_ascii=False))
'''