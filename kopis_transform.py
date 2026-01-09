import os
import re
from kopis_detail import get_performance_detail_list
from openai import OpenAI
from database import DatabaseManager


client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# AI에 활동명 물어보기
def fetch_stage_name_from_ai(raw_name, title):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "당신은 K-POP 및 공연 예술 데이터 정규화 전문가입니다. "
                        "제공된 정보를 종합하여 해당 아티스트의 '대중적인 활동명(예명)'을 찾아내세요.\n\n"
                        "[분석 규칙]\n"
                        "1. **지식 활용**: 'JT2DE'가 '저스디스'의 앨범명이라거나, '허승'이 '저스디스'의 본명이라는 것과 같은 당신의 사전 학습 지식을 적극 활용하세요.\n"
                        "2. **아이돌/래퍼**: K-POP 아이돌이나 래퍼는 본명이 입력되면 반드시 활동명으로 변환하세요. (예: 안유진 -> 안유진(변환X), 김민지 -> 민지(뉴진스 등 문맥 확인))\n"
                        "3. **일반인/클래식/연극**: 유명하지 않거나 활동명을 따로 쓰지 않는 배우, 연주자 등은 변환하지 말고 그대로 반환하세요.\n"
                        "4. **보수적 접근**: 확신이 없으면 추측하지 말고 입력된 이름을 그대로 반환하세요."
                    )
                },
                # 예시를 통해 패턴 학습
                {"role": "user", "content": "Title: i-dle WORLD TOUR, Syncopation IN SEOUL, Name: 미야와키 사쿠라"},
                {"role": "assistant", "content": "사쿠라"},
                {"role": "user", "content": "Title: LE SSERAFIM TOUR: EASY CRAZY HOT [서울 (앵콜) ], Name: 제니퍼 윤진 허"},
                {"role": "assistant", "content": "허윤진"},
                {"role": "user", "content": "Title: i-dle WORLD TOUR, Syncopation IN SEOUL, Name: 니차 욘따라락"},
                {"role": "assistant", "content": "민니"},
                {"role": "user", "content": "Title: LOCO CONCERT: SCRAPS TOUR [서울], Name: 권혁우"},
                {"role": "assistant", "content": "로꼬"},
                {"role": "user", "content": "Title: ITZY 3RD WORLD TOUR: TUNNEL VISION [서울], Name: 최지수"},
                {"role": "assistant", "content": "리아"},
                {"role": "user", "content": "Title: JT2DE: LIT, Name: 허승"},
                {"role": "assistant", "content": "저스디스"},

                {"role": "user", "content": f"title: {title}, Name: {raw_name}"} # 실제 질문
            ],
            temperature=0.1 # 창의성을 0에 가깝게 낮춰서 창의성 낮추기
        )
        result = completion.choices[0].message.content.strip()
        
        # AI가 "원래 이름을 그대로 반환합니다." 같은 응답을 하면 원본 반환
        if len(result) > 30 or "반환" in result:
            return raw_name
        
        return result
     
    except Exception as e:
        print(f"OpenAI API 호출 에러 ({raw_name}) : {e}")
        return raw_name # AI 에러 나면 본명 반환


def process_artist_names(raw_artist_string, title, db_manager):
    if not raw_artist_string or raw_artist_string == "정보 없음":
        return raw_artist_string
    
    # 정규식으로 '등, 외' 제거 및 분리
    cleaned_string = re.sub(r'\s*(?:등|외)\s*(?:,|$)', ',', raw_artist_string)
    raw_name_list = [name.strip() for name in cleaned_string.split(',') if name.strip()]
   
    final_names_list = []
    
    for raw_name in raw_name_list:        
        # DB 조회: 이미 아는 이름인가?
        cached_stage_name = db_manager.get_stage_name(raw_name)
        
        if cached_stage_name: # 아티스트 활동명이 이미 있으면 그대로 사용
            final_names_list.append(cached_stage_name)
        else: # 없으면 AI에 물어보고 DB에 저장
            print(f"[LLM 호출] 새로운 아티스트 발견 : {raw_name}")
            new_stage_name = fetch_stage_name_from_ai(raw_name, title)
            
            db_manager.save_artist_mapping(raw_name, new_stage_name)
            
            final_names_list.append(new_stage_name)
        
    # 다시 합쳐서 문자열로 반환    
    return ', '.join(final_names_list)
            


#매핑표에 따라 API 데이터를 DB 필드용으로 변환
def transform_event_data(start_date, end_date):
    performance_detail_list = get_performance_detail_list(start_date, end_date)
    transform_list = []
    
    db_manager = DatabaseManager()
    
    try:
        print("데이터 변환 및 아티스트명 정규화 시작...")
        
        for performance_detail in performance_detail_list:
            if performance_detail:
                
                original_artist = performance_detail.get('prfcast') if performance_detail.get('prfcast') else '정보 없음'
                title = performance_detail.get('prfnm', '')
                
                cleaned_artist = process_artist_names(original_artist, title, db_manager)
          
                transform_list.append({'kopis_id':performance_detail.get('mt20id'),
                    'title': title,
                    'artist': cleaned_artist,
                    'start_date': performance_detail.get('prfpdfrom','').replace('.','-'),
                    'end_date': performance_detail.get('prfpdto','').replace('.','-'),
                    'venue': performance_detail.get('fcltynm',),
                    'age': performance_detail.get('prfage'),
                    'poster': performance_detail.get('poster'),
                    'time': performance_detail.get('dtguidance'),
                    'price': performance_detail.get('pcseguidance'),
                    'update_date': performance_detail.get('updatedate')[:19], # 년월일 시간분초까지 슬라이싱
                    'relate_url': check_list_or_dict(performance_detail.get('relates', {}).get('relate')),
                    'host': performance_detail.get('entrpsnmH') if performance_detail.get('entrpsnmH') else '정보 없음',
                    'genre': '대중음악'
                    })   
        
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