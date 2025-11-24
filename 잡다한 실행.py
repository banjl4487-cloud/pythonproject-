# 아이템 이름 컬럼 이름 확인 필요, 보통 병합 후 'item_name_item_info' 혹은 비슷한 이름일 수 있음
item_name_col = 'item_id'  # 필요하면 실제 컬럼명으로 수정!

if item_name_col in final_mega_df.columns:
    solari_rows = final_mega_df[final_mega_df[item_name_col] == '강철의 솔라리 펜던트']
    if not solari_rows.empty:
        print("✅ 솔라리 펜던트가 final_mega_df에 존재합니다.")
        print(solari_rows.head())
        # 아이템 분류 칼럼도 확인
        item_type_col = 'item_type_item_info'  # 실제 컬럼명으로 수정 필요
        if item_type_col in solari_rows.columns:
            types = solari_rows[item_type_col].unique()
            print(f"-> 솔라리 펜던트의 분류: {types}")
        else:
            print("-> 아이템 타입(분류) 컬럼은 없습니다.")
    else:
        print("❌ final_mega_df에 솔라리 펜던트가 없습니다.")
else:
    print("❌ 아이템 이름 컬럼을 찾을 수 없습니다.")