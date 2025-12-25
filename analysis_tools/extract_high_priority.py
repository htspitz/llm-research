import pandas as pd
import os

# --- 設定 ---
input_file_name = "integrated_sumishin_syukkin.csv"
output_file_name = "high_priority_expenses.csv"

# 抽出対象とするキーワード
HIGH_PRIORITY_KEYWORDS = ['振込', '口座振替', 'ことら送金'] 
# 'ことら送金' も相手先が特定できるため、高優先度として追加

print("--- 処理開始: 高優先度経費の抽出 ---")

try:
    # 1. データの読み込み
    # 統合されたファイルは、最後にutf-8-sigで保存されていると仮定
    print(f"1. ファイル '{input_file_name}' を読み込み中...")
    df = pd.read_csv(input_file_name, encoding='utf-8-sig')

    # 2. データクレンジング（念のため、金額列を数値型に整形）
    print("2. データクレンジングを実行中...")
    cols_to_clean = ['出金金額(円)', '入金金額(円)', '残高(円)']
    for col in cols_to_clean:
        # 数値以外の文字を除去し、数値型に変換
        # NaNや変換エラーは0に置換（抽出条件に影響を与えないように）
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[^\d\.\-]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # '日付'を日付型に変換し、無効な行を削除
    if '日付' in df.columns:
        df['日付'] = pd.to_datetime(df['日付'], errors='coerce')
        df.dropna(subset=['日付'], inplace=True)

    # 3. 抽出条件の作成
    # '内容'列が特定のキーワードを含み、かつ '出金金額(円)' が 0 より大きい行を抽出
    
    # OR条件を作成するための初期設定
    keyword_condition = pd.Series([False] * len(df))
    
    # 各キーワードでOR条件を結合
    if '内容' in df.columns:
        for keyword in HIGH_PRIORITY_KEYWORDS:
            keyword_condition = keyword_condition | df['内容'].str.contains(keyword, na=False)

    # 最終的な抽出条件: キーワードを含む AND 出金がある
    final_condition = keyword_condition & (df['出金金額(円)'] > 0)

    high_priority_expenses = df[final_condition].copy()

    # 4. 結果を新しいCSVファイルとして保存
    high_priority_expenses.to_csv(output_file_name, index=False, encoding='utf-8-sig')

    print("\n--- 処理完了 ---")
    print(f"抽出された取引数: {len(high_priority_expenses)}件")
    print(f"結果はファイル '{output_file_name}' として保存されました。")
    print("\n[抽出結果の最初の5行]")
    # 結果のプレビュー
    if not high_priority_expenses.empty:
        print(high_priority_expenses.head().to_markdown(index=False))
    else:
        print("抽出条件に一致する取引は見つかりませんでした。")

except FileNotFoundError:
    print(f"\nエラー: ファイル '{input_file_name}' が見つかりません。ファイルが同じフォルダにあるか確認してください。")
except Exception as e:
    print(f"\n予期せぬエラーが発生しました: {e}")