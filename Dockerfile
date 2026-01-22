# 1. 파이썬 실행 환경 설정 (가볍고 보안에 강한 slim 버전 추천)
FROM python:3.11-slim

# 2. 컨테이너 내부 작업 디렉토리 생성
WORKDIR /app

# 3. 시스템 의존성 설치 (필요한 경우에만)
# 만약 마리아DB나 특정 라이브러리가 시스템 패키지를 요구하면 여기에 추가합니다.
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. 라이브러리 설치 (캐시 최적화를 위해 소스 코드보다 먼저 복사)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 소스 코드 복사
COPY . .

# 6. 실행 명령 (ETL의 메인 실행 파일을 지정)
# 예: python main.py
CMD ["python", "lambda_function.py"]
