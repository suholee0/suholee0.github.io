# URL to Korean Blog Post Translator

영문 기술 블로그 포스트를 한국어로 번역하여 Jekyll 블로그에 게시하는 자동화 도구입니다.

## 번역 워크플로우

```
┌─────────────────────────────────────────────────────────────┐
│                         사용자 입력                           │
│                    python3 translate_blog.py                 │
│                    https://example.com/article               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  📥 1. Content Fetcher                       │
│                                                              │
│  • URL 접속 (requests)                                       │
│  • HTML 파싱 (newspaper3k / BeautifulSoup)                  │
│  • 본문 텍스트 추출                                          │
│  • 이미지 URL 목록 수집                                      │
│  • 메타데이터 추출 (제목, 저자, 날짜)                        │
│                                                              │
│  Output: {                                                   │
│    content: "원문 텍스트...",                                │
│    metadata: {...},                                          │
│    images: ["url1", "url2", ...]                            │
│  }                                                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  🤖 2. OpenAI Translator                     │
│                                                              │
│  프롬프트 생성:                                              │
│  ┌────────────────────────────────────────────────┐        │
│  │ "이 영문 기술 블로그를 한국어로 번역해주세요"    │        │
│  │ • 기술 용어는 한글(English) 형태로               │        │
│  │ • 코드 블록은 그대로 유지                        │        │
│  │ • 핵심 요약 섹션 추가                            │        │
│  │ • Jekyll 포맷으로 구조화                         │        │
│  └────────────────────────────────────────────────┘        │
│                           ↓                                  │
│                    OpenAI API 호출                           │
│                  (gpt-4o-mini/gpt-4o)                        │
│                           ↓                                  │
│  Output: {                                                   │
│    title: "[해외 포스트] 제목",                              │
│    categories: ["Tech Translation", "..."],                  │
│    tags: ["tag1", "tag2"],                                  │
│    content: "번역된 본문..."                                 │
│  }                                                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  🖼️ 3. Image Handler                         │
│                                                              │
│  이미지 URL 목록 순회:                                       │
│  ┌────────────────────────────────────────────────┐        │
│  │  for each image_url:                            │        │
│  │    1. 다운로드 (requests)                       │        │
│  │    2. 리사이즈 (max 1400px)                     │        │
│  │    3. 최적화 (Pillow, 85% quality)              │        │
│  │    4. 저장: assets/img/posts/2025/파일명.jpg    │        │
│  │    5. URL 매핑 업데이트                         │        │
│  └────────────────────────────────────────────────┘        │
│                                                              │
│  Output: {                                                   │
│    "원본URL1": "/assets/img/posts/2025/image1.jpg",         │
│    "원본URL2": "/assets/img/posts/2025/image2.jpg"          │
│  }                                                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  📝 4. Post Generator                        │
│                                                              │
│  1. Front Matter 생성:                                       │
│     ---                                                      │
│     title: "[해외 포스트] ..."                               │
│     date: 2025-10-28 15:30:00 +0900                         │
│     categories: ["Tech Translation", "Frontend"]             │
│     tags: [react, hooks, optimization]                       │
│     original_author: "Dan Abramov"                          │
│     ---                                                      │
│                                                              │
│  2. 콘텐츠 처리:                                             │
│     • 이미지 URL을 로컬 경로로 치환                         │
│     • Jekyll 이미지 스타일 추가                             │
│       {:width="700" .shadow}                                │
│                                                              │
│  3. 파일 저장:                                               │
│     _posts/2025-10-28-translated-title.md                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     ✅ 완료!                                 │
│                                                              │
│  생성된 파일:                                                │
│  • _posts/2025-10-28-translated-title.md                    │
│  • assets/img/posts/2025/image1.jpg                         │
│  • assets/img/posts/2025/image2.jpg                         │
│                                                              │
│  다음 단계:                                                  │
│  1. 포스트 내용 검토                                        │
│  2. git add . && git commit && git push                     │
│  3. GitHub Pages 자동 배포 대기                             │
└─────────────────────────────────────────────────────────────┘
```

## 설치

1. Python 의존성 설치:
```bash
cd scripts
python3 -m pip install -r requirements.txt
```

2. OpenAI API 키 설정:
```bash
cp .env.example .env
# .env 파일을 열어서 OPENAI_API_KEY 입력
```

## 사용법

```bash
# 기본 사용
python3 translate_blog.py <URL>

# 예시
python3 translate_blog.py https://overreacted.io/before-you-memo/
```

## 기능

- 🌐 URL에서 콘텐츠 자동 추출 (newspaper3k)
- 🤖 OpenAI GPT로 한국어 번역
- 🖼️ 이미지 다운로드 및 최적화
- 📝 Jekyll 포맷 마크다운 생성
- 🏷️ 자동 카테고리/태그 생성

## 출력

- 생성된 포스트: `_posts/YYYY-MM-DD-제목.md`
- 다운로드된 이미지: `assets/img/posts/YYYY/`

## 환경 변수

- `OPENAI_API_KEY`: OpenAI API 키 (필수)
- `OPENAI_MODEL`: 사용할 모델 (기본: gpt-4o-mini)

## 비용

- GPT-4o-mini: 약 $0.01-0.02 per post
- GPT-4o: 약 $0.05-0.10 per post

## 주의사항

- 긴 포스트는 자동으로 잘려서 번역됩니다 (8000자 제한)
- 이미지는 최대 10개까지 다운로드됩니다
- 생성된 포스트는 검토 후 필요시 수정하세요