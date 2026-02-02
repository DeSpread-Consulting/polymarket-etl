"""
Uncategorized 이벤트 조회 및 분석
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from collections import Counter
import re

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL과 SUPABASE_KEY가 필요합니다.")

client = create_client(supabase_url, supabase_key)

# 전체 Uncategorized 이벤트 개수 조회
count_result = client.table("poly_events")\
    .select("*", count="exact")\
    .eq("category", "Uncategorized")\
    .limit(1)\
    .execute()

total_count = count_result.count

print(f"총 {total_count}개의 Uncategorized 이벤트 발견")
print(f"전체 데이터 조회 중...\n")

# 전체 Uncategorized 이벤트 조회 (페이지네이션)
events = []
batch_size = 1000
offset = 0

while True:
    result = client.table("poly_events")\
        .select("id, title, category, tags")\
        .eq("category", "Uncategorized")\
        .range(offset, offset + batch_size - 1)\
        .execute()

    if not result.data:
        break

    events.extend(result.data)
    offset += batch_size
    print(f"  {len(events)}개 조회됨...", end="\r")

    if len(result.data) < batch_size:
        break

print(f"\n조회 완료: {len(events)}개\n")
print("="*80)

# 제목 샘플 출력
print("\n[샘플 제목 20개]")
for i, event in enumerate(events[:20], 1):
    title = event.get("title", "")
    tags = event.get("tags", [])
    print(f"{i}. {title}")
    if tags:
        print(f"   Tags: {tags}")

# 공통 키워드 추출
print("\n" + "="*80)
print("\n[제목에서 자주 등장하는 단어 Top 30]")

# 모든 제목을 합쳐서 단어 추출
all_words = []
for event in events:
    title = event.get("title", "").lower()
    # 단어 추출 (2글자 이상)
    words = re.findall(r'\b[a-z]{2,}\b', title)
    all_words.extend(words)

# 불용어 제거
stopwords = {'will', 'the', 'be', 'to', 'in', 'of', 'on', 'at', 'for', 'by', 'and', 'or', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'do', 'does', 'did', 'from', 'with', 'as', 'an', 'a', 'that', 'this', 'it', 'than', 'more', 'before', 'after', 'their', 'his', 'her'}

filtered_words = [w for w in all_words if w not in stopwords]

word_counts = Counter(filtered_words)

for word, count in word_counts.most_common(30):
    print(f"{word}: {count}회")

print("\n" + "="*80)
print("\n완료")
