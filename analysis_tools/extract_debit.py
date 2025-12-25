import pandas as pd
import os

# --- 設定 ---
input_file_name = "integrated_sumishin_syukkin.csv"
output_file_name = "debit_transactions.csv"

print("--- 処理開始: デビット取引の抽出 ---")

try:
    # 1. データの読み込み
    # ファイルはutf-8-sigで保存されていると仮定して読み込み
    print(f"1. ファイル '{input_file_name}' を読み込み中...")
    df = pd.read_csv(input_file_name, encoding='utf-8-sig')

    # 2. データクレンジング（念のため、金額列を数値型に整形）
    print("2. データクレンジングを実行中...")
    cols_to_clean = ['出金金額(円)', '入金金額(円)', '残高(円)']
    for col in cols_to_clean:
        if col in df.columns:
            # 数値以外の文字を除去し、数値型に変換
            df[col] = df[col].astype(str).str.replace(r'[^\d\.\-]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # '日付'を日付型に変換
    if '日付' in df.columns:
        df['日付'] = pd.to_datetime(df['日付'], errors='coerce')
        df.dropna(subset=['日付'], inplace=True)

    # 3. 抽出条件の作成
    # '内容'列に 'デビット' という文字列を含み、かつ '出金金額(円)' が 0 より大きい行を抽出
    if '内容' in df.columns:
        # 'デビット'を含む AND 出金がある
        debit_condition = (df['内容'].str.contains('デビット', na=False)) & (df['出金金額(円)'] > 0)
    else:
        print("エラー: データに '内容' 列が見つかりません。抽出をスキップします。")
        exit()

    debit_transactions = df[debit_condition].copy()

    # 4. 結果を新しいCSVファイルとして保存
    debit_transactions.to_csv(output_file_name, index=False, encoding='utf-8-sig')

    print("\n--- 処理完了 ---")
    print(f"抽出されたデビット取引数: {len(debit_transactions)}件")
    print(f"結果はファイル '{output_file_name}' として保存されました。")
    print("\n[抽出結果の最初の5行]")
    # 結果のプレビュー
    if not debit_transactions.empty:
        print(debit_transactions.head().to_markdown(index=False))
    else:
        print("抽出条件に一致するデビット取引は見つかりませんでした。")

except FileNotFoundError:
    print(f"\nエラー: ファイル '{input_file_name}' が見つかりません。ファイルが同じフォルダにあるか確認してください。")
except Exception as e:
    print(f"\n予期せぬエラーが発生しました: {e}")