import pandas as pd
import json
import ast # json.loads 실패 시 문자열 딕셔너리를 파싱하기 위함

# --- 0단계: 모든 데이터 불러오기 (파일 경로 확인) ---
# 네가 저장한 .csv 파일들의 정확한 경로와 파일명을 입력
# 예시: 'C:/PythonProject/TFT_Challenger_MatchData.csv'
file_path_match = 'TFT_Challenger_MatchData.csv'
file_path_item = 'TFT_Item_CurrentVersion.csv'
file_path_champion_info = 'TFT_Champion_CurrentVersion.csv' # 이 파일도 '.csv'겠지


try:
    df_match = pd.read_csv(file_path_match)
    df_item = pd.read_csv(file_path_item)
    df_champion_info = pd.read_csv(file_path_champion_info)
    print("✅ 모든 데이터 불러오기 성공!")
except FileNotFoundError as e:
    print(f"❌ 오류: 파일 '{e.filename}'을(를) 찾을 수 없습니다. 파일 경로와 이름을 다시 확인해라!")
    exit() # 파일 없으면 더 진행할 필요 없음
except Exception as e:
    print(f"❌ 데이터 불러오기 중 알 수 없는 오류 발생: {e}")
    exit()

# --- 1단계: 'df_match'의 'champion' 컬럼 펼치기!!! (핵심!!!) ---
# 'champion' 컬럼이 문자열 형태의 JSON/딕셔너리인지 확인하고 변환하는 로직
# 이 데이터 샘플은 딕셔너리 형태, json.loads 또는 ast.literal_eval 이 필요
# 어떤 방식으로 들어있는지 직접 확인해보고 적절한 걸 써야됨
# 일단은 json.loads를 먼저 시도하고, 실패하면 ast.literal_eval을 시도하도록 한다.
# 오류 (예외 검출 코드) 출력이 없는 이유는 1번 2번은 별거 아닌 예외
def parse_champion_data(champ_str):
    if pd.isna(champ_str): # NaN 값 처리
        return {}
    try:
        return json.loads(champ_str)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(champ_str)
        except (ValueError, SyntaxError) as e:
            print(f"⚠️ 경고: 챔피언 데이터 파싱 실패: {champ_str}, 오류: {e}")
            return {}
    except Exception as e:
        print(f"⚠️ 경고: 예상치 못한 챔피언 데이터 파싱 오류: {champ_str}, 오류: {e}")
        return {}
# 챔피언 항목에있는 미지의 어떠한 것을 다 파악하여 새로운 chamion_parsed에 저장
df_match['champion_parsed'] = df_match['champion'].apply(parse_champion_data)
print("\n✅ 'champion' 컬럼 파싱 완료!")

# 1-1. 'champion_parsed' 컬럼의 챔피언 딕셔너리를 '펼쳐서' 각 챔피언을 독립된 행으로 만듬
#      'gameId' (경기를 구분하는 고유 ID)를 기준으로 다른 매치 정보들을 함께 가져와야 함
expanded_records = [] # 이 변수는 데이터를 임시 저장하는 리스트
# c언어의 배열 처럼 행과 열을 가지고 반복 그러나 C언어 처럼 종료에 대한 조건은 없음 (자동종료)
# 만약 밑에 있는 것처럼 일일히 뭘 뽑는것이다 설명을 달아버리면 반대의 경우가 생김
for index, row in df_match.iterrows():
    game_id = row['gameId']
    game_duration = row['gameDuration']
    level = row['level'] # 필요한 모든 매치 관련 정보들을 가져와라!
    last_round = row['lastRound']
    ranked_status = row['Ranked']
    ingame_duration = row['ingameDuration']

    # index를 안쓰는 이유: index를 써버리면 지금 작성하는 사람은 이해가 되지만 보는 사람들은 "이게 뭐지 궁금증" 이게 뭘 뽑는거인지 확실하게 인지
    for champ_name, champ_detail in row['champion_parsed'].items():
        expanded_records.append({
            'gameId': game_id, # 원본 데이터를 가공하여 생성된 개별 레코드들을 수집할 리스트 초기화
            'gameDuration': game_duration,
            'level': level,
            'lastRound': last_round,
            'Ranked': ranked_status,
            'ingameDuration': ingame_duration,
            'champion_name': champ_name,
            'champion_items_list': champ_detail.get('items', []), # 챔피언이 장착한 아이템 ID 리스트
            'champion_star': champ_detail.get('star', 0) # 챔피언 성급
        })

