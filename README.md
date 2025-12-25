# LLM & Data Science Research

本リポジトリは、LLM（大規模言語模型）の活用検証、およびデータサイエンスの実践的な前処理スクリプトをまとめたリサーチログです。

## 📂 構成

### 1. analysis_tools
銀行明細（住信SBIネット銀行）などの実データを対象とした、データエンジニアリング用スクリプト群です。
- **merge_csv.py**: 複数期間のCSVを統合し、エンコーディング修正や金額のクレンジング、日付によるソートを自動化します。
- **extract_debit.py / extract_high_priority.py**: 統合データからデビット利用明細や振込、高優先度の経費項目を特定条件で抽出します。

### 2. notebooks
LLM（Claude/Gemini等）を活用した技術検証ノートブックです。
- **llm-amazon-item-classification.ipynb**: Amazonの購入履歴をLLMに渡し、商品カテゴリの自動分類や家計簿データへの整形を試行した記録です。Google ColabのSecrets（環境変数）を利用し、APIキーの秘匿化を行っています。

## 🛠️ 技術スタック
本リポジトリでは、以下の技術・ライブラリを実戦的に組み合わせて使用しています。

- **Language**: Python 3.10+
- **LLM / AI**: 
    - **Anthropic (Claude API)**: 非同期クライアント (`AsyncAnthropic`) を用いた高速なデータ分類
    - **Prompt Engineering**: 構造化データ抽出のためのプロンプト最適化
- **Data Engineering**:
    - **pandas**: 大規模なCSV統合、型変換、クレンジング処理
    - **re (Regular Expression)**: 正規表現を用いた高度なテキスト抽出・正規化
    - **tqdm**: 非同期処理やループ処理の進捗可視化
- **Infrastructure / Environment**:
    - **Google Colab (Secrets管理)**: APIキー等の秘匿情報管理
    - **Asyncio**: 非同期処理によるAPIコールの効率化
- **Methodology**: 
    - **AI-DLC (AI Driven Life Cycle)**: AIを単なる補助ではなく、設計・実装・テストの各工程に組み込んだ爆速開発フローの実践

## ⚡ セキュリティについて
- 本リポジトリ内のコードは、APIキーや個人情報をハードコードせず、環境変数またはシークレット管理機能を利用して実行する構成としています。