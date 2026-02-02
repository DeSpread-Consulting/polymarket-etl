"""
Supabase에 저장된 모든 Uncategorized 이벤트를 새 로직으로 재분류
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from main import infer_category_from_title


def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("Uncategorized 이벤트 재분류 시작")
    print("=" * 80)

    # 환경 변수 로드
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL과 SUPABASE_KEY가 필요합니다.")

    client = create_client(supabase_url, supabase_key)
    print("✓ Supabase 연결 완료\n")

    # Uncategorized 이벤트 조회
    print("Uncategorized 이벤트 조회 중...")
    events = []
    batch_size = 1000
    offset = 0

    while True:
        result = client.table("poly_events")\
            .select("id, title, category")\
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

    print(f"\n✓ {len(events)}개 이벤트 조회 완료\n")

    # 재분류
    print("재분류 중...")
    updates_by_category = {
        'Sports': [],
        'Crypto': [],
        'Politics': [],
        'Finance': [],
        'Pop Culture': [],
        'Science': []
    }

    for event in events:
        new_category = infer_category_from_title(
            event.get('title', ''),
            event.get('category')
        )

        if new_category != 'Uncategorized':
            updates_by_category[new_category].append({
                'id': event['id'],
                'category': new_category
            })

    # 통계 출력
    print("\n재분류 결과:")
    print("-" * 80)
    total_reclassified = 0
    for category, updates in updates_by_category.items():
        count = len(updates)
        total_reclassified += count
        if count > 0:
            print(f"  {category}: {count}개")

    remaining = len(events) - total_reclassified
    print(f"  Uncategorized (남음): {remaining}개")
    print("-" * 80)
    print(f"✓ 총 {total_reclassified}개 재분류 예정\n")

    # 업데이트 실행
    if total_reclassified == 0:
        print("재분류할 항목이 없습니다.")
        return

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

                print(f"  {updated_count}/{total_reclassified} 업데이트됨...", end="\r")
            except Exception as e:
                print(f"\n  오류 발생: {e}")
                continue

    print(f"\n\n✓ {updated_count}개 이벤트 업데이트 완료!")
    print("=" * 80)
    print("재분류 완료")
    print("=" * 80)


if __name__ == "__main__":
    main()
