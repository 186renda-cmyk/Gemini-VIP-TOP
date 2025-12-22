import requests

# 你的百度推送接口
api_url = "http://data.zz.baidu.com/urls?site=https://gemini-vip.top&token=MkpV4it8Aq1PaVbS"

# 要推送的链接列表（首页和基础页面）
urls = [
    "https://gemini-vip.top/",
    "https://gemini-vip.top/index.html",
    "https://gemini-vip.top/sitemap.xml"
]

headers = {
    'User-Agent': 'curl/7.12.1',
    'Content-Type': 'text/plain'
}

try:
    print("🚀 正在向百度推送 Gemini VIP 的链接...")
    response = requests.post(api_url, data="\n".join(urls), headers=headers)
    print("【推送结果】:", response.text)
    
    if "success" in response.text:
        print("✅ 推送成功！")
    else:
        print("❌ 推送遇到问题，请检查。")
        
except Exception as e:
    print(f"发生错误: {e}")
