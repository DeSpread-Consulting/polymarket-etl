# 📊 폴리마켓 시장 이름 유형화 및 한국어 번역 규칙

> 💡 **분석 기준**
> - Supabase `poly_events` 테이블
> - 총 **416,657개** 시장 데이터 분석
> - 작성일: 2026-02-06

---

# 1️⃣ 시장 이름 유형 분류

## 1.1 💰 Crypto 카테고리

### 📌 주요 패턴
- "Up or Down" 형식: **60%**
- "Will" 질문 형식: **40%**
- 가격 범위 "between": **12%**

### 유형별 예시

**단기 등락 예측** (15분 단위)
```
Bitcoin Up or Down - October 1, 7:15PM-7:30PM ET
```

**가격 도달 여부** (특정 날짜)
```
Will the price of Ethereum be less than $4,000 on October 9?
```

**가격 범위 예측**
```
Will the price of Bitcoin be between $102,000 and $104,000 on October 5?
```

### 🔄 번역 규칙

**패턴 1: "Up or Down"**
```
영문: Bitcoin Up or Down - October 1, 7:15PM-7:30PM ET
한글: 비트코인 상승 또는 하락 - 10월 1일 오후 7시 15분~7시 30분 (동부 표준시)
```

**패턴 2: "Will the price of X be [조건]"**
```
영문: Will the price of Ethereum be less than $4,000 on October 9?
한글: 이더리움 가격이 10월 9일에 4,000달러 미만일까요?
```

**패턴 3: "between A and B"**
```
영문: Will the price be between $102,000 and $104,000?
한글: 가격이 102,000달러와 104,000달러 사이일까요?
```

---

## 1.2 🏛️ Politics 카테고리

### 📌 주요 패턴
- "Will" 질문 형식: **90%**
- 물음표로 끝남: **98%**
- 인물 중심 예측: **대부분**

### 유형별 예시

**정치 행동 예측**
```
Will Trump deport 500,000-750,000 people?
```

**발언 예측**
```
Will Trump say "Stupid person" this week?
```

**국제 관계**
```
US strikes Iran by February 1, 2026?
```

**인사 발표**
```
Will Trump announce Elon Musk to replace Kugler?
```

### 🔄 번역 규칙

**패턴 1: "Will [주체] [동사] [목적어/조건]?"**
```
영문: Will Trump deport 500,000-750,000 people?
한글: 트럼프가 50만~75만 명을 추방할까요?
```

**패턴 2: "Will [주체] say '[단어]'"**
```
영문: Will Trump say "Stupid person" this week?
한글: 트럼프가 이번 주 "멍청한 사람"이라고 말할까요?
```

**패턴 3: "[주체] [동사] [목적어] by [날짜]?"**
```
영문: US strikes Iran by February 1, 2026?
한글: 2026년 2월 1일까지 미국이 이란을 공습할까요?
```

---

## 1.3 💵 Finance 카테고리

### 📌 주요 패턴
- "Will" 질문 형식: **44%**
- "Anytime Touchdown" 형식: **22%** (스포츠 베팅)
- "Up or Down" 형식: **4%**

### 유형별 예시

**주가 등락**
```
Apple (AAPL) Up or Down on January 28?
```

**주가 목표치**
```
Will S&P 500 (SPX) close over 5,550 on Friday?
```

**스포츠 베팅** ⚠️
```
George Pickens: Anytime Touchdown
First Touchdown: Javonte Williams
```

### 🔄 번역 규칙

**패턴 1: "[주식명] ([티커]) Up or Down on [날짜]?"**
```
영문: Apple (AAPL) Up or Down on January 28?
한글: 1월 28일 애플(AAPL) 상승 또는 하락?
```

**패턴 2: "Will [지수] close over [가격]"**
```
영문: Will S&P 500 (SPX) close over 5,550 on Friday?
한글: S&P 500(SPX)이 금요일에 5,550 이상으로 마감할까요?
```

> ⚠️ **주의사항**
> 한국에서는 스포츠 베팅이 불법이므로 "Anytime Touchdown" 등의 유형은 번역 제외 권장

---

## 1.4 🎬 Pop Culture 카테고리

### 📌 주요 패턴
- "Will" 질문 형식: **92%**
- 물음표로 끝남: **100%**
- "between" 범위 예측: **28%**

### 유형별 예시

