#!/usr/bin/env python3
"""
Polymarket 시장 제목 한글 번역 스크립트 (덮어쓰기 모드)

사용법:
    export OPENAI_API_KEY="your-api-key"
    export SUPABASE_URL="your-supabase-url"
    export SUPABASE_KEY="your-supabase-key"
    python translate_feb11_15_bot.py

특징:
    - 오늘부터 2개월 이내 종료 시장 번역 (KST 기준)
    - Sports 카테고리 제외
    - Title_ko 덮어쓰기 (이미 번역이 있어도 재번역)
    - translation_prompt.md의 규칙 + 용어집 후처리 적용
    - 배치 크기: 100개씩 처리 (OpenAI API)
"""

import os
import sys
import time
import threading
import re
from typing import List, Dict
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from supabase import create_client, Client
from datetime import datetime

# .env 파일 로드 (프로젝트 루트에서)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# 설정값
BATCH_SIZE = 100  # 한 번에 100개씩 번역
MAX_RETRIES = 3  # 재시도 횟수
DEFAULT_WORKERS = 4  # 기본 워커 수

# 용어 교정 사전: LLM이 용어집을 무시했을 때 강제 교정
# {잘못된 표기: 올바른 표기}
GLOSSARY_CORRECTIONS = {
    # 인물명
    '엘론 머스크': '일론 머스크',
    '엘론이': '일론이',
    '엘론의': '일론의',
    '엘론은': '일론은',
    '반스': '밴스',
    '젤렌스끼': '젤렌스키',
    '습근평': '시진핑',
    '주커버그': '저커버그',
    '알트만': '올트먼',
    '네탄야후': '네타냐후',
    '매크롱': '마크롱',
    # 정치/사회
    '행정 명령': '행정명령',
    '경기 침체': '경기침체',
    '아카데미상': '오스카상',
    '아카데미 시상식': '오스카 시상식',
    '슈퍼 볼': '슈퍼볼',
    # 금융
    '연방준비': '연준',
    '이자율': '금리',
    '에어드롭': '에어드랍',
}


def apply_glossary_corrections(text: str) -> str:
    """번역 결과에서 잘못된 용어를 교정"""
    for wrong, correct in GLOSSARY_CORRECTIONS.items():
        if wrong in text:
            text = text.replace(wrong, correct)
    return text

# 날짜 범위: 오늘부터 2개월 (KST → UTC 변환)
# KST는 UTC+9 이므로, -9시간 해야 UTC
from datetime import timedelta, timezone
_now_utc = datetime.now(timezone.utc)
_today_kst_start_utc = _now_utc.replace(hour=15, minute=0, second=0, microsecond=0) - timedelta(days=1)
if _now_utc.hour >= 15:
    _today_kst_start_utc = _now_utc.replace(hour=15, minute=0, second=0, microsecond=0)
START_DATE = _today_kst_start_utc.strftime('%Y-%m-%d %H:%M:%S+00')
END_DATE = (_today_kst_start_utc + timedelta(days=60)).strftime('%Y-%m-%d %H:%M:%S+00')

