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


#    - 문제 정의: 원본 데이터의 `players` 컬럼은 JSON 문자열 또는 파이썬 리스트/딕셔너리 형태의 문자열로,
#                 다양한 플레이어와 그들이 보유한 유닛(챔피언) 정보를 중첩된 형태로 담고 있습니다.
#    - 해결 목표: 이 복잡한 구조에서 각 게임에 사용된 모든 챔피언의 `character_id`(이름)만을 안전하게 추출합니다.
# ----------------------------------------------------------------------------------------------------
def parse_players_and_units_for_champions(row):
    champions = []  # 추출된 챔피언 이름을 저장할 리스트 초기화

    # 데이터 파싱 시도: 데이터 포맷의 불확실성에 대비한 견고한(robust) 처리 로직입니다.
    try:
        players_data = json.loads(row['players'])  # 1차 시도: 표준 JSON 형식으로 파싱합니다. (가장 흔한 경우)
    except json.JSONDecodeError:  # JSON 파싱에 실패하면,
        try:
            # 2차 시도: 파이썬의 `ast.literal_eval`을 사용하여 리터럴 문자열을 파싱합니다.
            #          일반적인 문자열 딕셔너리/리스트 형태일 때 유용합니다.
            players_data = ast.literal_eval(row['players'])
        except (ValueError, SyntaxError):
            # 두 파싱 방식 모두 실패할 경우, 해당 row는 무시하고 빈 리스트를 반환합니다.
            # 데이터 손실을 최소화하면서도, 프로그램이 비정상적으로 종료되는 것을 방지하는 예외 처리입니다.
            return []

    # 추출된 플레이어 데이터에서 각 유닛(챔피언)의 ID를 탐색
    for player in players_data:
        # 'units' 키가 존재하고 그 값이 리스트 형태인지 확인하여, 데이터 구조의 유효성을 검증합니다.
        if 'units' in player and isinstance(player['units'], list):
            for unit in player['units']:
                # 'character_id' 키가 존재할 경우, 해당 챔피언 이름을 추출합니다.
                if 'character_id' in unit:
                    champions.append({'champion_name': unit['character_id']})
    return champions  # 추출된 챔피언 이름 리스트 반환


# ----------------------------------------------------------------------------------------------------
# 2. [데이터 불러오기] 필요한 원본 데이터 파일을 로드합니다.
#    - 중요성: 모든 분석의 시작점으로, 파일 경로의 정확성과 안정적인 로딩이 필수적입니다.
# ----------------------------------------------------------------------------------------------------
file_path_match = 'TFT_Challenger_MatchData.csv'  # 챌린저 매치 게임 상세 데이터
file_path_item = 'TFT_Item_CurrentVersion.csv'  # 아이템 정보 데이터
file_path_champion_info = 'TFT_Champion_CurrentVersion.csv'  # 챔피언 상세 정보 데이터

try:
    df_match = pd.read_csv(file_path_match)  # 매치 데이터 로드
    df_item = pd.read_csv(file_path_item)  # 아이템 데이터 로드
    df_champion_info = pd.read_csv(file_path_champion_info)  # 챔피언 데이터 로드
    print("✅ 모든 원본 데이터를 성공적으로 불러왔습니다. 분석 준비 완료.")
except FileNotFoundError as e:
    # `FileNotFoundError` 발생 시, 사용자에게 명확한 메시지를 전달하고 프로그램 종료를 유도합니다.
    # 이는 코드의 사용자 친화성과 견고성을 높이는 중요한 예외 처리입니다.
    print(f"❌ 오류: 지정된 파일 '{e.filename}'을(를) 찾을 수 없습니다. 파일 경로 및 이름을 다시 확인해주세요.")
    exit()
except Exception as e:
    # 예상치 못한 다른 오류 발생 시, 상세 오류 메시지를 출력하고 프로그램을 종료합니다.
    # 광범위한 예외 처리를 통해 안정성을 확보합니다.
    print(f"❌ 데이터 로드 중 예상치 못한 오류 발생: {e}")
    exit()