**앨범 출시**
```
New Rihanna Album before GTA VI?
```

**박스오피스 예측**
```
Will "Predator: Badlands" Opening Weekend Box Office be less than 29m?
```

**주가 목표치**
```
Will Netflix reach $175 in January?
```

**스트리밍 순위**
```
Will EoO by Bad Bunny be the 3rd most streamed song globally on Spotify for 2025?
```

**캐스팅 소식**
```
Tom Hardy announced as next James Bond?
```

### 🔄 번역 규칙

**패턴 1: "New [아티스트] Album before [이벤트]?"**
```
영문: New Rihanna Album before GTA VI?
한글: GTA VI 전에 리한나의 새 앨범이 나올까요?
```

**패턴 2: "Will '[영화명]' Opening Weekend Box Office be [조건]?"**
```
영문: Will "Predator: Badlands" Opening Weekend Box Office be less than 29m?
한글: "프레데터: 배드랜즈" 개봉 주말 박스오피스가 2,900만 달러 미만일까요?
```

**패턴 3: "Will [회사] reach $[가격] in [월]?"**
```
영문: Will Netflix reach $175 in January?
한글: 1월에 넷플릭스가 175달러에 도달할까요?
```

**패턴 4: "[인물] announced as [역할]?"**
```
영문: Tom Hardy announced as next James Bond?
한글: 톰 하디가 차기 제임스 본드로 발표될까요?
```

---

## 1.5 🔬 Science 카테고리

### 📌 주요 패턴
- "Will" 질문 형식: **72%**
- 물음표로 끝남: **84%**
- ⚠️ 일부 오분류 포함 (스포츠 경기 등)

### 유형별 예시

**기술 출시**
```
Will Tesla launch a driverless Robotaxi service by August 31?
```

**자율주행**
```
Tesla launches unsupervised full self driving (FSD) by October 31?
```

**암호화폐 에어드랍**
```
Rabby airdrop in Q3 2025?
```

**AI 모델 순위**
```
Will Meituan have the second-best AI model at the end of January 2026?
```

**날씨 예측**
```
Will the highest temperature in Buenos Aires be 30°C on December 20?
```

### 🔄 번역 규칙

**패턴 1: "Will [회사] launch [제품/서비스] by [날짜]?"**
```
영문: Will Tesla launch a driverless Robotaxi service by August 31?
한글: 8월 31일까지 테슬라가 무인 로보택시 서비스를 출시할까요?
```

**패턴 2: "[제품] airdrop in [기간]?"**
```
영문: Rabby airdrop in Q3 2025?
한글: 2025년 3분기에 Rabby 에어드랍이 있을까요?
```

**패턴 3: "Will [회사] have the [순위] AI model"**
```
영문: Will Meituan have the second-best AI model at the end of January 2026?
한글: 2026년 1월 말에 Meituan이 두 번째로 좋은 AI 모델을 보유할까요?
```

**패턴 4: "Will the [기상 요소] be [값]?"**
```
영문: Will the highest temperature in Buenos Aires be 30°C on December 20?
한글: 12월 20일 부에노스아이레스의 최고 기온이 30°C일까요?
```

---

## 1.6 ⚽ Sports 카테고리

### 📌 주요 패턴
- "vs" 대결 형식: **76%**
- "O/U" (Over/Under) 베팅: **24%**
- "Will" 질문 형식: **30%**

### 유형별 예시

**팀 대결**
```
Blues vs. Blackhawks
```

**총점 O/U**
```
Games Total: O/U 3.5
```

**점수차 예측**
```
Spread: Red Wings (-1.5)
```

**경기별 O/U**
```
Red Wings vs. Sharks: O/U 6.5
```

> ⚠️ **중요 경고**
>
> 한국에서는 **체육진흥투표권법**에 따라 스포츠토토(국내) 외의 스포츠 베팅이 **불법**입니다.
>
> **따라서 Sports 카테고리는 번역을 권장하지 않습니다.**

---

# 2️⃣ 번역 규칙 종합

## ✅ DO (권장 사항)

### 1. 의문형 유지
- 영문이 질문이면 한국어도 **"~할까요?"** 형태로 유지
- 예: "Will X happen?" → "X가 발생할까요?"

### 2. 숫자 표기 통일
- 금액: `$1,000` → `1,000달러` (쉼표 유지)
- 큰 단위: `$1m` → `100만 달러`, `$1b` → `10억 달러`
- 퍼센트: `50%` → `50%`