# 번역 프롬프트 (translation_prompt.md 내용을 직접 삽입)
TRANSLATION_PROMPT = """당신은 Polymarket 예측 시장 제목을 한국어로 번역하는 전문가입니다.

## 핵심 원칙

1. **반말 사용**: 모든 번역은 반말로 끝내야 합니다 (~할까?, ~될까?, ~인가?)
2. **날짜 한글화**: 월(Month)은 한글로 변환하되 일(Day)과 연도(Year)는 숫자 유지 (February 11 → 2월 11일, March 2026 → 3월 2026년)
3. **시간대 표기 필수**: ET, PT 등 시간대는 **반드시** 유지해야 합니다 (4AM ET → 오전 4시 ET, 2PM PT → 오후 2시 PT)
4. **간결성**: 원문의 뉘앙스를 유지하되 자연스러운 한국어로 변환
5. **일관성**: 같은 패턴은 같은 방식으로 번역

---

## 번역 규칙

### 1. Will 질문형 → "~할까?", "~될까?"

**패턴**: Will [주어] [동사] ...?

**예시**:
- Will Bitcoin reach $150,000 in February? → 비트코인이 2월에 $150,000에 도달할까?
- Will Trump nominate Judy Shelton as the next Fed chair? → 트럼프가 차기 연준 의장으로 Judy Shelton을 지명할까?

---

### 2. 수치 비교형 → "~보다 높을까?", "~보다 낮을까?"

**패턴**: [주어] above/below/greater than/less than [숫자]

**예시**:
- Will the price of Bitcoin be above $76,000 on February 11? → 비트코인 가격이 2월 11일에 $76,000보다 높을까?
- Zama auction clearing price above $0.05? → Zama 옥션 청산 가격이 $0.05보다 높을까?

---

### 3. 범위형 (between) → "~와 ~ 사이일까?"

**패턴**: between [숫자1] and [숫자2]

**예시**:
- Will MrBeast's next video get between 30 and 35 million views on day 1? → MrBeast의 다음 영상이 첫날 3천만~3천5백만 조회수를 기록할까?

---

### 4. 날짜/시간 포함형 → 날짜 그대로 유지

#### A. on [date] → "~에"
- Bitcoin Up or Down on February 11? → 비트코인이 2월 11일에 오를까 내릴까?

#### B. by [date] → "~까지"
- US x Iran meeting by February 6, 2026? → 미국과 이란이 2026년 2월 6일까지 회담할까?

#### C. in [year] → "~년에"
- US recession in 2025? → 2025년 미국 경기 침체?

#### D. before [time] → "~전에"
- Will Trump acquire Greenland before 2027? → 트럼프가 2027년 전에 그린란드를 인수할까?

#### E. 시간대 포함 (ET, PT 등) → **반드시 유지**
- Bitcoin Up or Down - February 11, 4AM ET → 비트코인 - 2월 11일, 오전 4시 ET에 오를까 내릴까?
- Ethereum Up or Down - February 10, 2PM PT → 이더리움 - 2월 10일, 오후 2시 PT에 오를까 내릴까?
- XRP Up or Down - February 11, 8AM ET → XRP - 2월 11일, 오전 8시 ET에 오를까 내릴까?

---

### 5. Up/Down 방향 예측 → "오를까 내릴까?"

**패턴**: [자산] Up or Down

**예시**:
- Bitcoin Up or Down - February 11, 2AM ET → 비트코인 - 2월 11일, 오전 2시 ET에 오를까 내릴까?
- Ethereum Up or Down on February 11? → 이더리움이 2월 11일에 오를까 내릴까?

---

### 6. 승패 예측형 → "~가 우승할까?", "~가 이길까?"

**패턴**: Will [팀/선수] win ...?

**예시**:
- Will the Indiana Pacers win the 2026 NBA Finals? → 인디애나 페이서스가 2026 NBA 파이널에서 우승할까?

---

## 용어집 (반드시 준수)

### 인물명 (⚠️ 다른 표기 절대 사용 금지)
- **Elon Musk** → 일론 머스크 (❌ 엘론 머스크)
- **Trump** → 트럼프
- **JD Vance** → 밴스 (❌ 반스)
- **Putin** → 푸틴
- **Xi Jinping** → 시진핑
- **Zelensky** → 젤렌스키 (❌ 젤렌스끼)
- **Sam Altman** → 샘 올트먼 (❌ 알트만)
- **Mark Zuckerberg** → 마크 저커버그 (❌ 주커버그)

### 금융/암호화폐
- **Bitcoin** → 비트코인
- **Ethereum** → 이더리움
- **Solana** → 솔라나
- **XRP** → XRP (원어 유지)
- **FDV** (Fully Diluted Valuation) → 시가총액(FDV) 또는 FDV
- **bps** (basis points) → bps
- **Fed** → 연준
- **interest rates** → 금리

### 정치/사회
- **executive order** → 행정명령 (❌ 행정 명령)
- **recession** → 경기침체
- **ceasefire** → 휴전
- **Oscar** → 오스카 (❌ 아카데미)

### 숫자 표현 (원문 유지)
- **$76,000** → $76,000 (쉼표 포함 그대로)
- **$500b** → $500b (b/m/k 그대로)
- **$1t** → $1t
- **50+ bps** → 50+ bps

### 시간 표현 (시간대 반드시 유지!)
- **February 11** → 2월 11일 ✅
- **March 31, 2026** → 2026년 3월 31일 ✅
- **2AM ET** → 오전 2시 ET ✅ (ET 반드시 포함!)
- **4PM PT** → 오후 4시 PT ✅ (PT 반드시 포함!)
- **day 1** → 첫날 또는 day 1

---

## 주의사항

### ❌ 하지 말아야 할 것
1. 존댓말 사용 (~할까요?, ~될까요?)
2. 날짜를 영문 그대로 유지 (February 11 → 2월 11일로 변환 필수)
3. **시간대 누락** (4AM ET → 오전 4시 ❌, 오전 4시 ET ✅)
4. 숫자 변환 ($76,000 → 7만 6천 달러)
5. 의역이나 과도한 해석

### ✅ 반드시 해야 할 것
1. 반말로 끝내기 (~할까?, ~될까?, ~인가?)
2. 날짜 한글화 (February 11 → 2월 11일, March 2026 → 2026년 3월)
3. **시간 한글화하되 시간대는 반드시 유지** (2AM ET → 오전 2시 ET, 4PM PT → 오후 4시 PT)
4. 숫자/금액 원문 유지 ($76,000, 50+ bps)
5. 전문 용어 적절히 처리 (FDV, bps 등)

---

## 출력 형식

**입력이 1개인 경우**:
번역된 제목만 출력하세요. 설명이나 부가 정보는 포함하지 마세요.

**입력이 여러 개인 경우**:
번호와 함께 출력하세요.

---

## 추가 예시 (시간대 표기 중점)

### 예시 1
**원문**: Bitcoin Up or Down - February 11, 4AM ET
**번역**: 비트코인 - 2월 11일, 오전 4시 ET에 오를까 내릴까?

### 예시 2
**원문**: Ethereum Up or Down - February 10, 2PM PT
**번역**: 이더리움 - 2월 10일, 오후 2시 PT에 오를까 내릴까?

### 예시 3
**원문**: XRP Up or Down - February 11, 8AM ET
**번역**: XRP - 2월 11일, 오전 8시 ET에 오를까 내릴까?

### 예시 4
**원문**: Solana Up or Down on February 12?
**번역**: 솔라나가 2월 12일에 오를까 내릴까?

---

이제 번역할 Polymarket 시장 제목을 입력하세요.
"""


