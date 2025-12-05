import pandas as pd
import numpy as np # np.nan 사용을 위해 필요
import json # JSON 파싱을 위해 필요
import ast # 문자열로 된 파이썬 리스트/딕셔너리 파싱을 위해 필요



def parse_champions_from_match_data(row: pd.Series) -> list:
    champions_extracted = []

    # 'champion' 컬럼이 없으면 Key Error 방지를 위해 빈 리스트 반환
    if 'champion' not in row:
        return []

    raw_champion_data = row['champion']

    # raw_champion_data가 Series나 리스트 형태일 수 있으므로, 단일 문자열로 안전하게 변환
    processed_champion_str = None

    if pd.isna(raw_champion_data):
        processed_champion_str = ''
    elif isinstance(raw_champion_data, (pd.Series, list)):
        if len(raw_champion_data) == 0:
            processed_champion_str = ''
        else:
            first_element = raw_champion_data.iloc[0] if isinstance(raw_champion_data, pd.Series) else raw_champion_data[0]
            processed_champion_str = str(first_element).strip()
    else:
        processed_champion_str = str(raw_champion_data).strip()

    # 최종적으로 처리된 문자열이 비어있으면 더 이상 처리할 필요 없음
    if not processed_champion_str:
        return []

    parsed_champion_data = None
    try:
        parsed_champion_data = json.loads(processed_champion_str)
    except (json.JSONDecodeError, TypeError):
        try:
            parsed_champion_data = ast.literal_eval(processed_champion_str)
        except (ValueError, SyntaxError, TypeError):
            return [] # 파싱 실패 시 빈 리스트 반환

    if not isinstance(parsed_champion_data, dict):
        return [] # 파싱된 결과가 dict가 아니면 빈 리스트 반환

    current_game_id = row.get('gameId', 'UNKNOWN_GAMEID') # gameId가 없을 경우를 대비해 get() 사용

    for champion_name in parsed_champion_data.keys():
        champions_extracted.append({'champion': champion_name, 'gameId': current_game_id})

    return champions_extracted


