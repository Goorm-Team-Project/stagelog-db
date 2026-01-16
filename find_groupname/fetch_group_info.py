import os
import json
import pymysql
import traceback
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_ROOT_PASSWORD'),
        db=os.getenv('DB_NAME'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
def fetch_groupname_info(event_list):
    if not event_list:
        return {}
    
    items_text = ""
    for idx, item in enumerate(event_list):
        items_text += f"ID_{idx}: 제목[{item['title']}] / 출연[{item['artist']}]\n"
    
    prompt = (
        "당신은 K-POP 공연 데이터 분석가입니다. 입력된 공연 목록을 보고 K-POP 아이돌 그룹 여부를 판단하세요.\n"
        "**출연진들이 하나의 'K-POP 아이돌 그룹(또는 밴드)' 멤버들로 구성된 경우**에만 해당 그룹명을 추출하세요.\n\n"
        "[필수 규칙]\n"
        "1. **1:1 대응 원칙**: 입력된 **모든 ID**에 대해 반드시 응답해야 합니다.\n"
        "2. **대상 포함**: \n"
        "  - 일반적인 댄스 아이돌 그룹 (예: BTS, IVE, ITZY)\n"
        "  - 아이돌형 밴드 (예: DAY6, QWER)\n"
        "3. **아이돌 식별**: 출연진이 특정 'K-POP 아이돌 그룹' 멤버들로 구성된 경우만 그룹명을 한글로 적으세요.\n"
        "   - 예: 공연명 'LE SSERAFIM TOUR', 출연 '김채원, 사쿠라, 허윤진' -> '르세라핌'\n"
        "4. **엄격한 제외**: 다음의 경우 반드시 `null`을 반환하세요.\n"
        "   - 출연진이 서로 다른 그룹/가수로 섞여 있는 경우 (예: '성시경, 아이유, 싸이' 또는 'NCT, 에스파, 아이브') -> `null`\n"
        "   - 포크, 트로트, 힙합 크루, 발라드 가수 (예: 쎄시봉, 송창식)\n"
        "   - 뮤지컬, 연극, 클래식 (예: 조승우, 옥주현)\n"
        "   - 페스티벌 (여러 가수가 따로 출연)\n"
        "5. **언어**: 그룹명은 반드시 **한국어**로 반환하세요. (BTS -> 방탄소년단, ITZY -> 있지)\n"
        "6. **형식**: `{'ID_0': '그룹명', 'ID_1': null, ...}` 형태의 JSON.\n\n"
        f"[분석할 데이터]\n{items_text}"
    )
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "JSON format only. Output format: {\"0\": \"Group Name\", \"1\": null}"}, 
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        result_text = completion.choices[0].message.content

        result_json = json.loads(result_text)
    
        cleaned_result = {}
        for key, value in result_json.items():
            if key.startswith("ID_"):
                clean_key = key.replace("ID_", "")
                cleaned_result[clean_key] = value
            elif key.isdigit():
                 cleaned_result[key] = value
                
        return cleaned_result
    
    except Exception as e:
        print(f"❌ GPT 호출 중 에러 발생:")
        print(traceback.format_exc()) 
        return {}