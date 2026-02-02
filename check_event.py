"""
특정 이벤트 확인
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL과 SUPABASE_KEY가 필요합니다.")

client = create_client(supabase_url, supabase_key)

# Lorenzo Musetti vs Novak Djokovic 검색
result = client.table("poly_events")\
    .select("*")\
    .ilike("title", "%musetti%djokovic%")\
    .execute()

print(f"검색 결과: {len(result.data)}개\n")

for event in result.data:
    print("="*80)
    print(f"제목: {event.get('title')}")
    print(f"카테고리: {event.get('category')}")
    print(f"Closed: {event.get('closed')}")
    print(f"End Date: {event.get('end_date')}")
    print(f"ID: {event.get('id')}")
    print("="*80)
