from kopis_detail import get_performance_detail_list
import json

#매핑표에 따라 API 데이터를 DB 필드용으로 변환
def transform_event_data(start_date, end_date):
    performance_detail_list = get_performance_detail_list(start_date, end_date)
    transform_list = []
    try:
        for performence_detail in performance_detail_list:
            if(performence_detail):  
            
                transform_list.append({'kopis_id':performence_detail.get('mt20id'),
                    'title': performence_detail.get('prfnm'),
                    'start_date': performence_detail.get('prfpdfrom','').replace('.','-'),
                    'end_date': performence_detail.get('prfpdto','').replace('.','-'),
                    'venue': performence_detail.get('fcltynm',),
                    'time': performence_detail.get('dtguidance'),
                    'age': performence_detail.get('prfage'),
                    'price': performence_detail.get('pcseguidance'),
                    'host': performence_detail.get('entrpsnmH') if performence_detail.get('entrpsnmH') else '정보 없음',
                    'relate_url': check_list_or_dict(performence_detail.get('relates', {}).get('relate')),
                    'update_date': performence_detail.get('updatedate')[:19], # 년월일 시간분초까지 슬라이싱
                    'poster': performence_detail.get('poster'),
                    'artist': performence_detail.get('prfcast')if performence_detail.get('prfcast') else '정보 없음',
                    'genre': '대중음악'
                    })   
        
        # print(json.dumps(transform_list, indent=4, ensure_ascii=False))
        print(f"kopis_transform : 총 {len(transform_list)}개의 데이터를 DB 필드용으로 변환했습니다.")
        return transform_list
    
    except Exception as e:
        print(f"DB필드용으로 데이터 변환 실패 : {e}")
        return []

def check_list_or_dict(relate_data):
    if isinstance(relate_data, list) and relate_data:
        return relate_data[0].get('relateurl', '')if relate_data else ''
    elif isinstance(relate_data, dict):
         return relate_data.get('relateurl','') 
    return ''

'''
if __name__ == "__main__":
    transform_event_data()
'''