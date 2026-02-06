# /status - 프로젝트 상태 체크

다음을 순서대로 실행하고 결과를 한국어로 요약해줘:

## 1. 로컬 서버 상태
- `lsof -i :8080` 으로 포트 점유 확인
- `curl -s -o /dev/null -w "%{http_code}" http://localhost:8080` 으로 응답 확인
- 둘 다 실행해서 실제 상태를 판단할 것

## 2. Git 상태
- `git status` 로 변경된 파일 확인
- `git log --oneline -5` 로 최근 커밋 5개 확인

## 3. Supabase 연결 상태
- Python으로 Supabase에 테스트 쿼리 실행 (LIMIT 1)
- 연결 성공/실패 여부 보고

## 4. 요약 리포트
아래 형식으로 보고:
```
서버: 실행 중 / 중지됨 (포트 8080)
Git: 변경 N개 / 클린 | 최근 커밋: [메시지]
Supabase: 연결됨 / 연결 실패
```
