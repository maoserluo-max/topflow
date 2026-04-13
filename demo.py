import json
from crawler import crawler


def print_separator():
    """打印分隔线"""
    print("\n" + "=" * 60 + "\n")


def format_number(num):
    """格式化数字显示"""
    if num is None:
        return "N/A"
    if isinstance(num, (int, float)):
        if num >= 100000000:
            return f"{num / 100000000:.2f}亿"
        elif num >= 10000:
            return f"{num / 10000:.2f}万"
        else:
            return str(num)
    return str(num)


def display_influencer_info(data):
    """展示达人信息"""
    if not data:
        print("❌ 获取达人信息失败！")
        return

    print("✅ 成功获取达人信息！\n")
    print(f"📱 平台: {data.get('platform', 'unknown').upper()}")
    print(f"👤 账号名称: {data.get('account_name', 'N/A')}")
    print(f"🔗 用户名: {data.get('username', 'N/A')}")
    
    tiktok_id = data.get('tiktok_id', '')
    if tiktok_id:
        print(f"🆔 TikTok ID: {tiktok_id}")
    
    fans_count = data.get('fans_count', 0)
    if fans_count > 0:
        print(f"👥 粉丝数: {format_number(fans_count)}")
    else:
        print(f"👥 粉丝数: 受限 (需要登录或API权限)")
    
    print(f"🎬 视频数: {format_number(data.get('video_count'))}")
    signature = data.get('signature', 'N/A')
    if signature:
        print(f"📝 简介: {signature[:100]}...")
    else:
        print(f"📝 简介: 未公开")
    print(f"🖼️ 头像: {data.get('avatar_url', 'N/A')}")
    print(f"🔗 主页: {data.get('homepage_url', 'N/A')}")

    print("\n原始数据（JSON格式）:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def display_video_info(data):
    """展示视频信息"""
    if not data:
        print("❌ 获取视频数据失败！")
        return

    print("✅ 成功获取视频数据！\n")
    print(f"📱 平台: {data.get('platform', 'unknown').upper()}")
    print(f"👤 达人: {data.get('influencer_name', 'N/A')}")
    print(f"🎬 标题: {data.get('video_title', 'N/A')}")
    print(f"📅 发布日期: {data.get('publish_date', 'N/A')}")
    print(f"▶️ 播放量: {format_number(data.get('play_count'))}")
    print(f"❤️ 点赞数: {format_number(data.get('like_count'))}")
    print(f"💬 评论数: {format_number(data.get('comment_count'))}")
    print(f"🔄 分享数: {format_number(data.get('share_count'))}")
    print(f"🔗 视频链接: {data.get('video_url', 'N/A')}")

    print("\n原始数据（JSON格式）:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    """主函数 - 交互式菜单"""
    print("\n" + "🎯" * 20)
    print("       TikTok 数据抓取 Demo")
    print("🎯" * 20)

    while True:
        print("\n请选择功能:")
        print("1. 📊 获取达人主页信息")
        print("2. 🎬 获取视频数据")
        print("3. ❌ 退出程序")

        choice = input("\n请输入选项 (1/2/3): ").strip()

        if choice == '1':
            print_separator()
            print("功能1: 获取达人主页信息")
            print("示例链接: https://www.tiktok.com/@jiaozi_2004\n")
            url = input("请粘贴达人主页链接: ").strip()

            if not url:
                print("⚠️ 链接不能为空！")
                continue

            print(f"\n⏳ 正在抓取达人信息... ({url})")
            result = crawler.extract_influencer(url)
            display_influencer_info(result)

        elif choice == '2':
            print_separator()
            print("功能2: 获取视频数据")
            print("示例链接: https://www.tiktok.com/@jiaozi_2004/video/7570315858824957204\n")
            url = input("请粘贴视频链接: ").strip()

            if not url:
                print("⚠️ 链接不能为空！")
                continue

            print(f"\n⏳ 正在抓取视频数据... ({url})")
            result = crawler.extract_video(url)
            display_video_info(result)

        elif choice == '3':
            print("\n👋 感谢使用，再见！")
            break
        else:
            print("⚠️ 无效选项，请重新输入！")

        input("\n按回车键继续...")


if __name__ == "__main__":
    main()