### 3. 날짜 현지화
- 미국식: `October 9` → 한국식: `10월 9일`
- 시간대 표기: `ET` → `동부 표준시`, `PT` → `태평양 표준시`
- 요일: `Friday` → `금요일`

### 4. 고유명사 처리
- 인물명: 원음 표기 (예: Trump → 트럼프)
- 회사명: 통용 표기 우선 (예: Apple → 애플, Netflix → 넷플릭스)
- 브랜드: 원어 유지 or 통용 표기 (예: Bitcoin → 비트코인)

### 5. 간결함 유지
- 불필요한 조사 생략
- 예: "~에 대해서" → "~에 대해"

---

## ❌ DON'T (피해야 할 사항)

### 1. 직역체 지양
- ❌ 나쁜 예: "비트코인의 가격이 될 것인가?"
- ✅ 좋은 예: "비트코인 가격이 ~일까요?"

### 2. 과도한 의역 금지
- 원문의 핵심 정보 보존
- 조건/숫자는 정확히 번역

### 3. 불필요한 존댓말 과다 사용
- 간결한 "~할까요?" 형태 선호
- "~하실까요?", "~되실까요?" 등은 과도

### 4. 베팅 용어 직역 금지
- "Over/Under" → ~~"오버/언더"~~ (차라리 영문 유지)
- "Spread" → ~~"스프레드"~~ (의미 전달 우선)

---

## 🎯 카테고리별 번역 우선순위

| 카테고리 | 우선순위 | 이유 | 비율 |
|---------|---------|------|------|
| 💰 **Crypto** | ⭐⭐⭐⭐⭐ 최우선 | 한국 커뮤니티 관심도 높음 | ~20% |
| 🏛️ **Politics** | ⭐⭐⭐⭐ 높음 | 글로벌 정치 관심사 | ~15% |
| 🎬 **Pop Culture** | ⭐⭐⭐⭐ 높음 | 엔터/문화 콘텐츠 수요 | ~10% |
| 🔬 **Science** | ⭐⭐⭐ 중간 | 기술/과학 관심층 대상 | ~5% |
| 💵 **Finance** | ⭐⭐ 낮음 | 스포츠 베팅 포함 (법적 이슈) | ~10% |
| ⚽ **Sports** | ⭐ 최하위 | 한국 법적 제약 (불법 도박) | ~40% |

---

## 📚 특수 표현 번역 사전

### 일반 표현

| 영문 | 한국어 | 비고 |
|------|--------|------|
| Up or Down | 상승 또는 하락 | 주가/코인 등락 |
| Will | ~할까요? | 의문형 |
| between A and B | A와 B 사이 | 범위 |
| less than | ~미만 | 부등호 |
| greater than | ~초과 | 부등호 |
| more than | ~이상 | 부등호 |
| by [날짜] | [날짜]까지 | 기한 |
| on [날짜] | [날짜]에 | 특정일 |
| before [이벤트] | [이벤트] 전에 | 시간 비교 |

### Crypto 전용

| 영문 | 한국어 | 비고 |
|------|--------|------|
| Bitcoin | 비트코인 | 고유명사 |
| Ethereum | 이더리움 | 고유명사 |
| the price of X | X 가격 / X의 가격 | 맥락에 따라 선택 |

### Politics 전용

| 영문 | 한국어 | 비고 |
|------|--------|------|
| deport | 추방하다 | 이민 정책 |
| announce | 발표하다 | 공식 발표 |
| strike | 공습하다, 공격하다 | 군사 행동 |

### Pop Culture 전용

| 영문 | 한국어 | 비고 |
|------|--------|------|
| Opening Weekend Box Office | 개봉 주말 박스오피스 | 영화 수익 |
| reach $X | X달러에 도달하다 | 주가 목표 |
| announced as | ~로 발표되다 | 캐스팅 소식 |

### Science 전용

| 영문 | 한국어 | 비고 |
|------|--------|------|
| launch | 출시하다 | 제품 출시 |
| driverless | 무인, 자율주행 | 자동차 |
| airdrop | 에어드랍 | 암호화폐 |
| Q1/Q2/Q3/Q4 | 1분기/2분기/3분기/4분기 | 분기 표기 |

---

# 3️⃣ 구현 방법

