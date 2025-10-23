# 📝 Notion → Jekyll 블로그 자동화 설정 가이드

> ⚠️ **Notion API 알림** (2025.09.03 업데이트 대응)
> - 현재 스크립트는 안정적인 API 버전(2022-06-28)을 사용합니다
> - 기존 Database ID 방식으로 정상 작동합니다
> - 추후 SDK 업데이트 시 자동 마이그레이션 예정

## 🚀 빠른 시작 (10분 소요)

### Step 1: Notion Integration 생성 (3분)

1. **Integration 생성**
   - https://www.notion.so/my-integrations 접속
   - "New integration" 클릭
   - Name: `Blog Publisher`
   - Capabilities: **Read content** 체크
   - Submit

2. **Secret Key 복사**
   - `secret_xxxxx...` 형태의 키 복사 (나중에 사용)

### Step 2: Notion Database 생성 (5분)

1. **새 데이터베이스 생성**
   - Notion에서 새 페이지 → Table 선택

2. **필수 속성 추가**
   | 속성명 | 타입 | 설명 |
   |--------|------|------|
   | Title (또는 이름) | Title | 포스트 제목 |
   | published | Select | 옵션: `not published`, `publish required`, `already published` |
   | Category (또는 카테고리) | Select | Paper Review, Tutorial 등 |
   | Tags (또는 태그) | Multi-select | transformer, cnn, gan 등 |
   | Date (또는 날짜) | Date | 작성 날짜 |

3. **Integration 연결**
   - 데이터베이스 페이지 우측 상단 "..." 클릭
   - "Add connections" → "Blog Publisher" 선택

4. **Database ID 찾기**
   - 데이터베이스 URL: `https://notion.so/xxxxxxxxxxxxx?v=yyyy`
   - Database ID = `xxxxxxxxxxxxx` (32자리)

### Step 3: GitHub 설정 (2분)

1. **Repository Secrets 추가**
   - https://github.com/suholee0/suholee0.github.io/settings/secrets/actions
   - "New repository secret" 클릭

2. **두 개의 Secret 추가**
   - Name: `NOTION_API_KEY`
     Value: (Step 1에서 복사한 Secret Key)

   - Name: `NOTION_DATABASE_ID`
     Value: (Step 2에서 찾은 Database ID)

## ✅ 사용 방법

### 1. 노션에서 글 작성
- 데이터베이스에 새 항목 추가
- 제목, 내용 작성 (이미지, 수식, 코드 모두 지원)
- Category, Tags 설정
- **published를 `publish required`로 설정** (중요!)

### 2. 동기화 실행

**방법 1: 수동 실행**
- GitHub → Actions 탭 → "Sync Notion to Jekyll"
- "Run workflow" 버튼 클릭

**방법 2: 자동 실행**
- 매일 오전 9시, 오후 9시 자동 실행

### 3. 확인
- Actions 탭에서 실행 상태 확인
- 5-10분 후 https://suholee0.github.io 에서 확인

## 🎯 지원 기능

✅ **자동 변환**
- Notion 형식 → Jekyll Markdown
- 이미지 자동 다운로드 (`/assets/img/posts/년도/`)
- 수식 변환 ($$수식$$ 지원)
- 코드블록 변환

✅ **메타데이터**
- 카테고리, 태그 자동 매핑
- 날짜 자동 설정
- 제목에서 URL 슬러그 자동 생성

## ⚠️ 주의사항

1. **published 상태 관리**
   - `not published`: 초안 (동기화 안 됨)
   - `publish required`: 게시 대기 (동기화됨)
   - `already published`: 이미 게시됨 (재동기화 안 됨)
2. **속성명** - 대소문자 구분 (published는 소문자로)
3. **이미지** - 자동으로 다운로드되어 저장됨
4. **첫 실행** - npm 패키지 설치로 약간 시간 걸림

## 🐛 문제 해결

**"object_not_found" 에러**
- Database ID 확인
- Integration이 데이터베이스에 연결되었는지 확인

**"unauthorized" 에러**
- API Key 확인
- Secret 설정 확인

**포스트가 안 보임**
- published 속성이 `publish required`로 설정되었는지 확인
- GitHub Actions 로그 확인