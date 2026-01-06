import requests
import xmltodict
import json
from kopis_parser import get_performance_id_list


#공연 세부정보 API조회
def get_performance_detail(performance_id):
    
    url = f'http://www.kopis.or.kr/openApi/restful/pblprfr/{performance_id}'

    params = {'service':'630bccf5f992490981fad0df69483aa1'

    }

    try:
        #api 요청
        response = requests.get(url, params=params)
        #데이터 파싱
        data_dict = xmltodict.parse(response.content)
        #데이터 추출
        detail = data_dict.get('dbs', {}).get('db', [])        

    except Exception as e:
        print(f"상세조회 에러 {e}" )
        
    return detail
    
#공연 세부정보 리스트화
def get_performance_detail_list():
    performance_id_list = get_performance_id_list()
    performance_detail_list = []

    try:
        for performance_id in performance_id_list:
            performance_detail_list.append(get_performance_detail(performance_id))
        
    except Exception as e:
        print(f"세부사항 리스트를 얻어오는데 실패{e}")

    print(f"kopis_detail 총 {len(performance_detail_list)}개의 공연 세부사항을 가져옴")    
    return performance_detail_list


        

if __name__ == "__main__":
    detail_list = get_performance_detail_list()
    print(json.dumps(detail_list, indent=4, ensure_ascii=False))
        