class TitleTranslator:
    def __init__(self, num_workers: int = 1):
        # API 키 확인
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')

        if not all([self.openai_key, self.supabase_url, self.supabase_key]):
            print("❌ 환경 변수를 설정해주세요:")
            print("   export OPENAI_API_KEY='your-key'")
            print("   export SUPABASE_URL='your-url'")
            print("   export SUPABASE_KEY='your-key'")
            sys.exit(1)

        # 클라이언트 초기화
        self.openai_client = OpenAI(api_key=self.openai_key)
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # 병렬 처리 설정
        self.num_workers = num_workers

        # 통계 (Thread-safe)
        self.lock = threading.Lock()
        self.total_translated = 0
        self.total_batches = 0
        self.failed_batches = 0

    def get_event_batch(self, offset: int, limit: int) -> List[Dict]:
        """이벤트 배치 조회 (2월 11-15일, Sports 제외)"""
        response = self.supabase.table('poly_events') \
            .select('id, title, category, end_date') \
            .gte('end_date', START_DATE) \
            .lt('end_date', END_DATE) \
            .neq('category', 'Sports') \
            .limit(limit) \
            .offset(offset) \
            .execute()

        return response.data

    def _fix_timezone_consistency(self, original: str, translated: str) -> str:
        """번역에서 시간대(ET, PT 등)가 누락된 경우 자동 추가"""
        # 원문에서 시간대 패턴 찾기 (ET, PT, EST, PST, UTC 등)
        timezone_pattern = r'\b([0-9]{1,2}(?::[0-9]{2})?(?:AM|PM)?)\s+(ET|PT|EST|PST|UTC|GMT)\b'
        original_match = re.search(timezone_pattern, original, re.IGNORECASE)

        if not original_match:
            return translated  # 원문에 시간대 없으면 그대로 반환

        timezone = original_match.group(2).upper()  # ET, PT 등

        # 번역에서 시간대가 있는지 확인
        if timezone in translated:
            return translated  # 이미 시간대가 있으면 그대로 반환

        # 시간대가 누락된 경우: "오후 2시에" → "오후 2시 ET에"로 수정
        time_patterns = [
            (r'(오전|오후)\s*(\d{1,2})시에', rf'\1 \2시 {timezone}에'),  # "오후 2시에" → "오후 2시 ET에"
            (r'(오전|오후)\s*(\d{1,2})시\s*(\d{1,2})분에', rf'\1 \2시 \3분 {timezone}에'),  # "오후 2시 30분에" → "오후 2시 30분 ET에"
            (r'자정에', f'자정 {timezone}에'),  # "자정에" → "자정 ET에"
            (r'정오에', f'정오 {timezone}에'),  # "정오에" → "정오 ET에"
        ]

        for pattern, replacement in time_patterns:
            if re.search(pattern, translated):
                fixed = re.sub(pattern, replacement, translated)
                return fixed

        return translated  # 패턴을 찾지 못하면 그대로 반환

    def translate_batch(self, titles: List[str]) -> List[str]:
        """배치 번역 (최대 100개)"""
        if not titles:
            return []

        # 번역 요청 텍스트 생성
        titles_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(titles)])
        request_text = f"{TRANSLATION_PROMPT}\n\n번역할 제목들:\n{titles_text}"

        # OpenAI API 호출 (재시도 로직 포함)
        for attempt in range(MAX_RETRIES):
            try:
                completion = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",  # GPT-4o-mini 모델 (빠르고 저렴)
                    max_tokens=5000,
                    temperature=0.3,  # 낮은 temperature로 규칙 준수 강화
                    messages=[
                        {"role": "system", "content": """당신은 전문 번역가입니다.

중요 규칙:
1. 반드시 반말로 번역 (~할까, ~될까, ~인가)
2. 절대 존댓말 사용 금지 (~할까요, ~될까요 ❌)
3. 시간대 표기 필수: ET, PT 등은 반드시 유지 (4AM ET → 오전 4시 ET ✅, 오전 4시 ❌)
4. 모든 제목에서 일관성 유지

시간대 예시:
- "Bitcoin Up or Down - February 11, 4AM ET" → "비트코인 - 2월 11일, 오전 4시 ET에 오를까 내릴까?"
- "XRP Up or Down - February 11, 8AM ET" → "XRP - 2월 11일, 오전 8시 ET에 오를까 내릴까?"
"""},
                        {"role": "user", "content": request_text}
                    ]
                )

                response_text = completion.choices[0].message.content.strip()

                # 🔧 개선된 파싱: 번호 기반으로 정확히 매칭
                translations_dict = {}  # {번호: 번역}로 저장
                for line in response_text.split('\n'):
                    line = line.strip()
                    if not line:
                        continue

                    # "1. 번역" 형식에서 번호와 번역 추출
                    if '. ' in line and line[0].isdigit():
                        parts = line.split('. ', 1)
                        try:
                            num = int(parts[0])
                            translation = parts[1]
                            translations_dict[num] = translation  # 번호로 매칭
                        except (ValueError, IndexError):
                            continue

                # 번호 순서대로 정렬 + 시간대 일관성 검증 + 용어 교정
                translations = []
                for i in range(len(titles)):
                    translation = translations_dict.get(i+1, titles[i])  # 번역 없으면 원본
                    # 시간대 일관성 검증 및 수정
                    translation = self._fix_timezone_consistency(titles[i], translation)
                    # 용어 교정 (glossary 후처리)
                    translation = apply_glossary_corrections(translation)
                    translations.append(translation)

                # 검증: 번역 개수가 원본과 다르면 경고
                if len(translations) != len(titles):
                    print(f"  ⚠️  번역 개수 불일치: {len(translations)} != {len(titles)}")

                return translations

            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"  ⚠️  재시도 {attempt + 1}/{MAX_RETRIES}")
                    time.sleep(2 ** attempt)
                else:
                    print(f"  ❌ API 호출 실패: {e}")
                    return []

        return []

    def update_translations(self, event_ids: List[str], translations: List[str]) -> int:
        """번역 결과를 DB에 업데이트 (덮어쓰기 모드)"""
        success_count = 0

        for event_id, translation in zip(event_ids, translations):
            try:
                self.supabase.table('poly_events') \
                    .update({'title_ko': translation}) \
                    .eq('id', event_id) \
                    .execute()
                success_count += 1
            except Exception as e:
                print(f"  ❌ 업데이트 실패 (ID: {event_id[:8]}...): {e}")

        return success_count

    def process_batch(self, batch_num: int, offset: int) -> Dict:
        """단일 배치 처리 (워커 스레드에서 실행)"""
        # 워커별 독립 클라이언트 생성 (Connection pool 고갈 방지)
        worker_supabase = create_client(self.supabase_url, self.supabase_key)

        try:
            # 배치 조회
            response = worker_supabase.table('poly_events') \
                .select('id, title, category, end_date') \
                .gte('end_date', START_DATE) \
                .lt('end_date', END_DATE) \
                .neq('category', 'Sports') \
                .limit(BATCH_SIZE) \
                .offset(offset) \
                .execute()

            batch_events = response.data

            if not batch_events:
                return {'success': False, 'count': 0, 'reason': 'empty'}

            batch_titles = [e['title'] for e in batch_events]
            batch_ids = [e['id'] for e in batch_events]

            # 번역
            translations = self.translate_batch(batch_titles)

            if len(translations) != len(batch_titles):
                translations = translations[:len(batch_titles)]

            # DB 업데이트 (재시도 로직 추가)
            success = self._update_with_retry(worker_supabase, batch_ids, translations)

            # 통계 업데이트 (Thread-safe)
            with self.lock:
                self.total_translated += success
                self.total_batches += 1

            return {
                'success': True,
                'batch_num': batch_num,
                'count': success,
                'total': len(batch_titles)
            }

        except Exception as e:
            with self.lock:
                self.failed_batches += 1

            return {
                'success': False,
                'batch_num': batch_num,
                'error': str(e)
            }

    def _update_with_retry(self, supabase_client: Client, event_ids: List[str], translations: List[str]) -> int:
        """DB 업데이트 (재시도 로직 포함)"""
        success_count = 0

        for event_id, translation in zip(event_ids, translations):
            for attempt in range(MAX_RETRIES):
                try:
                    supabase_client.table('poly_events') \
                        .update({'title_ko': translation}) \
                        .eq('id', event_id) \
                        .execute()
                    success_count += 1
                    break  # 성공하면 다음 항목으로
                except Exception as e:
                    if attempt < MAX_RETRIES - 1:
                        # 재시도 전 대기
                        time.sleep(0.5 * (attempt + 1))
                    else:
                        # 최종 실패
                        print(f"  ❌ 업데이트 실패 (ID: {event_id[:8]}..., {MAX_RETRIES}번 시도): {e}")

        return success_count

    def run(self, max_batches: int = None):
        """병렬 번역 실행"""
        is_parallel = self.num_workers > 1

        print("\n🚀 Polymarket 제목 번역 시작 (오늘~2개월, Sports 제외)\n")
        print(f"📅 날짜 범위: {START_DATE} ~ {END_DATE} (UTC)")
        print(f"🚫 제외 카테고리: Sports")
        print(f"🔄 덮어쓰기 모드: Title_ko 기존 값 무시하고 재번역")

        if is_parallel:
            print(f"⚡ 병렬 처리: {self.num_workers}개 워커")
        else:
            print(f"📝 순차 처리: 1개 워커")

        print()

        # 전체 개수 확인
        total_response = self.supabase.table('poly_events') \
            .select('id', count='exact') \
            .gte('end_date', START_DATE) \
            .lt('end_date', END_DATE) \
            .neq('category', 'Sports') \
            .execute()

        total_count = total_response.count if hasattr(total_response, 'count') else 0
        total_batches_expected = (total_count + BATCH_SIZE - 1) // BATCH_SIZE

        if max_batches:
            total_batches_expected = min(total_batches_expected, max_batches)

        print(f"📊 대상 이벤트: {total_count:,}개")
        print(f"📦 예상 배치 수: {total_batches_expected}개")

        if is_parallel:
            print(f"⏱️  예상 시간: ~{(total_batches_expected * 1.5 / self.num_workers / 60):.1f}분\n")
        else:
            print(f"⏱️  예상 시간: ~{(total_batches_expected * 1.5 / 60):.1f}분\n")

        start_time = time.time()

        if is_parallel:
            # 병렬 처리
            self._run_parallel(total_batches_expected)
        else:
            # 순차 처리
            self._run_sequential(total_batches_expected, total_count)

        # 완료
        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"🎉 번역 완료!")
        print(f"   총 {self.total_translated:,}개 이벤트 번역됨")
        print(f"   성공 배치: {self.total_batches}개")
        print(f"   실패 배치: {self.failed_batches}개")
        print(f"   소요 시간: {elapsed/60:.1f}분")
        if self.total_translated > 0:
            print(f"   평균 속도: {self.total_translated/(elapsed/60):.0f}개/분")
        print(f"{'='*60}\n")

    def _run_parallel(self, total_batches_expected: int):
        """병렬 처리 실행"""
        # 배치 목록 생성
        batch_jobs = []
        for i in range(total_batches_expected):
            offset = i * BATCH_SIZE
            batch_jobs.append((i + 1, offset))

        # 병렬 처리
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            # 모든 배치 제출
            futures = {
                executor.submit(self.process_batch, batch_num, offset): (batch_num, offset)
                for batch_num, offset in batch_jobs
            }

            # 완료된 순서대로 결과 출력
            for future in as_completed(futures):
                result = future.result()

                if result['success']:
                    if result.get('reason') == 'empty':
                        continue

                    batch_num = result['batch_num']
                    count = result['count']

                    # 진행률 계산
                    progress = (self.total_batches / total_batches_expected) * 100

                    print(f"✅ 배치 {batch_num:3d}/{total_batches_expected} 완료 | "
                          f"{count:3d}개 번역 | "
                          f"누적: {self.total_translated:,}개 ({progress:.1f}%)")
                else:
                    if result.get('reason') == 'empty':
                        continue
                    batch_num = result.get('batch_num', '?')
                    error = result.get('error', 'Unknown')
                    print(f"❌ 배치 {batch_num} 실패: {error}")

    def _run_sequential(self, total_batches_expected: int, total_count: int):
        """순차 처리 실행"""
        batch_num = 0
        offset = 0

        while batch_num < total_batches_expected:
            batch_num += 1

            # 배치 조회
            print(f"📦 배치 {batch_num}/{total_batches_expected} 조회 중... (offset: {offset})")
            batch_events = self.get_event_batch(offset, BATCH_SIZE)

            if not batch_events:
                print(f"\n✅ 모든 이벤트 처리 완료!")
                break

            batch_titles = [e['title'] for e in batch_events]
            batch_ids = [e['id'] for e in batch_events]

            print(f"   → {len(batch_events)}개 이벤트 발견, 번역 중...")

            # 번역
            translations = self.translate_batch(batch_titles)

            if len(translations) != len(batch_titles):
                print(f"  ⚠️  번역 수 불일치: {len(translations)} != {len(batch_titles)}")
                translations = translations[:len(batch_titles)]

            # DB 업데이트
            success = self.update_translations(batch_ids, translations)
            self.total_translated += success
            self.total_batches += 1

            print(f"   ✅ {success}/{len(batch_titles)}개 업데이트 완료")
            print(f"   누적: {self.total_translated}/{total_count}개 번역됨 ({self.total_translated/total_count*100:.1f}%)\n")

            # 다음 배치로
            offset += BATCH_SIZE

            # API Rate Limit 방지 (1초 대기)
            time.sleep(1)




def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='Polymarket 2월 11-15일 제목 한글 번역 (병렬 처리 지원)')
    parser.add_argument('--workers', type=int, default=1,
                        help=f'워커 수 (기본: 1, 병렬 처리 권장: {DEFAULT_WORKERS})')
    parser.add_argument('--max-batches', type=int, default=None,
                        help='최대 배치 수 (테스트용)')
    parser.add_argument('--test', action='store_true',
                        help='테스트 모드 (1개 배치만)')

    args = parser.parse_args()

    # 테스트 모드
    if args.test:
        args.max_batches = 1
        print("🧪 테스트 모드: 1개 배치만 처리합니다\n")

    # 워커 수 검증
    if args.workers < 1:
        print("❌ 워커 수는 1 이상이어야 합니다")
        sys.exit(1)

    if args.workers > 10:
        print("⚠️  워커가 너무 많으면 API Rate Limit에 걸릴 수 있습니다")
        print("   권장: 3-5개 워커")
        response = input("   계속하시겠습니까? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)

    # 번역 실행
    translator = TitleTranslator(num_workers=args.workers)
    translator.run(max_batches=args.max_batches)


if __name__ == '__main__':
    main()