## 현재 구현 상태

**파일:** `translate_titles.py`

- OpenAI API 사용하여 영문 시장 이름을 한국어로 번역
- `title` → `title_ko` 필드에 저장

**번역 대상:**
- ✅ Crypto
- ✅ Politics
- ✅ Finance (일부)
- ✅ Pop Culture
- ✅ Science
- ❌ Sports (제외됨 - 법적 이슈)

---

## 🔧 번역 방식 비교

### A. 프롬프트 기반 번역 (현재 방식)

**장점:**
- 유연한 번역
- 복잡한 문장도 처리 가능
- 자연스러운 한국어

**단점:**
- 비용 발생 (OpenAI API)
- 느린 속도
- 일관성 보장 어려움

### B. 패턴 기반 번역 (제안)

**장점:**
- 빠른 속도
- 무료
- 일관성 높음

**단점:**
- 패턴 미매칭 시 처리 불가
- 초기 개발 비용

### C. 하이브리드 방식 (✅ 추천)

1. **1단계**: 패턴 매칭으로 90% 처리 (빠름, 일관성 높음)
2. **2단계**: 패턴 미매칭 시 OpenAI API 사용 (유연함)
3. **3단계**: 사람 검수 (품질 보증)

---

## ✅ 번역 품질 자동 검증 규칙

### 1. 물음표 일관성
- 원문이 `?`로 끝나면 번역문도 `?`로 끝나야 함

### 2. 숫자 일관성
- 원문과 번역문의 숫자 개수가 일치해야 함

### 3. 길이 제한
- 번역문이 원문보다 **2배 이상 길면** → 오번역 가능성
- 번역문이 원문보다 **30% 미만 짧으면** → 오번역 가능성

### 4. 금지 단어 체크
- Sports 카테고리에서 **"오버", "언더", "스프레드"** 등의 베팅 용어 포함 시 경고

---

# 4️⃣ 통계 및 권장 사항

## 📊 카테고리별 예상 분포

| 카테고리 | 예상 시장 수 | 비율 | 번역 권장 |
|---------|------------|------|----------|
| ⚽ Sports | ~167,000개 | ~40% | ❌ **제외** |
| 💰 Crypto | ~83,000개 | ~20% | ✅ **최우선** |
| 🏛️ Politics | ~62,000개 | ~15% | ✅ **우선** |
| 💵 Finance | ~42,000개 | ~10% | ⚠️ **선별** (스포츠 베팅 제외) |
| 🎬 Pop Culture | ~42,000개 | ~10% | ✅ **우선** |
| 🔬 Science | ~21,000개 | ~5% | ✅ **포함** |

---

## 🎯 번역 작업 로드맵

### Phase 1 (최우선) 🔥
**대상:** Crypto + Politics + Pop Culture
- 약 **18만~20만 개** 시장
- 한국 커뮤니티 관심도 가장 높음
- 예상 기간: 2-3주

### Phase 2 (차순위)
**대상:** Science + Finance (선별)
- 약 **6만~8만 개** 시장
- Finance는 스포츠 베팅 제외하고 주가만 포함
- 예상 기간: 1-2주

### Phase 3 (제외) ⛔
**대상:** Sports
- 약 **16만~18만 개** 시장
- 한국 법적 제약으로 번역 및 서비스 제외

---

# 5️⃣ 실행 가이드

## 🚀 번역 스크립트 실행

### 기존 스크립트 (OpenAI API)
```bash
python translate_titles.py
```

### 새로운 패턴 기반 스크립트 (제안)
```bash
python translate_titles_v2.py --categories "Crypto,Politics,Pop Culture"
```

---

## 💾 Supabase 스키마 업데이트

### 필수 컬럼 추가
```sql
-- title_ko 컬럼 추가
ALTER TABLE poly_events
ADD COLUMN IF NOT EXISTS title_ko TEXT;

-- 번역 품질 메타데이터
ALTER TABLE poly_events
ADD COLUMN IF NOT EXISTS translation_method TEXT,
ADD COLUMN IF NOT EXISTS translation_confidence FLOAT;

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_poly_events_title_ko
ON poly_events(title_ko);
```

---

## 🌐 웹 UI 업데이트

