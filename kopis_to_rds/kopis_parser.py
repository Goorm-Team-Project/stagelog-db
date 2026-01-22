from kopis_extract import get_performance_list
from get_date_range import get_date_range


#공연 ID를 추출하여 list화 시킴
def get_performance_id_list(start_date, end_date):
    raw_data_list = get_performance_list(start_date=start_date, end_date=end_date)
    performance_id_list = []

    try:
        for raw_data in raw_data_list:
            performance_id = raw_data['mt20id']
            performance_id_list.append(performance_id) 
        
    except Exception as e:
        print(f"공연id_list를 가져오는데 실패 : {e}")       


    print(f"kopis_parser : 총 {len(performance_id_list)}개의 공연id를 추출했습니다.")
    return performance_id_list

'''
if __name__ == "__main__":
    
    performance_id_list = get_performance_id_list()
    print(performance_id_list)
    print(f"총 {len(performance_id_list)}개의 ID를 저장했습니다")
'''