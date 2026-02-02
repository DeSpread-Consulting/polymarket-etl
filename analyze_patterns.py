"""
Uncategorized 이벤트의 패턴을 더 상세히 분석
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from collections import defaultdict
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
print("="*80)

# 패턴별 그룹화
patterns = {
    'Elon Musk 트윗': [],
    '날씨/온도': [],
    '무역 협정': [],
    '군사/핵': [],
    '암호화폐 가격': [],
    '주식/상품 가격': [],
    '제품 출시': [],
    '스포츠 통계': [],
    '국채/경제': [],
    '기타': []
}

for event in events:
    title = event.get("title", "").lower()

    if 'elon' in title and ('tweet' in title or 'post' in title):
        patterns['Elon Musk 트윗'].append(event['title'])
    elif 'temperature' in title or 'celsius' in title or 'fahrenheit' in title or '°c' in title or '°f' in title:
        patterns['날씨/온도'].append(event['title'])
    elif 'trade deal' in title or 'trade agreement' in title:
        patterns['무역 협정'].append(event['title'])
    elif 'nuclear' in title or 'strike' in title or 'military' in title or 'iran' in title or 'russia' in title:
        patterns['군사/핵'].append(event['title'])
    elif any(crypto in title for crypto in ['bitcoin', 'btc', 'ethereum', 'eth', 'hyperliquid', 'solana', 'xrp', 'cardano', 'doge']):
        patterns['암호화폐 가격'].append(event['title'])
    elif 'silver' in title or 'gold' in title or any(word in title for word in ['stock', 'nasdaq', 'dow', 's&p']):
        patterns['주식/상품 가격'].append(event['title'])
    elif 'released' in title or 'launch' in title or 'grok' in title:
        patterns['제품 출시'].append(event['title'])
    elif any(word in title for word in ['rebounds', 'assists', 'points', 'rounds', 'over/under', 'spread']):
        patterns['스포츠 통계'].append(event['title'])
    elif 'debt' in title or 'trillion' in title or 'gdp' in title:
        patterns['국채/경제'].append(event['title'])
    else:
        patterns['기타'].append(event['title'])

# 패턴별 통계 출력
print("\n[패턴별 분류 결과]\n")
for pattern, titles in patterns.items():
    count = len(titles)
    if count > 0:
        print(f"\n{pattern}: {count}개")
        print("-" * 80)
        # 각 패턴의 샘플 5개 출력
        for i, title in enumerate(titles[:5], 1):
            print(f"  {i}. {title}")
        if count > 5:
            print(f"  ... 외 {count - 5}개")

print("\n" + "="*80)
print("\n완료")
