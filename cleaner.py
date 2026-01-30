import pandas as pd
import os
from datetime import datetime

# --- 配置区域 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, 'raw_keywords.csv')
OUTPUT_CSV = os.path.join(BASE_DIR, 'final_tasks.csv')
OUTPUT_MD = os.path.join(BASE_DIR, 'research_plan.md')

BLACKLIST = ['星座', '运势', '性格', '配对', '男', '女', '生日', 'NASA', '天文', '股票', '基金']

INTENT_KEYWORDS = {
    'Transactional': ['买', '号', '价格', '充值', '合租', '拼车', '会员', '升级', '便宜'],
    'Informational': ['怎么', '教程', '注册', '下载', '登录', '入口', '失败', '验证', '节点', '梯子']
}
# ----------------

def classify_intent(keyword):
    """
    根据关键词内容分类意图
    """
    keyword = str(keyword)
    
    # Check Transactional
    for term in INTENT_KEYWORDS['Transactional']:
        if term in keyword:
            return 'Transactional'
            
    # Check Informational
    for term in INTENT_KEYWORDS['Informational']:
        if term in keyword:
            return 'Informational'
            
    return 'General'

def is_blacklisted(keyword):
    """
    检查是否包含黑名单词汇
    """
    keyword = str(keyword)
    for term in BLACKLIST:
        if term in keyword:
            return True
    return False

def generate_markdown(df):
    """
    生成 Markdown 格式的研究计划
    """
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    md_content = f"""# 🦁 Gemini 网站内容素材搜集表
> 自动生成时间：{current_date}

## 💰 必争的变现词 (Transactional)
*提示：重点搜索价格对比、防骗指南、购买渠道测评*
"""

    # Transactional Section
    trans_df = df[df['Intent'] == 'Transactional']
    for _, row in trans_df.iterrows():
        md_content += f"""- [ ] **关键词：{row['Keyword']}**
  - [ ] *素材来源 1 (链接/笔记):*
  - [ ] *素材来源 2 (链接/笔记):*
"""

    md_content += """
## 📈 必写的引流词 (Informational)
*提示：重点搜索最新教程、报错解决方法*
"""

    # Informational Section
    info_df = df[df['Intent'] == 'Informational']
    for _, row in info_df.iterrows():
        md_content += f"""- [ ] **关键词：{row['Keyword']}**
  - [ ] *素材来源 1:*
  - [ ] *素材来源 2:*
"""

    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Markdown report generated: {OUTPUT_MD}")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Please run miner.py first.")
        return

    print("Loading data...")
    try:
        df = pd.read_csv(INPUT_FILE)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print(f"Original count: {len(df)}")

    # 1. 去重 (虽然 miner.py 做了去重，但为了保险再做一次，且去空)
    df.drop_duplicates(subset=['Keyword'], inplace=True)
    df.dropna(subset=['Keyword'], inplace=True)
    
    # 2. 黑名单过滤
    # 使用 apply 函数进行过滤
    mask = df['Keyword'].apply(lambda x: not is_blacklisted(x))
    df = df[mask]
    print(f"After blacklist filtering: {len(df)}")

    # 3. 意图分类
    df['Intent'] = df['Keyword'].apply(classify_intent)
    
    # 4. 设置状态
    df['Status'] = 'Pending'

    # 5. 保存清洗后的数据 (final_tasks.csv)
    # 只保留需要的列
    output_columns = ['Keyword', 'Intent', 'Status']
    # 如果原文件有 Original_Seed，也可以保留
    if 'Original_Seed' in df.columns:
        output_columns.append('Original_Seed')
        
    df[output_columns].to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"Cleaned data saved to: {OUTPUT_CSV}")

    # 6. 生成 Markdown 报告
    generate_markdown(df)

if __name__ == "__main__":
    main()