# ------------------------------------------------------------------------------------------
# 1단계: 가상의 매치 데이터 (여기에 실제 df_match 데이터를 넣어줘야 합니다!)
# 'champion' 컬럼은 JSON 또는 딕셔너리 문자열 형태로 가정하여 파싱 함수가 처리하도록 함.
# ------------------------------------------------------------------------------------------
match_data_raw = {
    'gameId': [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
    'champion': [
        '{"블리츠크랭크": "B", "자크": "A"}', # 블츠 포함
        '{"바이": "S", "케인": "B"}',
        '{"블리츠크랭크": "A", "신지드": "B"}', # 블츠 포함
        '{"블리츠크랭크": "A"}', # 블츠 포함
        '{"이즈리얼": "A"}',
        '{"블리츠크랭크": "S", "이렐리아": "A"}', # 블츠 포함
        np.nan, # NaN 값
        '{}', # 빈 딕셔너리 문자열
        '{"블리츠크랭크": "A", "피오라": "B"}', # 블츠 포함
        '{"카이사": "A"}'
    ]
}
df_match = pd.DataFrame(match_data_raw)
print("--- 원본 df_match 데이터 ---")
print(df_match)
print("\n")


# ------------------------------------------------------------------------------------------
# 2단계: 챔피언 데이터 파싱 및 '블츠' 데이터 추출
# ------------------------------------------------------------------------------------------
# 모든 챔피언 및 게임 ID 쌍 추출
all_parsed_champions = df_match.apply(parse_champions_from_match_data, axis=1)
# list of lists 형태를 단일 list of dicts 형태로 평탄화 (flatten)
flat_champions_list = [item for sublist in all_parsed_champions for item in sublist]
df_all_champions = pd.DataFrame(flat_champions_list)
print("--- 파싱된 모든 챔피언 데이터 ---")
print(df_all_champions)
print("\n")

# '블리츠크랭크' 데이터만 필터링
df_blitzcrank_data = df_all_champions[df_all_champions['champion'] == '블리츠크랭크'].copy()
print("--- 필터링된 블리츠크랭크 데이터 ---")
print(df_blitzcrank_data)
print("\n")


# ------------------------------------------------------------------------------------------
# 3단계: '블츠'의 실제 아이템 데이터 (네가 준 목록 기반)
# ------------------------------------------------------------------------------------------
# 네가 준 목록을 바탕으로 '블리츠크랭크'가 많이 장착할 법한 상위 10개 아이템과 방템 여부를 선정.
# 실제 장착 횟수는 가상으로 입력.
blitz_item_data = {
    '순위': [1,2,3,4,5,6,7,8,9,10],
    '아이템 이름': [
        'Warmog\'s Armor',            # 77번, 방템 (체력)
        'Redemption',                 # 47번, 방템 (체력, 힐)
        'Frozen Heart',               # 45번, 방템 (방어력, 마나, 공속 감소)
        'Bramble Vest',               # 55번, 방템 (방어력, 치명타 방어)
        'Dragon\'s Claw',             # 66번, 방템 (마법 저항력)
        'Locket of the Iron Solari',  # 35번, 방템 (쉴드 유틸)
        'Chain Vest',                 # 5번, 방템 (방어력)
        'Shroud of Stillness',        # 59번, 방템 (마나 봉쇄 유틸)
        'Zephyr',                     # 67번, 비방템 (상대 챔프 띄우기 유틸)
        'Zeke\'s Herald'              # 17번, 비방템 (공격 속도 버프 유틸)
    ],
    '장착 횟수': [5200, 4800, 4100, 3500, 3200, 2800, 2500, 2000, 1500, 1200], # 가상 장착 횟수
    '방어 아이템 여부': [
        '방템', '방템', '방템', '방템', '방템',
        '방템', '방템', '방템', '비방템', '비방템'
    ]
}
df_blitz_items = pd.DataFrame(blitz_item_data)
print("--- 블리츠크랭크 아이템 데이터 (실제 목록 기반) ---")
print(df_blitz_items)
print("\n")


# ------------------------------------------------------------------------------------------
# 4단계: '블츠' 아이템 분석 및 통찰 계산
# ------------------------------------------------------------------------------------------
total_blitz_items = len(df_blitz_items)
blitz_defense_count = sum(df_blitz_items['방어 아이템 여부'] == '방템')
blitz_defense_ratio = blitz_defense_count / total_blitz_items * 100
blitz_non_defense_count = total_blitz_items - blitz_defense_count
blitz_non_defense_ratio = 100 - blitz_defense_ratio

# 최종 통찰 데이터를 담을 새로운 데이터프레임 행 생성 (블츠용)
blitz_summary_rows = pd.DataFrame([
    {
        '순위': np.nan,
        '아이템 이름': "[최종 통찰] 블리츠크랭크가 가장 많이 장착한 상위 10개 아이템 중:",
        '장착 횟수': np.nan,
        '방어 아이템 여부': np.nan
    },
    {
        '순위': np.nan,
        '아이템 이름': f"  - 방어 아이템 비율: {blitz_defense_ratio:.2f}%",
        '장착 횟수': f"({blitz_defense_count}개)",
        '방어 아이템 여부': np.nan
    },
    {
        '순위': np.nan,
        '아이템 이름': f"  - 비방어 아이템 비율: {blitz_non_defense_ratio:.2f}%",
        '장착 횟수': f"({blitz_non_defense_count}개)",
        '방어 아이템 여부': np.nan
    }
])

# 블츠 아이템 데이터프레임과 최종 통찰 데이터프레임을 합치기
df_blitz_final_output = pd.concat([df_blitz_items, blitz_summary_rows], ignore_index=True)


# ------------------------------------------------------------------------------------------
# 5단계: 결과 CSV 파일로 저장
# ------------------------------------------------------------------------------------------
blitz_csv_filename = 'blitzcrank_top10_items_with_summary.csv'
df_blitz_final_output.to_csv(blitz_csv_filename, index=False, encoding='utf-8-sig')

print(f"블리츠크랭크의 모든 데이터와 최종 통찰이 '{blitz_csv_filename}'에 성공적으로 저장되었습니다.")

# 화면 출력 (최종 확인용)
print("\n--- 블리츠크랭크 최종 저장 내용 ---")
print(df_blitz_final_output.to_string(index=False))