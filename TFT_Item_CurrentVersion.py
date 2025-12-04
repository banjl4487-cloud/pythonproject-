import pandas as pd

# --------------------------------------------------------------------------
# --- '초 필사적인 0단계: TFT_Item_CurrentVersion.csv' 파일 로드 ---
# 'id', 'name' 컬럼을 포함하는 원본 아이템 데이터 파일!
df_item = pd.read_csv('TFT_Item_CurrentVersion.csv')

# --- [디버그] 이 파일에 'id'와 'name' 컬럼이 정확히 존재하는지 확인!
# print(df_item.head())
# print("-" * 50)


# --------------------------------------------------------------------------
# --- '초 필사적인 1단계: 아이템 타입 ('item_type') 분류를 위한 기본 아이템 리스트 정의 ---
# '초 강력하게 "기본 아이템(Component Items)"' 이름들을 여기에 '초 깔끔하게 빠짐없이' 입력해야 해!
# TFT 공식 영어 아이템명과 대소문자, 띄어쓰기까지 정확히 일치해야 한다!
component_items = [
    "B.F. Sword", "Recurve Bow", "Needlessly Large Rod", "Tear of the Goddess",
    "Chain Vest", "Negatron Cloak", "Giant's Belt", "Spatula", "Sparring Gloves" # Sparring Gloves도 component로!
    # ... '초 필사적인 네가 아는 모든 기본 아이템' 이름들을 여기에 정확히 추가!
]

# '초 필사적인 classify_item 함수'를 사용해서 'item_type' 컬럼 생성
def classify_item(item_name_str):
    if item_name_str in component_items:
        return 'component'
    return 'completed' # 기본 아이템이 아니면 'completed'로 간주!

df_item['item_type'] = df_item['name'].apply(classify_item)


# --------------------------------------------------------------------------
# --- '초 필사적인 2단계: 방어 아이템 ('is_defensive') 분류를 위한 방템 리스트 정의 ---
# '초 강력한 네 기준에 따른 방템 (TFT 공식 영어 이름)' 리스트!
# 이 부분도 '수동 정의'가 필요하며, 'TFT 공식 명칭'과 '초 필사적인 대소문자, 띄어쓰기'가 정확히 일치해야 해!
defensive_items = [
    "Guardian Angel",          # 수호천사
    "Titan's Resolve",         # 거인의 결의
    "Locket of the Iron Solari", # 강철의 솔라리 팬던트
    "Frozen Heart",            # 얼어붙은 심장
    "Redemption",              # 구원
    "Warmog's Armor",          # 워모그의 갑옷
    "Trap Claw",               # 덫 발톱
    "Bramble Vest",            # 덤불 조끼 (Chain Vest와 Negatron Cloak 합성 아이템)
    "Dragon's Claw",           # 용의 발톱
    "Quicksilver",             # 수은
    "Zephyr",                  # 기병대 전투훈련 (바람의 징표) - 유틸성 방템
    # ... '초 필사적인 네가 정의하는 모든 방어 아이템' 이름들을 여기에 정확히 추가!
]

df_item['is_defensive'] = df_item['name'].isin(defensive_items)


# --------------------------------------------------------------------------
# --- '초 필사적인 3단계: 통합 분류 완료된 df_item을 새로운 CSV 파일로 저장 ---
output_categorized_filename = 'TFT_Item_Categorized_Version.csv'
df_item.to_csv(output_categorized_filename, index=False)

# --- [정보] 파일 저장 확인 (실행 시 원하는 경우 주석 해제)
# print(f"\n--- [정보] 통합 분류 완료된 '{output_categorized_filename}' 파일 저장 완료! ---")
# print("-" * 50)