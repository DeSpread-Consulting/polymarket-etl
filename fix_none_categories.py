"""
category가 None인 이벤트들을 재분류
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from main import infer_category_from_title


def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("category=None 이벤트 재분류 시작")
    print("=" * 80)

    # 환경 변수 로드
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL과 SUPABASE_KEY가 필요합니다.")

    client = create_client(supabase_url, supabase_key)
    print("✓ Supabase 연결 완료\n")

    # category가 None인 이벤트 조회
    print("category=None 이벤트 조회 중...")
    events = []
    batch_size = 1000
    offset = 0

    while True:
        result = client.table("poly_events")\
            .select("id, title, category")\
            .is_("category", "null")\
            .range(offset, offset + batch_size - 1)\
            .execute()

        if not result.data:
            break

        events.extend(result.data)
        offset += batch_size
        print(f"  {len(events)}개 조회됨...", end="\r")

        if len(result.data) < batch_size:
            break

    print(f"\n✓ {len(events)}개 이벤트 조회 완료\n")

    if len(events) == 0:
        print("category=None인 이벤트가 없습니다.")
        return

    # 재분류
    print("재분류 중...")
    updates_by_category = {
        'Sports': [],
        'Crypto': [],
        'Politics': [],
        'Finance': [],
        'Pop Culture': [],
        'Science': [],
        'Uncategorized': []
    }

    for event in events:
        new_category = infer_category_from_title(
            event.get('title', ''),
            None  # category가 None이므로
        )

        updates_by_category[new_category].append({
            'id': event['id'],
            'category': new_category
        })

    # 통계 출력
    print("\n재분류 결과:")
    print("-" * 80)
    for category, updates in updates_by_category.items():
        count = len(updates)
        if count > 0:
            print(f"  {category}: {count}개")

    total_updates = sum(len(updates) for updates in updates_by_category.values())
    print("-" * 80)
    print(f"✓ 총 {total_updates}개 업데이트 예정\n")

    # 업데이트 실행
    print("Supabase에 업데이트 중...")
    updated_count = 0

    for category, updates in updates_by_category.items():
        if not updates:
            continue

        # 배치 단위로 업데이트
        batch_size = 100
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            try:
                for update in batch:
                    client.table("poly_events")\
                        .update({"category": update['category']})\
                        .eq("id", update['id'])\
                        .execute()
                    updated_count += 1

                print(f"  {updated_count}/{total_updates} 업데이트됨...", end="\r")
            except Exception as e:
                print(f"\n  오류 발생: {e}")
                continue

    print(f"\n\n✓ {updated_count}개 이벤트 업데이트 완료!")
    print("=" * 80)
    print("재분류 완료")
    print("=" * 80)


if __name__ == "__main__":
    main()