# ----------------------------------------------------------------------------------------------------
# 3. [데이터 전처리] `df_match`에서 챔피언 이름 추출 및 `df_champions_exploded` 생성
#    - 문제 정의: `df_match`의 `players` 컬럼은 JSON(또는 유사 형태) 내 챔피언 이름을 포함하며,
#                 이 형태로는 직접적인 분석이 어렵습니다.
#    - 해결 목표: 각 게임의 모든 챔피언 이름을 개별 행으로 분리하여 새로운 데이터프레임을 생성합니다.
# ----------------------------------------------------------------------------------------------------
all_champions_data = df_match.apply(parse_players_and_units_for_champions, axis=1)  # 각 매치에 함수 적용
# 추출된 중첩 리스트를 평탄화(flatten)하여 단일 DataFrame `df_champions_exploded`를 생성합니다.
# 이는 통계 및 집계 분석을 위한 핵심적인 데이터 구조 변환 과정입니다.
df_champions_exploded = pd.DataFrame([champ for sublist in all_champions_data if sublist for champ in sublist])
print("✅ `df_champions_exploded` (각 게임의 챔피언 목록) 생성이 완료되었습니다.")

# ----------------------------------------------------------------------------------------------------
# 4. [데이터 정제] 챔피언 이름 통일 (대소문자 일치)
#    - 문제 정의: `df_champions_exploded`의 `champion_name`과 `df_champion_info`의 `name` 컬럼에
#                 동일 챔피언이라도 대소문자 표기(예: 'Vi' vs 'vi')가 다를 수 있습니다.
#                 이는 `pd.merge()` 시 데이터 불일치(KeyError 또는 누락)로 이어져 분석 오류를 유발합니다.
#    - 해결 목표: 두 데이터프레임의 모든 챔피언 이름을 일관된 형태(여기서는 대문자)로 통일하여,
#                 이후 데이터 병합 및 분석의 정확성을 확보합니다.
# ----------------------------------------------------------------------------------------------------
df_champions_exploded['champion_name'] = df_champions_exploded['champion_name'].str.upper()  # 모든 챔피언 이름을 대문자로 변환
df_champion_info['name'] = df_champion_info['name'].str.upper()  # 챔피언 정보 데이터의 이름도 대문자로 변환
print("✅ 두 데이터프레임(`df_champions_exploded`, `df_champion_info`)의 챔피언 이름이 모두 대문자로 통일되었습니다.")
print("    - 이제 `pd.merge` 등 챔피언 이름을 기준으로 하는 모든 작업에서 데이터 불일치 문제가 발생하지 않을 것입니다.")

# ----------------------------------------------------------------------------------------------------
# [다음 단계]
# 이제 df_champions_exploded와 df_champion_info, df_item 데이터를 활용하여
# 챔피언과 아이템 정보를 병합하고, 원하는 분석(예: Vi 챔피언의 방어 아이템 착용시 생존 분석)을 진행할 준비가 완료되었습니다.
# ----------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------
# 5. [프로젝트 전제 검증] 챌린저 게임에서 가장 많이 등장한 챔피언 확인 (Vi에 집중하는 핵심 동기 재확인)
#    - [프로젝트 목표 연결]: Vi 챔피언의 생존 시간 분석을 위한 'Vi 선택'의 정당성을 확보합니다.
#                           Vi가 챌린저 큐에서 실제 가장 많이 활용되는 챔피언 중 하나임을 검증합니다.
#    - [해결 목표]: `df_champions_exploded` 데이터에서 각 챔피언의 총 등장 횟수를 계산하여 순위를 매기고,
#                 Vi 챔피언(`VI`)의 등장 횟수와 순위를 '확실하게' 다 확인합니다.
# ----------------------------------------------------------------------------------------------------

