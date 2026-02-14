import cloudscraper
import requests
import time
import os

# 配置区域 ==================================================
# 目标 URL (DMIT Malibu 套餐)
TARGET_URL = "https://www.dmit.io/cart.php?a=add&pid=183"

# Server酱 SendKey (去 https://sct.ftqq.com/ 获取)
# 建议由环境变量传入，或者直接填在下面引号里
SC_KEY = os.environ.get("SC_KEY", "这里填你的Server酱Key") 

# =========================================================

def send_wechat_notice(title, content):
    """发送微信通知"""
    if not SC_KEY or "这里填" in SC_KEY:
        print("未配置 Server酱 Key，跳过通知")
        return
    
    url = f"https://sctapi.ftqq.com/{SC_KEY}.send"
    data = {"title": title, "desp": content}
    try:
        requests.post(url, data=data)
        print("微信通知已发送")
    except Exception as e:
        print(f"发送通知失败: {e}")

def check_stock():
    # 创建 CloudScraper 实例，模拟 Chrome 浏览器
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'darwin',
            'desktop': True
        }
    )

    try:
        print(f"正在尝试访问: {TARGET_URL}")
        # 请求网页
        resp = scraper.get(TARGET_URL, timeout=30)
        
        # 打印状态码，方便调试
        print(f"Status Code: {resp.status_code}")

        # 核心判断逻辑：
        # 如果页面里包含 "Out of Stock"，说明没货
        # 如果页面里包含 "Order Summary" 或者 "Configure"，说明有货！
        if "Out of Stock" in resp.text:
            print("当前状态: 缺货 (Out of Stock)")
        elif "Order Summary" in resp.text or "Checkout" in resp.text:
            print("!!! 发现有货 !!!")
            send_wechat_notice("DMIT Malibu 补货了！", f"快去抢！链接: {TARGET_URL}")
        else:
            # 可能是 Cloudflare 盾太厚，没过得去，或者页面结构变了
            print("未知状态 (可能被盾拦截或页面变动)")
            # 可以在这里发个通知告诉自己脚本可能失效了
            # send_wechat_notice("DMIT监控异常", "无法识别页面状态，请检查 GitHub Actions")

    except Exception as e:
        print(f"请求发生错误: {e}")

if __name__ == "__main__":
    check_stock()
