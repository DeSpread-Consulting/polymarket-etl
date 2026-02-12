#!/usr/bin/env python3
"""
2026년 2월 11일~15일 이벤트만 빠르게 번역 (병렬 처리)

사용법:
    export OPENAI_API_KEY="your-api-key"
    export SUPABASE_URL="your-supabase-url"
    export SUPABASE_KEY="your-supabase-key"
    python translate_feb11_15.py
"""

import os
import sys
import time
import threading
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from supabase import create_client, Client

# 설정값
BATCH_SIZE = 100
MAX_RETRIES = 3
NUM_WORKERS = 4

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

# 날짜 범위 (KST 기준)
START_DATE = '2026-02-11'
END_DATE = '2026-02-16'  # 2월 15일 23:59까지 포함하려면 16일로 설정

# 번역 프롬프트 로드
def load_translation_prompt():
    """translation_prompt.md 파일에서 프롬프트 로드"""
    prompt_file = os.path.join(os.path.dirname(__file__), 'translation_prompt.md')
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            start = content.find('```\n당신은') + 4
            end = content.find('\n```', start)
            if start > 3 and end > start:
                return content[start:end].strip()
    except Exception as e:
        print(f"⚠️  프롬프트 로드 실패: {e}")

    return """당신은 Polymarket 예측 시장 제목을 한국어로 번역하는 전문가입니다.

## 핵심 원칙

1. **반말 사용**: 모든 번역은 반말로 끝내야 합니다 (~할까?, ~될까?, ~인가?)
2. **날짜 한글화**: 월(Month)은 한글로 변환하되 일(Day)과 연도(Year)는 숫자 유지 (February 11 → 2월 11일)
3. **시간대 유지**: 시간대는 원문 그대로 유지 (2AM ET → 오전 2시 ET)
4. **간결성**: 원문의 뉘앙스를 유지하되 자연스러운 한국어로 변환
5. **일관성**: 같은 패턴은 같은 방식으로 번역

번역된 제목만 출력하세요. 번호와 함께 출력하세요."""

TRANSLATION_PROMPT = load_translation_prompt()


class DateRangeTranslator:
    def __init__(self):
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

        # 통계
        self.lock = threading.Lock()
        self.total_translated = 0
        self.total_batches = 0
        self.failed_batches = 0

    def get_total_count(self) -> int:
        """번역 대상 이벤트 총 개수 조회 (날짜 범위 필터)"""
        response = self.supabase.table('poly_events') \
            .select('id', count='exact') \
            .is_('title_ko', 'null') \
            .gte('end_date', START_DATE) \
            .lt('end_date', END_DATE) \
            .limit(1) \
            .execute()
        return response.count if response.count else 0

    def get_event_batch(self, offset: int, limit: int) -> List[Dict]:
        """이벤트 배치 조회 (날짜 범위 필터)"""
        response = self.supabase.table('poly_events') \
            .select('id, title, end_date') \
            .is_('title_ko', 'null') \
            .gte('end_date', START_DATE) \
            .lt('end_date', END_DATE) \
            .order('end_date') \
            .limit(limit) \
            .offset(offset) \
            .execute()
        return response.data

    def translate_batch(self, titles: List[str]) -> List[str]:
        """배치 번역"""
        if not titles:
            return []

        titles_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(titles)])
        request_text = f"{TRANSLATION_PROMPT}\n\n번역할 제목들:\n{titles_text}"

        for attempt in range(MAX_RETRIES):
            try:
                completion = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    max_tokens=5000,
                    temperature=0.3,
                    messages=[
                        {"role": "system", "content": "당신은 전문 번역가입니다. 반드시 반말로 번역하세요. 절대 존댓말(~할까요, ~될까요)을 사용하지 마세요. 반말(~할까, ~될까, ~인가)만 사용하세요."},
                        {"role": "user", "content": request_text}
                    ]
                )

                response_text = completion.choices[0].message.content.strip()

                # 🔧 개선된 파싱: 번호 기반으로 정확히 매칭
                translations = {}  # {번호: 번역}로 저장
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
                            translations[num] = translation  # 번호로 매칭
                        except (ValueError, IndexError):
                            continue

                # 번호 순서대로 정렬하여 리스트로 변환 + 용어 교정
                result = [apply_glossary_corrections(translations.get(i+1, titles[i])) for i in range(len(titles))]

                # 검증: 번역 개수가 원본과 다르면 경고
                if len(result) != len(titles):
                    print(f"  ⚠️  번역 개수 불일치: {len(result)} != {len(titles)}")
                    while len(result) < len(titles):
                        result.append(titles[len(result)])

                return result

            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                else:
                    print(f"  ❌ API 호출 실패: {e}")
                    return []

        return []

    def update_translations(self, event_ids: List[str], translations: List[str]) -> int:
        """번역 결과를 DB에 업데이트"""
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
        """단일 배치 처리"""
        try:
            batch_events = self.get_event_batch(offset, BATCH_SIZE)

            if not batch_events:
                return {'success': False, 'count': 0, 'reason': 'empty'}

            batch_titles = [e['title'] for e in batch_events]
            batch_ids = [e['id'] for e in batch_events]

            translations = self.translate_batch(batch_titles)

            if len(translations) != len(batch_titles):
                translations = translations[:len(batch_titles)]

            success = self.update_translations(batch_ids, translations)

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

    def run(self):
        """병렬 번역 실행"""
        print("\n🚀 2월 11일~15일 이벤트 번역 시작\n")
        print(f"📅 날짜 범위: {START_DATE} ~ {END_DATE}")
        print(f"⚙️  워커 수: {NUM_WORKERS}개")
        print(f"📦 배치 크기: {BATCH_SIZE}개\n")

        # 총 개수 확인
        total_count = self.get_total_count()
        total_batches_expected = (total_count + BATCH_SIZE - 1) // BATCH_SIZE

        print(f"📊 번역 대상: {total_count:,}개 이벤트")
        print(f"📦 예상 배치 수: {total_batches_expected}개")
        print(f"⏱️  예상 시간: ~{(total_batches_expected * 1.5 / NUM_WORKERS / 60):.1f}분\n")

        if total_count == 0:
            print("✅ 번역할 이벤트가 없습니다.")
            return

        start_time = time.time()

        # 배치 목록 생성
        batch_jobs = []
        for i in range(total_batches_expected):
            offset = i * BATCH_SIZE
            batch_jobs.append((i + 1, offset))

        # 병렬 처리
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            futures = {
                executor.submit(self.process_batch, batch_num, offset): (batch_num, offset)
                for batch_num, offset in batch_jobs
            }

            for future in as_completed(futures):
                result = future.result()

                if result['success']:
                    if result.get('reason') == 'empty':
                        continue

                    batch_num = result['batch_num']
                    count = result['count']
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

        # 완료
        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"🎉 번역 완료!")
        print(f"   총 {self.total_translated:,}개 이벤트 번역됨")
        print(f"   성공 배치: {self.total_batches}개")
        print(f"   실패 배치: {self.failed_batches}개")
        print(f"   소요 시간: {elapsed/60:.1f}분")
        print(f"   평균 속도: {self.total_translated/(elapsed/60):.0f}개/분")
        print(f"{'='*60}\n")


def main():
    """메인 함수"""
    translator = DateRangeTranslator()
    translator.run()


if __name__ == '__main__':
    main()
