from datetime import datetime
from dateutil.relativedelta import relativedelta
 
# KOPIS API로 가져올 공연 데이터의 기간 범위를 정하는 함수 (수집일로부터 n개월 뒤)

def get_date_range(): 
        today = datetime.now()
        months = 2 # 이 값으로 n개월 정의
        n_months_later = today + relativedelta(months=months)
        
        return today.strftime('%Y%m%d'), n_months_later.strftime('%Y%m%d')