print("\n--- ✅ 챌린저 게임 데이터 내 챔피언 등장 빈도 TOP 10 검증 ---")

# 'champion_name' 컬럼(현재 모두 대문자)의 각 챔피언 등장 횟수를 계산하고 내림차순으로 정렬합니다.
# 이는 특정 챔피언이 해당 게임 환경에서 얼마나 주력으로 사용되는지 보여주는 핵심 지표입니다.
most_picked_champions = df_champions_exploded['champion_name'].value_counts()

# 가장 많이 등장한 상위 10개 챔피언을 출력하여 전체적인 챔피언 활용 분포를 파악합니다.
print(most_picked_champions.head(10))

# 'VI' 챔피언이 전체 순위에서 몇 위인지, 총 몇 번 등장했는지 '강력하게' 찾아 증명합니다.
if 'VI' in most_picked_champions.index:  # 'VI'가 챔피언 목록에 있는지 먼저 확인
    vi_count = most_picked_champions['VI']  # 'VI' 챔피언의 총 등장 횟수
    # `get_loc()`은 해당 값의 인덱스(0부터 시작)를 반환하므로, 실제 순위를 위해 +1을 합니다.
    vi_rank = most_picked_champions.index.get_loc('VI') + 1

    print(f"\n👉 'VI' 챔피언 순위: {vi_rank}위, 총 등장 횟수: {vi_count}회")
    print("    - 위 결과는 'VI' 챔피언이 챌린저 큐에서 높은 활용도를 가짐을 보여주며, ")
    print("    - 'VI' 챔피언의 생존력 분석에 집중하는 본 프로젝트의 핵심 동기를 뒷받침합니다.")
else:
    print("\n👉 'VI' 챔피언은 검증 목록에 없습니다. 프로젝트 전제 재검토 필요!")

# ----------------------------------------------------------------------------------------------------
# [다음 단계]
#   - Vi(VI) 챔피언의 높은 활용도 전제가 검증되었으므로, 이제 데이터를 병합하여
#     Vi의 방어 아이템 착용 여부에 따른 게임 내 '생존 시간(ingameDuration)' 분석을 본격적으로 진행할 준비가 완료되었습니다.
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# 5. [데이터 최적화/필터링] 모든 챔피언 중 'VI' 챔피언 데이터만 초기 단계에서 분리
#    - [프로젝트 목표 연결]: Vi 챔피언의 생존 시간 분석이라는 명확한 목표에 따라,
#                           전체 데이터를 모두 병합한 후 Vi를 필터링하는 대신,
#                           초기 단계에서부터 'VI' 챔피언 데이터에만 집중하여 처리 효율을 극대화합니다.
#    - [해결 목표]: `df_champions_exploded`에서 'VI' 챔피언에 해당하는 행들만 추출하여,
#                 이후의 모든 병합 및 분석 과정에서 'VI' 데이터에만 집중할 수 있도록 준비합니다.
#                 이는 불필요한 데이터 처리량을 줄여 성능을 향상시킵니다.
# ----------------------------------------------------------------------------------------------------
print("\n--- ✅ `df_champions_exploded`에서 'VI' 챔피언 데이터만 초기 필터링 시작 ---")

# 'VI' 챔피언 데이터만 추출합니다.
# 이미 'champion_name' 컬럼이 모두 대문자로 통일되었으므로 'VI'로 정확하게 필터링할 수 있습니다.
vi_exploded = df_champions_exploded[df_champions_exploded['champion_name'] == 'VI'].copy()

if vi_exploded.empty:
    print("❌ 초기 `df_champions_exploded`에서 'VI' 챔피언 데이터를 '초 코딱지만큼도' 찾을 수 없습니다. (프로그램 종료)")
    print("    - 챔피언 이름 대문자 통일 과정 또는 원본 데이터에 'VI' 챔피언 존재 여부를 재확인해 주세요.")
    exit() # Vi 데이터가 없으면 이후 분석을 진행할 이유가 없으므로 종료

