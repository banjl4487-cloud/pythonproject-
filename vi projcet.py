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