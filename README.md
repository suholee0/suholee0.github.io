# 딥러닝 논문 리뷰 블로그

딥러닝 논문을 리뷰하고 정리하는 개인 기술 블로그입니다.

- **URL**: https://suholee0.github.io
- **테마**: Jekyll Chirpy
- **배포**: GitHub Pages

## 📝 Notion 연동 구조

이 블로그는 Notion과 자동으로 연동되어 있어, Notion에서 글을 작성하면 자동으로 블로그에 포스팅됩니다.

### 연동 방식
- Notion 데이터베이스에서 글 작성 → GitHub Actions가 자동 변환 → Jekyll 블로그에 배포
- 자세한 설정 방법은 [NOTION_SETUP.md](NOTION_SETUP.md) 참고

### 포스팅 업데이트 방법

1. **Notion 데이터베이스에서 글 작성**
   - 제목, 내용, 카테고리, 태그 등 작성
   - 이미지, 수식, 코드블록 모두 지원

2. **published 필드를 `publish required`로 변경**
   - `not published`: 초안 (동기화 안 됨)
   - `publish required`: 게시 대기 (동기화됨) ← 이것으로 변경!
   - `already published`: 이미 게시됨 (재동기화 안 됨)

3. **GitHub Actions 워크플로우 실행**
   - **자동 실행**: 매주 월요일 오전 9시 (한국시간)
   - **수동 실행**:
     1. GitHub 저장소 → Actions 탭
     2. "Sync Notion to Jekyll" 선택
     3. "Run workflow" 버튼 클릭

4. **블로그 확인**
   - 5-10분 후 https://suholee0.github.io 에서 확인
   - 게시 완료 후 Notion에서 `already published`로 변경 권장

## 🚀 로컬 개발

```bash
# 의존성 설치
bundle install

# 로컬 서버 실행
bundle exec jekyll serve

# http://localhost:4000 에서 확인
```

## 📁 프로젝트 구조

```
.
├── _posts/          # 블로그 포스트 (Notion에서 자동 생성)
├── _tabs/           # 상단 네비게이션 탭
├── assets/
│   └── img/
│       ├── profile.png    # 프로필 이미지
│       └── posts/         # 포스트 이미지 (자동 다운로드)
├── scripts/
│   └── notion-to-jekyll.js  # Notion 동기화 스크립트
├── .github/workflows/
│   ├── pages-deploy.yml     # GitHub Pages 배포
│   └── notion-sync.yml      # Notion 동기화
├── _config.yml      # Jekyll 설정
├── package.json     # Node.js 의존성
└── NOTION_SETUP.md  # Notion 연동 상세 가이드
```

## 📄 라이선스

[MIT License](LICENSE)