### app.js 수정 (한국어 우선 표시)
```javascript
function renderEvent(event) {
    // 한국어 번역이 있으면 우선 표시
    const displayTitle = event.title_ko || event.title;

    return `
        <div class="event-card">
            <h3>${displayTitle}</h3>
            ${event.title_ko ? `<p class="original">${event.title}</p>` : ''}
        </div>
    `;
}
```

---

# 6️⃣ 체크리스트

## ✅ 번역 작업 전

- [ ] 번역 대상 카테고리 확정
  - [ ] Crypto ⭐⭐⭐⭐⭐
  - [ ] Politics ⭐⭐⭐⭐
  - [ ] Pop Culture ⭐⭐⭐⭐
  - [ ] Science ⭐⭐⭐
  - [ ] Finance ⚠️ (스포츠 베팅 제외)
  - [ ] Sports ❌ (전체 제외)

- [ ] Sports/Finance 중 스포츠 베팅 필터링 로직 구현
- [ ] OpenAI API 키 설정 확인 (`.env` 파일)
- [ ] Supabase 스키마 업데이트 완료

---

## ✅ 번역 작업 중

- [ ] 패턴별 샘플 번역 테스트 (카테고리당 10개)
- [ ] 자동 검증 규칙 적용 및 에러 모니터링
- [ ] 번역 품질 모니터링 (주기적 샘플 체크)
- [ ] 진행률 대시보드 구축 (선택)

---

## ✅ 번역 작업 후

- [ ] 웹 UI에서 한국어 표시 확인
  - [ ] 캘린더 뷰에서 title_ko 표시
  - [ ] 모달 창에서 원문/번역 모두 표시

- [ ] 검색 기능에 title_ko 포함
  ```javascript
  filtered.filter(e =>
      e.title?.toLowerCase().includes(query) ||
      e.title_ko?.includes(query) ||  // 한국어 검색 추가
      e.category?.toLowerCase().includes(query)
  );
  ```

- [ ] 사용자 피드백 수집 채널 마련
  - [ ] "번역 오류 신고" 버튼 추가
  - [ ] Google Form 또는 Discord 채널 연동

- [ ] 주기적 번역 업데이트 스케줄 설정
  - [ ] 신규 시장은 자동 번역 (cron job)
  - [ ] 주 1회 품질 검수

---

# 7️⃣ 관련 파일

| 파일 | 용도 |
|------|------|
| `/schema.sql` | 데이터베이스 스키마 |
| `/main.py` | Polymarket API 수집 스크립트 |
| `/translate_titles.py` | 번역 스크립트 |
| `/web/app.js` | 프론트엔드 코드 |
| `/web/config.js` | Supabase 연결 설정 |
| `/migration.sql` | DB 마이그레이션 |

---

# 💬 Q&A

> 💡 **Q1: Sports 카테고리를 왜 제외하나요?**
>
> A: 한국 **체육진흥투표권법**에 따라 국내 스포츠토토 외의 스포츠 베팅은 불법입니다. 법적 리스크를 피하기 위해 번역 및 서비스에서 제외합니다.

> 💡 **Q2: Finance 카테고리는 어떻게 처리하나요?**
>
> A: Finance는 **주가 예측**과 **스포츠 베팅**이 혼재되어 있습니다. 주가 관련 시장만 선별하여 번역하고, "Anytime Touchdown" 등의 스포츠 베팅은 제외합니다.

> 💡 **Q3: 번역 비용은 얼마나 드나요?**
>
> A: OpenAI GPT-4 API 기준:
> - Phase 1 (20만 개): 약 $200~300
> - Phase 2 (8만 개): 약 $80~120
> - **총 예상 비용: $280~420**
>
> 패턴 기반 번역으로 90%를 처리하면 비용을 **$30~50**로 절감 가능합니다.

> 💡 **Q4: 번역 품질은 어떻게 보장하나요?**
>
> A: 3단계 품질 관리:
> 1. 자동 검증 (물음표, 숫자 일관성)
> 2. 샘플 검수 (카테고리당 100개)
> 3. 사용자 피드백 수집 및 반영

---

# 📌 작성자 노트

이 문서는 **416,657개** 시장 데이터를 분석하여 작성되었습니다.

실제 번역 작업 시 샘플 테스트를 통해 규칙을 검증하고, 필요에 따라 수정하시기 바랍니다.

---

**문서 버전**: 1.0
**최종 수정**: 2026-02-06
**담당자**: [담당자명 입력]
