# AWS Lambda에서 사용할 최종 코드

import json
import logging
from datetime import datetime, timedelta
from kopis_transform import transform_event_data
from database import DatabaseManager
from get_date_range import get_date_range
    
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS Lambda 메인 핸들러 함수
def lambda_handler(event, context):
    logger.info("Lambda Start")
    
    try:
        start_date, end_date = get_date_range(2)
        logger.info(f"공연 정보 수집 범위 : {start_date} ~ {end_date}")
        
        events_data = transform_event_data(start_date, end_date)
        
        if not events_data:
            logger.info("데이터가 없거나 변환에 실패했습니다.")
            return {
                'statusCode': 200,
                'body': json.dumps("진행할 데이터가 없습니다.")
            }
            
        db_manager = DatabaseManager()
        db_manager.upsert_events(events_data)
        
        logger.info(f"성공적으로 {len(events_data)}개의 공연을 수집했습니다.")
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"성공 : {len(events_data)}개의 공연을 저장했습니다.")
        }

    except Exception as e:
        logger.error(f"에러 : {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"에러 : {str(e)}")
        }

# 로컬 테스트        
if __name__=='__main__':
    lambda_handler(None, None)
    print("-----------cd 성공!---------")