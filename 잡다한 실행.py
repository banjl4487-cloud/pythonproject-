import pandas as pd

# ====================================================================
# 🚨🚨🚨 초 강력하게 중요!!! 파일 경로를 네 환경에 맞게 '초 정확하게' 수정하세요! 🚨🚨🚨
# 네가 이전에 알려줬던 경로 예시: r'D:\PythonProject 1\TFT_Item_CurrentVersion.csv'
# ====================================================================
ITEM_FILE_PATH = r'D:\PythonProject 1\TFT_Item_CurrentVersion.csv'
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# 위에 `ITEM_FILE_PATH` 변수 안에 '초 정확한 절대 경로'를 넣어주세요!
# 복사한 경로가 r'C:\Users\Juhyun\MyProject\data\TFT_Item_CurrentVersion.csv' 라면
# ITEM_FILE_PATH = r'C:\Users\Juhyun\MyProject\data\TFT_Item_CurrentVersion.csv' 이렇게!
# ====================================================================


# --- Step 1: df_item 데이터 로드 ---
try:
    df_item = pd.read_csv(ITEM_FILE_PATH)
    print("✅ `df_item` 데이터 로드 '초 성공'!")
except FileNotFoundError:
    print(f"❌ 에러: 지정된 경로에서 파일 '{ITEM_FILE_PATH}'을(를) 찾을 수 없습니다!")
    print("   👉 파일 경로 `ITEM_FILE_PATH` 변수를 '초 확실하게' 다시 확인하고 수정해주세요!")
    # 파일 로드 실패 시, 빈 DataFrame 생성하여 에러를 막고 메시지 출력
    df_item = pd.DataFrame(columns=['id', 'name'])
except Exception as e:
    print(f"❌ 에러: 파일을 로드하는 중 예상치 못한 오류 발생: {e}")
    df_item = pd.DataFrame(columns=['id', 'name'])


# --- Step 2: '거인의 결의' 아이템 검색 ---
if not df_item.empty:  # df_item이 비어있지 않을 때만 검색
    print("\n--- ✅ '거인의 결의' 또는 'Titan\'s Resolve' 아이템 검색 시작 ---")

    # '거인의 결의' (한글) 또는 'Titan\'s Resolve' (영어) 키워드를 포함하는 아이템 검색
    # 'name' 컬럼이 문자열이 아닐 경우를 대비해 `.astype(str)` 추가
    # `case=False`는 대소문자 무시, `na=False`는 NaN 값 있을 때 에러 방지
    found_resolve_items = df_item[
        df_item['name'].astype(str).str.contains("거인의 결의", case=False, na=False) |
        df_item['name'].astype(str).str.contains("Titan's Resolve", case=False, na=False)
        ].copy()

    if not found_resolve_items.empty:
        print(f"✅ `df_item`에서 '거인의 결의' 또는 'Titan\'s Resolve' 관련 아이템을 '초 확실하게' 다 조져서 발견했습니다!")
        print("   --- 발견된 아이템 목록 ---")
        for index, row in found_resolve_items.iterrows():
            print(f"   - ID: {row['id']}, 이름: {row['name']}")
    else:
        print(f"❌ `df_item`에서 '거인의 결의' 또는 'Titan\'s Resolve' 관련 아이템을 '초 코딱지만큼도' 찾을 수 없습니다.")

    print("\n✅ '거인의 결의' 아이템 존재 여부 검색 완료!")
else:
    print("\n--- ⚠️ `df_item`이 로드되지 않아 아이템 검색을 수행할 수 없습니다. 파일 경로를 확인해주세요! ---")