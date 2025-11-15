# TbotV9

TbotV9은 사용자가 자신만의 거래 전략을 쉽게 자동화할 수 있도록 지원하는 지능형 자동 거래 플랫폼입니다. 자세한 내용은 `PRD.md` 파일을 참고해주세요.

## 시작하기

### 1. 프로젝트 복제

```bash
git clone https://github.com/your-username/tbotv9.git
cd tbotv9
```

### 2. 백엔드 설정

백엔드 애플리케이션은 FastAPI로 구축되었습니다.

```bash
# tbot 디렉토리로 이동
cd tbot

# 가상 환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 필요한 API 키 등을 설정합니다.
```

### 3. 프론 Regeln드 설정

프론트엔드 애플리케이션은 React와 Vite로 구축되었습니다.

```bash
# tbot/frontend 디렉토리로 이동
cd tbot/frontend

# 의존성 설치
npm install
```

## 개발 서버 실행

### 백엔드

프로젝트 루트 디렉토리에서 다음 명령어를 실행하세요.

```bash
# tbot 가상 환경이 활성화된 상태여야 합니다.
PYTHONPATH=. tbot/venv/bin/uvicorn tbot.app.main:app --reload
```

서버는 `http://127.0.0.1:8000`에서 실행됩니다.

### 프론트엔드

`tbot/frontend` 디렉토리에서 다음 명령어를 실행하세요.

```bash
npm run dev
```

개발 서버는 `http://localhost:5173`에서 실행됩니다.

## 테스트 실행

### 백엔드

프로젝트 루트 디렉토리에서 다음 명령어를 실행하세요.

```bash
# tbot 가상 환경이 활성화된 상태여야 합니다.
PYTHONPATH=. tbot/venv/bin/pytest
```

### 프론트엔드

`tbot/frontend` 디렉토리에서 다음 명령어를 실행하세요.

```bash
# 아직 테스트 스크립트가 설정되지 않았습니다.
# 추후 React Testing Library 및 Playwright를 사용한 테스트 스크립트가 추가될 예정입니다.
npm test
```