df_champions_exploded = pd.DataFrame(expanded_records)
print("✅ 각 게임의 챔피언 데이터 행으로 펼치기 완료!")
print(df_champions_exploded.head())

# --- 2단계: 아이템 목록도 'explode'해서 각 아이템을 독립된 행으로 만들고, 아이템 정보를 합침 ---
# 챔피언 한 명이 여러 아이템을 가질 수 있으니, 아이템 리스트도 펼쳐야 한다!
# 아이템이 없는 경우는 어떻게 할지 (NaN으로 둘지, 제외할지) 생각해라. 일단 NaN으로 둔다!
# NaN으로 놔두는 이유: 1. 바이가 아이템을 안샀다고 해서 쓸모없는 데이터가 아닐 수도 있다 2. 유연성 생성 3. 바이어스 방지
df_final_detail = df_champions_exploded.explode('champion_items_list')
# 컬럼명을 바꾸는 이유, 아이템을 각자 펼쳤으니 이제 이것은 list가 아니다 라는것을 컴퓨터에다가 알려주기 위함
df_final_detail.rename(columns={'champion_items_list': 'item_id'}, inplace=True)
print("\n✅ 챔피언별 아이템 리스트 행으로 펼치기 완료!")
print(df_final_detail.head())


# --- 3단계: 이제 다른 데이터프레임들과 'merge'해서 하나의 메가 테이블을 만들었음---
# 3-1. 챔피언별 아이템 데이터와 'df_item' 합치기
# item_id가 NaN인 경우를 대비해서 'how='left''를 쓴다.
# 모든 최종 상세 데이터(df_final_detail)를 유지하며 아이템 정보를 매칭하기 위함
# item_id가 없는 레코드도 보존하여 누락된 아이템 분석에 활용할 계획
# (주의) 다른 join 방식 사용 시 데이터 손실 발생 가능
                               how='left', suffixes=('_champ', '_item_info')
merged_with_item_df = pd.merge(df_final_detail, df_item)
                               left_on='item_id', right_on='id'

print("\n✅ df_item과 합치기 완료!")
print(merged_with_item_df.head())


# 3-2. 'merged_with_item_df'와 'df_champion_info' 합치기 (챔피언의 코스트/속성 정보!)
# 'champion_name' 컬럼에 있는 이름으로 합친다.
# 이 챔피언 정보 데이터에는 'name', 'cost', 'origin', 'class' 등이 있을 거다.
final_mega_df = pd.merge(merged_with_item_df, df_champion_info,
                         left_on='champion_name', right_on='name',
                         how='left', suffixes=('_base', '_champ_info'))
print("\n✅ 최종 챔피언 정보까지 합치기 완료! 이제 '메가 테이블'이다!!!!")
print(final_mega_df.head())
final_mega_df.info()

# --- 최종적으로 '메가 테이블' 저장해 놓는 것도 좋다!!! ---
# 다음에 다시 불러와서 쓸 수 있게!
# final_mega_df.to_csv('processed_tft_mega_data.csv', index=False)
# print("\n✅ 최종 메가 테이블 'processed_tft_mega_data.csv'로 저장 완료!")

final_mega_df.to_csv('processed_tft_mega_data.csv', index=False)
print("\n✅ 최종 메가 테이블 'processed_tft_mega_data.csv'로 저장 완료!")

# --- [설정] 최종 데이터 저장 여부 플래그 ---
# 이 플래그(Flag)를 통해 최종 결과물인 'final_mega_df'를 CSV 파일로 저장할지 여부를 제어합니다.
# 개발 및 테스트 중에는 'False'로 설정하여 빠른 코드 실행 및 불필요한 파일 생성을 방지하고,
# 최종 결과물 도출 및 공유 시에는 'True'로 설정하여 유연하게 활용할 수 있습니다.
# 이는 단순히 주석 처리하는 것보다 코드의 의도를 명확히 하고, 유지보수 및 확장성을 높이는 방법입니다.
SHOULD_SAVE_TO_FILE = False

