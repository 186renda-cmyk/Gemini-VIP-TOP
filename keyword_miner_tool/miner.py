import requests
import time
import random
import csv
import string
import os
from fake_useragent import UserAgent
from tqdm import tqdm

# --- 配置区域 ---
DEEP_MINING = True  # 是否开启深度递归挖掘
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, 'seeds.txt')
OUTPUT_FILE = os.path.join(BASE_DIR, 'raw_keywords.csv')
# ----------------

class KeywordMiner:
    def __init__(self):
        self.ua = UserAgent()
        self.seen_keywords = set()
        self.results = []
        
        # 初始化输出文件
        if not os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Keyword', 'Source_Engine', 'Original_Seed'])

    def get_headers(self):
        return {'User-Agent': self.ua.random}

    def fetch_google(self, keyword):
        url = f"http://google.com/complete/search?client=chrome&q={keyword}&hl=zh-CN"
        try:
            response = requests.get(url, headers=self.get_headers(), timeout=5)
            if response.status_code == 200:
                data = response.json()
                if len(data) >= 2:
                    return data[1]
        except Exception as e:
            # tqdm.write(f"Google error for {keyword}: {e}")
            pass
        return []

    def fetch_bing(self, keyword):
        url = f"https://api.bing.com/osjson.aspx?query={keyword}"
        try:
            response = requests.get(url, headers=self.get_headers(), timeout=5)
            if response.status_code == 200:
                data = response.json()
                if len(data) >= 2:
                    return data[1]
        except Exception as e:
            # tqdm.write(f"Bing error for {keyword}: {e}")
            pass
        return []

    def save_keyword(self, keyword, source, original_seed):
        if keyword in self.seen_keywords:
            return
        
        self.seen_keywords.add(keyword)
        self.results.append({
            'Keyword': keyword,
            'Source_Engine': source,
            'Original_Seed': original_seed
        })
        
        # 实时写入
        with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([keyword, source, original_seed])

    def random_delay(self):
        time.sleep(random.uniform(0.5, 1.5))

    def mine(self, seed, level=1):
        # Level 1: 直接搜索种子
        # print(f"Mining Level 1: {seed}")
        self._process_keyword(seed, seed, "Level 1")

        # --- 优化：防卡死机制 ---
        # 关键词长度限制：超过 4 个单词或 25 个字符，跳过深度挖掘
        # 这样可以避免脚本在处理极长、无意义的句子时浪费时间
        if len(seed.split()) > 4 or len(seed) > 25:
            # tqdm.write(f"Skipping deep mining for long keyword: {seed}")
            return
        # ---------------------

        # Level 2: 后缀遍历
        suffixes = list(string.ascii_lowercase + string.digits)
        # print(f"Mining Level 2: {seed} + suffixes")
        
        l2_keywords = []
        
        for char in tqdm(suffixes, desc=f"L2 Mining '{seed}'", leave=False):
            query = f"{seed} {char}"
            new_keywords = self._process_keyword(query, seed, "Level 2")
            l2_keywords.extend(new_keywords)
            self.random_delay()

        # Level 3: 递归扩展
        if DEEP_MINING and level < 3:
            # 按长度排序，取前5个最长的
            l2_keywords.sort(key=len, reverse=True)
            top_5 = l2_keywords[:5]
            
            for sub_seed in tqdm(top_5, desc=f"L3 Deep Mining from '{seed}'", leave=False):
                self.mine(sub_seed, level=level+1)

    def _process_keyword(self, query, original_seed, stage):
        """
        请求双引擎并保存结果
        返回本次请求发现的新关键词列表（用于Deep Mining）
        """
        found_keywords = []
        
        # Google
        g_results = self.fetch_google(query)
        for kw in g_results:
            if kw not in self.seen_keywords:
                self.save_keyword(kw, 'google', original_seed)
                found_keywords.append(kw)
        
        self.random_delay()
        
        # Bing
        b_results = self.fetch_bing(query)
        for kw in b_results:
            if kw not in self.seen_keywords:
                self.save_keyword(kw, 'bing', original_seed)
                if kw not in found_keywords: 
                    pass
        
        current_batch = set(g_results + b_results)
        if query in current_batch:
            current_batch.remove(query)
            
        return list(current_batch)

    def run(self):
        # 读取种子
        if not os.path.exists(INPUT_FILE):
            print(f"Error: {INPUT_FILE} not found.")
            return

        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            seeds = [line.strip() for line in f if line.strip()]

        print(f"Loaded {len(seeds)} seeds: {seeds}")

        for seed in tqdm(seeds, desc="Total Progress"):
            self.mine(seed)
            
        print(f"\nDone! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    miner = KeywordMiner()
    miner.run()
