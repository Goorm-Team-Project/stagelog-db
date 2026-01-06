import requests
import xmltodict
import os
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

load_dotenv()

class KopisDataCollector:
    def __init__(self):
        self.apikey = os.getenv('KOPIS_API_KEY')
        self.list_url = "http://www.kopis.or.kr/openApi/restful/pblprfr"
        self.detail_url = "http://www.kopis.or.kr/openApi/restful/pblprfr/"
        

    def get_date_range(self): # 공연 수집 범위 계산 (수집일로부터 n개월 뒤)
        today = datetime.now()
        months = 1
        n_months_later = today + relativedelta(months=months)
        
        print(f"수집 기간 : {today} ~ {n_months_later} | {months}개월")
        
        return today.strftime('%Y%m%d'), n_months_later.strftime('%Y%m%d')

        
    def fetch_event_list(self, start_date, end_date):
        all_events = []
        cpage = 1
        
        while True:
            params = {
                "service": self.apikey,
                "stdate": start_date,
                "eddate": end_date,
                "cpage": cpage,
                "rows": 100,
                "shcate": 'CCCD'
            }
            
            print(f"페이지 {cpage} 수집 중 ...")
            response = requests.get(self.list_url, params=params)
            time.sleep(0.15)
            data = xmltodict.parse(response.content)
            
            dbs = data.get('dbs')
            if dbs is None:
                items = []
            else:
                items = dbs.get('db', [])
            
            event_list = [items] if isinstance(items, dict) else items
            
            if not event_list:
                break
            
            all_events.extend(event_list)
            cpage += 1
            
        return all_events
        
    def fetch_event_detail(self, mt20id):
        url = f"{self.detail_url}{mt20id}"
        params = {"service": self.apikey}
        
        response = requests.get(url, params=params)
        data = xmltodict.parse(response.content)

        return data.get('dbs', {}).get('db', [])
    
    
    def extract_relate_url(self, detail):
        relate_raw = detail.get('relates', {}).get('relate', [])
        
        relate_list = [relate_raw] if isinstance(relate_raw, dict) else relate_raw
        
        if relate_list and len(relate_list) > 0:
            return relate_list[0].get('relateurl')
        return None


    def collect_all_data(self, stdate, eddate):
        final_list = []
        events_list = self.fetch_event_list(stdate, eddate)
        print(f"총 {len(events_list)}개의 공연 발견. 상세 정보 수집 시작...")
        
        for item in events_list:
            target_id = item.get('mt20id')
            
            detail = self.fetch_event_detail(target_id)
            
            time.sleep(0.15)
            
            refined = {
                'kopis_id': target_id,
                'title': detail.get('prfnm'),
                'artist': detail.get('prfcast'),
                'start_date': detail.get('prfpdfrom').replace('.', '-'),
                'end_date': detail.get('prfpdto').replace('.', '-'),
                'venue': detail.get('fcltynm'),
                'age': detail.get('prfage'),
                'poster': detail.get('poster'),
                'time': detail.get('dtguidance'),
                'price': detail.get('pcseguidance'),
                'update_date': detail.get('updatedate'),
                'relate_url': self.extract_relate_url(detail),
                'host': detail.get('entrpsnmH'),
            }
            final_list.append(refined)

        return final_list
    
if __name__ == "__main__":
    collector = KopisDataCollector()
    
    s, e = collector.get_date_range()
    result = collector.collect_all_data(stdate=s, eddate=e)
    print(f"최종 수집 완료 : {len(result)}건")
    print("-------공연 데이터 수집 결과-------")
    print(result)
    
    #print(collector.collect_all_data(stdate=20260105,eddate=20260106))