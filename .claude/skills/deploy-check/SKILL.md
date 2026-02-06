# /deploy-check - Vercel 배포 전 점검

배포 전 다음 항목을 순서대로 점검하고 한국어로 보고해줘:

## 1. 파일 추적 확인
- `git ls-files web/` 로 web 디렉토리 파일이 Git에 추적되는지 확인
- config.js, app.js, style.css, index.html 이 포함되어야 함

## 2. 환경 변수 확인
- .env 파일에 SUPABASE_URL, SUPABASE_KEY 존재 여부 확인
- web/config.js 에 Supabase URL/Key가 하드코딩되어 있는지 확인

## 3. 빌드/정적 파일 확인
- web/index.html 이 존재하고 정상적인 HTML인지 확인
- JavaScript 파일에 문법 에러가 없는지 간단 체크

## 4. .gitignore 점검
- .env, node_modules 등 민감 파일이 .gitignore에 포함되어 있는지 확인
- 배포에 필요한 파일이 .gitignore에 잘못 포함되어 있지 않은지 확인

## 5. 요약 리포트
아래 형식으로 보고:
```
Git 추적: OK / 문제 있음 (누락 파일: ...)
환경 변수: OK / 문제 있음 (누락: ...)
정적 파일: OK / 문제 있음
.gitignore: OK / 문제 있음
배포 가능 여부: 가능 / 불가능 (사유: ...)
```
