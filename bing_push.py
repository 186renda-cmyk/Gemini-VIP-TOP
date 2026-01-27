import urllib.request
import json
import os

# 配置信息
HOST = "gemini-vip.top"
KEY = "b571b53d075d4ba09bc1fc37b9e1da48"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
API_URL = "https://api.indexnow.org/indexnow"

def get_all_urls():
    """从 sitemap.xml 提取所有 URL"""
    urls = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sitemap_path = os.path.join(base_dir, 'sitemap.xml')
    
    if not os.path.exists(sitemap_path):
        print(f"❌ 错误: 找不到 sitemap.xml 文件: {sitemap_path}")
        return []
    
    try:
        import re
        with open(sitemap_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 提取 <loc> 标签内容
            urls = re.findall(r'<loc>(.*?)</loc>', content)
            # 过滤掉空白字符
            urls = [url.strip() for url in urls if url.strip()]
            
            # 过滤掉 Google 验证文件 (以防万一 sitemap 中包含)
            urls = [url for url in urls if "google" not in url.split('/')[-1]]
            
    except Exception as e:
        print(f"❌ 解析 sitemap.xml 失败: {str(e)}")
        
    return urls

def push_to_bing(url_list):
    """提交 URL 到 Bing IndexNow"""
    data = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": url_list
    }
    
    json_data = json.dumps(data).encode("utf-8")
    
    req = urllib.request.Request(
        API_URL, 
        data=json_data, 
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    
    print(f"正在提交 {len(url_list)} 个链接到 Bing IndexNow...")
    for url in url_list:
        print(f" - {url}")
        
    try:
        with urllib.request.urlopen(req) as response:
            code = response.getcode()
            if code == 200:
                print("\n✅ 提交成功！Bing 已经收到您的收录请求。")
            else:
                print(f"\n⚠️ 提交可能有问题，返回状态码: {code}")
                print(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"\n❌ 提交失败: {e.code} {e.reason}")
        print(e.read().decode("utf-8"))
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")

if __name__ == "__main__":
    urls = get_all_urls()
    if urls:
        push_to_bing(urls)
    else:
        print("未找到任何 HTML 文件。")