print(f"✅ 'VI' 챔피언 데이터 {len(vi_exploded)}개 초기 필터링 완료! (vi_exploded 생성)")
# print(vi_exploded.head())


# ----------------------------------------------------------------------------------------------------
# 6. [데이터 병합 1단계] 'VI' 챔피언 데이터에 해당 게임의 상세 정보 연결
#    - [프로젝트 목표 연결]: 'VI' 챔피언이 어떤 게임에 속했고, 그 게임이 얼마나 지속되었는지를
#                           정확히 파악하여 `ingameDuration` 분석의 기반을 마련합니다.
#    - [해결 목표]: `vi_exploded` (필터링된 'VI' 챔피언 목록)에 `df_match` (게임별 상세 정보)의
#                 핵심 컬럼을 `gameId`를 기준으로 병합합니다.
# ----------------------------------------------------------------------------------------------------
print("\n--- ✅ `vi_exploded`에 매치 정보 병합 시작 ---")
# df_match에서 필요한 컬럼(gameId, ingameDuration)만 추출하여 메모리 효율성을 높입니다.
df_match_for_merge = df_match[['gameId', 'ingameDuration']].copy()
vi_merged_with_match = pd.merge(
    vi_exploded,                 # 왼쪽 데이터프레임: 'VI' 챔피언 정보 (gameId, champion_name)
    df_match_for_merge,          # 오른쪽 데이터프레임: 게임 상세 정보 (gameId, ingameDuration)
    on='gameId',                 # 병합 기준 키: 게임 ID
    how='left'                   # 왼쪽('VI' 챔피언 목록) 기준으로 모든 정보 유지
)
print("✅ 'VI' 챔피언 데이터에 매치 정보 병합 완료! (vi_merged_with_match 생성)")
# print(vi_merged_with_match.head())


# ----------------------------------------------------------------------------------------------------
# 7. [데이터 병합 2단계] 'VI' 챔피언 데이터에 챔피언 상세 정보 연결
#    - [프로젝트 목표 연결]: 'VI' 챔피언 자체의 속성(`cost`, `origin`, `class`)을 연결하여,
#                           Vi 챔피언의 특성을 이해하고 추후 필요 시 심층적인 분석 기반을 마련합니다.
#    - [해결 목표]: `vi_merged_with_match`에 `df_champion_info` (챔피언 상세 정보)를
#                 챔피언 이름을 기준으로 병합합니다.
#                 (이번 단계에서는 `df_item`과의 병합이 생략되므로 `suffixes`도 필요 없습니다.)
# ----------------------------------------------------------------------------------------------------
print("\n--- ✅ `vi_merged_with_match`에 챔피언 상세 정보 병합 시작 ---")
# `suffixes`는 두 DataFrame에 같은 이름의 컬럼이 있을 때만 필요합니다.
# `vi_merged_with_match`에는 'champion_name'만 있고 'name' 컬럼이 없으며,
# `df_champion_info`에는 'name' 컬럼만 있어 충돌이 발생하지 않습니다.
final_vi_df_no_items = pd.merge(
    vi_merged_with_match,        # 왼쪽 데이터프레임: 'VI' 챔피언, 매치 정보 (gameId, ingameDuration, champion_name)
    df_champion_info,            # 오른쪽 데이터프레임: 챔피언 상세 정보 (name, cost, origin, class 등)
    left_on='champion_name',     # 왼쪽 키: 챔피언 이름 (현재 모두 대문자 'VI')
    right_on='name',             # 오른쪽 키: 챔피언 정보의 이름 (현재 모두 대문자 'VI')
    how='left'                   # 왼쪽('VI' 챔피언) 기준으로 모든 정보 유지
)
print("✅ 'VI' 챔피언만을 위한 최종 데이터프레임 (아이템 제외) `final_vi_df_no_items` 생성 완료!")