# --- 4단계: '바이' 챔피언 데이터만 필터링 ---
# 'final_mega_df'에서 'champion_name'이 '바이'인 레코드들만 추출하여
# 'df_vi_data'라는 새로운 데이터프레임에 저장합니다.
# 이를 통해 '바이' 챔피언에 특화된 분석을 집중적으로 수행할 기반을 마련합니다.
df_vi_data = final_mega_df[final_mega_df['champion_name'] == '바이']

print("\n✅ '바이' 챔피언 데이터 필터링 완료!")
print(df_vi_data.head()) # '바이' 데이터의 상위 5행을 확인합니다.
print(f"\n총 '바이' 챔피언 데이터 수: {len(df_vi_data)}개") # 필터링된 데이터의 총 개수를 확인합니다.

# DEFENSIVE_VI_ITEMS: TFT 시즌 3 메타에서 바이 챔피언의 방어적 역할 수행에 핵심적인 아이템 목록입니다.
# 각 아이템은 단순히 방어력, 마법 저항력 증가 외에도 체력, 생존기, 아군 보호 등 탱커 챔피언의 역할을
# 강화하는 기능들을 고려하여 선정되었습니다.
DEFENSIVE_VI_ITEMS = [
    '수호천사',                 # 생존력 증대에 직접 기여하는 아이템 (부활)
    '거인의 결의',               # 전투 지속력(탱킹)을 높이는 스탯 증가 아이템
    '덤불조끼',                 # 방어력 및 치명타 피해 감소를 제공하는 탱커 핵심 아이템
    '용의 발톱',                 # 마법 저항력 및 마법 피해 감소를 위한 핵심 아이템
    '강철의 솔라리 펜던트',     # 주변 아군 보호막 제공을 통한 아군 생존력 향상 (탱커가 주로 사용)
    '얼어붙은 심장',             # 방어력 제공과 함께 적의 공격 속도를 감소시켜 탱킹력 증대
    '구원',                     # 아군 체력 회복을 통한 전투 유지력 기여 (탱커의 아군 지원 아이템)
    '워모그의 갑옷'             # 높은 체력 재생으로 장기적인 생존력을 확보하는 핵심 탱킹 아이템
]

print(f"\n✅ 분석을 위한 바이 방어 아이템 목록 정의 완료 (총 {len(DEFENSIVE_VI_ITEMS)}개):")
for item in DEFENSIVE_VI_ITEMS:
    print(f"- {item}")

# df_vi_data에 'has_defensive_item' 컬럼을 추가합니다.
# 'item_name_item_info' 컬럼의 아이템 이름이 DEFENSIVE_VI_ITEMS 리스트에 포함되는지 확인하여 True/False를 반환합니다.
# 이를 통해 방어 아이템 장착 여부를 명확하게 구분할 수 있습니다.
df_vi_data['has_defensive_item'] = df_vi_data['item_name_item_info'].isin(DEFENSIVE_VI_ITEMS)

print("\n✅ 'has_defensive_item' 컬럼 추가 완료:")
# 새로 추가된 컬럼과 함께 주요 관련 컬럼들을 출력하여 변화를 확인합니다.
print(df_vi_data[['champion_name', 'item_name_item_info', 'has_defensive_item', 'lastRound']].head(10))

# 각 그룹의 데이터 수를 확인하여 그룹 분류의 현황을 파악합니다.
print(f"\n- 방어 아이템을 장착한 바이 게임 수: {df_vi_data['has_defensive_item'].sum()}회")
print(f"- 방어 아이템을 장착하지 않은 바이 게임 수: {len(df_vi_data) - df_vi_data['has_defensive_item'].sum()}회")
# 최종 병합된 데이터프레임을 엑셀 파일로 저장
merged_with_item_df.to_excel('TFT_Vi_Survival_Analysis_merged.xlsx', index=False)

print("TFT_Vi_Survival_Analysis_merged.xlsx 파일이 성공적으로 저장되었습니다! 😉")
