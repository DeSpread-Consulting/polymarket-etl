"""
'기타' 카테고리의 상세 분석
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

print("Uncategorized 이벤트 조회 중...\n")

# 전체 Uncategorized 이벤트 조회
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

# 이미 분류된 패턴 필터링
misc_events = []
for event in events:
    title = event.get("title", "").lower()

    # 이미 분류된 패턴은 제외
    if ('elon' in title and ('tweet' in title or 'post' in title)):
        continue
    if ('temperature' in title or 'celsius' in title or 'fahrenheit' in title or '°c' in title or '°f' in title):
        continue
    if ('trade deal' in title or 'trade agreement' in title):
        continue
    if ('nuclear' in title or 'strike' in title or 'military' in title or 'iran' in title or 'russia' in title):
        continue
    if any(crypto in title for crypto in ['bitcoin', 'btc', 'ethereum', 'eth', 'hyperliquid', 'solana', 'xrp', 'cardano', 'doge']):
        continue
    if ('silver' in title or 'gold' in title or any(word in title for word in ['stock', 'nasdaq', 'dow', 's&p'])):
        continue
    if ('released' in title or 'launch' in title or 'grok' in title):
        continue
    if any(word in title for word in ['rebounds', 'assists', 'points', 'rounds', 'over/under', 'spread']):
        continue
    if ('debt' in title or 'trillion' in title):
        continue

    misc_events.append(event)

print("="*80)
print(f"\n기타 이벤트 수: {len(misc_events)}개\n")

# 샘플 100개 출력
print("[샘플 100개]\n")
for i, event in enumerate(misc_events[:100], 1):
    print(f"{i}. {event.get('title', '')}")

# 키워드 빈도 분석
print("\n" + "="*80)
print("\n[기타 카테고리 키워드 Top 50]\n")

all_words = []
for event in misc_events:
    title = event.get("title", "").lower()
    words = re.findall(r'\b[a-z]{2,}\b', title)
    all_words.extend(words)

stopwords = {'will', 'the', 'be', 'to', 'in', 'of', 'on', 'at', 'for', 'by', 'and', 'or', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'do', 'does', 'did', 'from', 'with', 'as', 'an', 'a', 'that', 'this', 'it', 'than', 'more', 'before', 'after', 'their', 'his', 'her'}

filtered_words = [w for w in all_words if w not in stopwords]
word_counts = Counter(filtered_words)

for word, count in word_counts.most_common(50):
    print(f"{word}: {count}회")

print("\n" + "="*80)
print("\n완료")