# 최종 결과 확인 (옵션)
# print(final_vi_df_no_items.head())
# print(final_vi_df_no_items.info())

# ----------------------------------------------------------------------------------------------------
# [최종 준비 완료]
#   - 이제 `final_vi_df_no_items`는 각 게임에서 등장한 'VI' 챔피언에 대한 게임 ID, `ingameDuration`,
#     그리고 챔피언 자체의 상세 정보(`cost`, `origin`, `class` 등)가 모두 통합된,
#     'VI' 챔피언 생존 분석에 최적화된 데이터프레임입니다.
#   - 이 데이터프레임에는 현재 아이템 정보는 포함되어 있지 않습니다.
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# 9. [아이템 데이터 추출] 각 게임에서 'VI' 챔피언이 장착한 아이템 ID 추출
#    - [프로젝트 목표 연결]: Vi의 생존 시간 분석에서 '방어 아이템 착용 여부'를 판단하기 위해,
#                           Vi가 각 게임에서 어떤 아이템을 장착했는지 파악해야 합니다.
#    - [해결 목표]: `df_match`의 `players` 컬럼에서 'VI' 챔피언이 장착한 모든 `item_id`를 추출합니다.
# ----------------------------------------------------------------------------------------------------
print("\n--- ✅ 'VI' 챔피언이 장착한 아이템 ID 추출 시작 ---")

# 'final_vi_df_no_items'의 고유 gameId 리스트를 '초 강력하게' 준비 (VI가 나온 게임만!)
vi_game_ids = final_vi_df_no_items['gameId'].unique()


# 각 게임의 'players' 컬럼에서 특정 챔피언(VI)이 장착한 아이템 ID를 추출하는 함수
def parse_vi_items(row, target_champion_name="VI"):
    vi_items = []

    # 예외 처리: 'players' 컬럼이 비어있거나 파싱할 수 없는 경우를 대비합니다.
    try:
        players_data = json.loads(row['players'])
    except json.JSONDecodeError:
        try:
            players_data = ast.literal_eval(row['players'])
        except (ValueError, SyntaxError):
            return vi_items  # 파싱 실패 시 빈 리스트 반환

    for player in players_data:
        if 'units' in player and isinstance(player['units'], list):
            for unit in player['units']:
                # `character_id`가 우리가 찾는 `target_champion_name` ('VI')과 일치하는지 확인
                if 'character_id' in unit and unit['character_id'].upper() == target_champion_name:
                    # 해당 VI 챔피언이 장착한 모든 아이템 ID를 추출합니다.
                    if 'item_ids' in unit and isinstance(unit['item_ids'], list):
                        for item_id in unit['item_ids']:
                            vi_items.append({'gameId': row['gameId'], 'vi_item_id': item_id})
    return vi_items


# VI 챔피언이 등장했던 게임(`vi_game_ids`)만 필터링하여 'players' 컬럼 파싱
vi_match_data = df_match[df_match['gameId'].isin(vi_game_ids)].copy()
all_vi_items_data = vi_match_data.apply(parse_vi_items, axis=1)

# 추출된 아이템 ID 데이터를 단일 DataFrame으로 '초 강력하게' 변환
vi_items_exploded = pd.DataFrame([item for sublist in all_vi_items_data for item in sublist])

if vi_items_exploded.empty:
    print("❌ 'VI' 챔피언이 장착한 아이템 데이터를 '초 코딱지만큼도' 찾을 수 없습니다. (Top 5 분석 불가)")
    # exit() # Top 5 분석이 불가능하지만, 이후 다른 분석을 위해 일단 종료하지는 않습니다.
else:
    print(f"✅ 'VI' 챔피언이 장착한 아이템 데이터 {len(vi_items_exploded)}개 추출 완료! (vi_items_exploded 생성)")
    # print(vi_items_exploded.head())

