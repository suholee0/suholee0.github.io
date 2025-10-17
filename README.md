# 딥러닝 논문 리뷰 블로그 관리 가이드

블로그 URL: https://suholee0.github.io

## 📝 새 포스트 작성하기

### 1. 포스트 파일 생성
`_posts` 폴더에 새 파일 생성:
```
_posts/YYYY-MM-DD-제목.md
```

예시: `_posts/2025-01-20-transformer-paper-review.md`

### 2. Front Matter 작성 (필수)
파일 최상단에 다음 형식으로 작성:

```yaml
---
title: "[논문리뷰] 논문 제목"
date: YYYY-MM-DD HH:MM:SS +0900
categories: [Paper Review, 분야]
tags: [태그1, 태그2, 태그3]
math: true                    # 수식 사용시
mermaid: true                 # 다이어그램 사용시
image:
  path: /assets/img/파일명.png  # 대표 이미지 (선택)
  alt: 이미지 설명
---
```

### 3. 카테고리 옵션
- `[Paper Review, Computer Vision]` - CNN, Vision Transformer 등
- `[Paper Review, NLP]` - Transformer, BERT, GPT 등
- `[Paper Review, Generative Model]` - GAN, VAE, Diffusion 등
- `[Paper Review, Reinforcement Learning]` - RL 관련
- `[General, Tutorial]` - 튜토리얼, 가이드

### 4. 포스트 작성 후 배포
```bash
git add .
git commit -m "Add: 논문제목 리뷰"
git push origin main
```

5-10분 후 블로그에 자동 반영됨

## 🎨 블로그 설정 변경

### 블로그 제목/설명 변경
`_config.yml` 파일 수정:
```yaml
title: 블로그 제목
tagline: 부제목
description: 블로그 설명
```

### 작성자 정보 변경
`_config.yml` 파일 수정:
```yaml
author:
  name: 이름
  email: 이메일
  github: GitHub 아이디
```

### 댓글 기능 활성화
1. [Giscus](https://giscus.app) 접속
2. 설정 후 생성된 정보를 `_config.yml`에 추가:
```yaml
comments:
  active: giscus
  giscus:
    repo: suholee0/suholee0.github.io
    repo_id: 자동생성값
    category: Announcements
    category_id: 자동생성값
```

## 📁 중요 파일/폴더 구조

```
├── _posts/          # 블로그 포스트 (여기에 글 작성!)
├── _config.yml      # 블로그 전체 설정
├── assets/
│   └── img/        # 포스트에 사용할 이미지 저장
├── _sass/          # 스타일 커스터마이징 (고급)
└── index.html      # 홈페이지 (수정 불필요)
```

## 💡 작성 팁

### 수식 작성
```markdown
인라인 수식: $a^2 + b^2 = c^2$

블록 수식:
$$
\mathbf{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$
```

### 이미지 삽입
```markdown
![설명](/assets/img/image.png)
```

### 코드 블록
````markdown
```python
def attention(q, k, v):
    scores = torch.matmul(q, k.transpose(-2, -1))
    return torch.matmul(F.softmax(scores, dim=-1), v)
```
````

### 목차 자동 생성
Front Matter에 `toc: true` 추가하면 자동으로 목차 생성

## 🔧 로컬에서 미리보기

```bash
# 의존성 설치 (최초 1회)
bundle install

# 로컬 서버 실행
bundle exec jekyll serve

# 브라우저에서 확인
# http://localhost:4000
```

## ⚠️ 주의사항

1. **파일명 형식 엄수**: `YYYY-MM-DD-제목.md`
2. **Front Matter 필수**: 없으면 포스트가 표시되지 않음
3. **이미지 경로**: `/assets/img/` 폴더 사용
4. **푸시 후 반영 시간**: 5-10분 소요

## 📚 참고 자료

- [Chirpy 테마 문서](https://chirpy.cotes.page/)
- [Jekyll 변수](https://jekyllrb.com/docs/variables/)
- [Markdown 문법](https://www.markdownguide.org/cheat-sheet/)

---

문제 발생시 Issues 탭에 문의