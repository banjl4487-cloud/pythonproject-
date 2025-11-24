import pandas as pd

file_path1 = 'TFT_Item_CurrentVersion.csv'

try:
    # 이 부분!!! 불러온 데이터를 'df'라는 변수에 담아야 해!
    df = pd.read_csv(file_path1)  # <- df = 이 부분이 없었으면 에러가 났겠지!

    print("데이터 불러오기 성공!")
    print("데이터프레임 상위 5줄:")
    print(df.head())  # <- 담아둔 'df' 변수를 써서 데이터를 보는 거야
    print("\n데이터프레임 정보:")
    df.info()  # <- 역시 'df' 변수를 써서 정보를 보는 거고
except FileNotFoundError:
    print(f"오류: '{file_path1}' 파일을 찾을 수 없습니다. 파일 경로와 이름을 확인해 주세요.")
except Exception as e:
    print(f"데이터 불러오기 중 오류 발생: {e}")