# ----------------------------------------------------------------------------------------------------
# 10. [데이터 병합] 추출된 'VI' 아이템 ID와 'df_item'을 병합하여 아이템 이름 가져오기
#    - [프로젝트 목표 연결]: 장착한 아이템의 ID만으로는 분석이 어렵기 때문에,
#                           사람이 이해할 수 있는 아이템 이름으로 변환해야 합니다.
#    - [해결 목표]: `vi_items_exploded`의 `vi_item_id`와 `df_item`의 `id`를 병합하여,
#                 각 아이템의 이름(`name`)을 `vi_item_name` 컬럼으로 가져옵니다.
# ----------------------------------------------------------------------------------------------------
if not vi_items_exploded.empty:
    print("\n--- ✅ 'VI' 아이템 ID에 아이템 이름 정보 병합 시작 ---")
    # df_item의 name 컬럼을 'vi_item_name'으로 가져올 것이므로, 여기서도 suffixes는 필요 없습니다.
    # df_item의 'id' 컬럼은 이미 정수형일 것이므로, 'id' 기준으로 병합.
    vi_items_with_names = pd.merge(
        vi_items_exploded,  # 왼쪽: 'VI' 챔피언의 gameId와 item_id
        df_item[['id', 'name']],  # 오른쪽: 아이템의 id와 이름
        left_on='vi_item_id',  # 왼쪽 키: 추출된 'VI' 아이템 ID
        right_on='id',  # 오른쪽 키: df_item의 아이템 ID
        how='left'  # 왼쪽 기준으로 모두 유지
    ).rename(columns={'name': 'vi_item_name'})  # 병합된 아이템 이름을 'vi_item_name'으로 변경하여 명확하게 합니다.
    print("✅ 'VI' 챔피언 아이템 ID에 이름 정보 병합 완료! (vi_items_with_names 생성)")
    # print(vi_items_with_names.head())

    # ----------------------------------------------------------------------------------------------------
    # 11. [분석] 'VI' 챔피언이 가장 많이 장착한 아이템 Top 5 분석
    #    - [프로젝트 목표 연결]: 'VI'가 자주 사용하는 방어 아이템의 종류를 파악하여,
    #                           이후 생존 시간 분석 시 특정 아이템 그룹에 집중할 수 있는 기반을 마련합니다.
    #    - [해결 목표]: 'vi_items_with_names'에서 `vi_item_name` 컬럼의 빈도를 계산하여,
    #                 가장 많이 등장한 상위 5개 아이템을 '초 확실하게' 다 조져서 출력합니다.
    # ----------------------------------------------------------------------------------------------------
    print("\n--- ✅ 'VI' 챔피언이 가장 많이 장착한 아이템 TOP 5 ---")

    # `value_counts()`로 각 아이템 이름의 빈도를 계산하고, 상위 5개를 출력합니다.
    top_5_vi_items = vi_items_with_names['vi_item_name'].value_counts().head(5)

    if not top_5_vi_items.empty:
        print(top_5_vi_items)
        print("✅ 'VI' 챔피언이 가장 많이 장착한 아이템 Top 5 분석 완료!")
    else:
        print("❌ 'VI' 챔피언의 아이템 데이터가 없어 Top 5를 분석할 수 없습니다.")
else:
    print("\n⚠️ 'VI' 챔피언의 아이템 데이터가 부족하여 Top 5 분석을 건너뜁니다.")

# ----------------------------------------------------------------------------------------------------
# [다음 단계]
#   - 이제 Vi 챔피언이 가장 많이 사용하는 아이템 Top 5를 파악했습니다.
#   - 이 정보를 바탕으로 주현 님이 제시할 방어 아이템 목록과 비교 검증하고,
#     최종적으로 이 아이템 정보를 `final_vi_df_no_items`에 합치는 단계로 나아갈 것입니다.
# ----------------------------------------------------------------------------------------------------


