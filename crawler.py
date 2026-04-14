import yt_dlp
from typing import Dict, Optional
import time
import random
import os


class TopFlowCrawler:
    def __init__(self, proxy: str = None, cookies_file: str = None):
        self.proxy = proxy
        self.cookies_file = cookies_file
        self.last_error = None
        self._base_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': False,
            'nocheckcertificate': True,
            'socket_timeout': 30,
            'retries': 3,
            'format': 'worst',
        }

        if proxy:
            self._base_opts['proxy'] = proxy

    def _get_opts(self, url: str = '') -> dict:
        opts = dict(self._base_opts)
        platform = self._detect_platform(url) if url else ''

        if platform == 'youtube':
            opts.update({
                'extract_flat': False,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                    }
                },
            })
        else:
            opts['user_agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

        if self.cookies_file and os.path.exists(self.cookies_file):
            opts['cookiefile'] = self.cookies_file

        return opts

    def _rate_limit(self):
        time.sleep(random.uniform(0.5, 1.5))

    def _retry_with_backoff(self, func, max_retries: int = 3, url: str = ""):
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    wait_time = min(2 ** attempt + random.uniform(0, 1), 15)
                    print(f"    ⏳ 第 {attempt}/{max_retries} 次重试... (等待 {wait_time:.1f}s)")
                    time.sleep(wait_time)

                result = func()
                if result:
                    return result

            except Exception as e:
                last_error = e
                error_msg = str(e).lower()

                if 'sign in' in error_msg or 'login' in error_msg or 'bot' in error_msg:
                    print(f"    ⚠️ 需要登录/被识别为机器人 (尝试 {attempt}/{max_retries})")
                elif 'ssl' in error_msg or 'certificate' in error_msg:
                    print(f"    ⚠️ SSL错误 (尝试 {attempt}/{max_retries})")
                elif 'timeout' in error_msg or 'timed out' in error_msg:
                    print(f"    ⚠️ 连接超时 (尝试 {attempt}/{max_retries})")
                elif 'remote end closed' in error_msg or 'connection' in error_msg:
                    print(f"    ⚠️ 连接中断 (尝试 {attempt}/{max_retries})")
                else:
                    print(f"    ⚠️ 错误: {str(e)[:100]} (尝试 {attempt}/{max_retries})")

        raise last_error

    def extract_influencer(self, homepage_url: str) -> Optional[Dict]:
        self._rate_limit()
        opts = self._get_opts(homepage_url)

        def _do_extract():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(homepage_url, download=False)

        try:
            info = self._retry_with_backoff(_do_extract, max_retries=3, url=homepage_url)

            display_name = info.get('uploader') or info.get('channel', '')

            if not display_name and 'entries' in info and info['entries']:
                first_entry = info['entries'][0]
                if first_entry:
                    display_name = first_entry.get('uploader', '')

            username_from_url = ''
            if '@' in homepage_url:
                username_from_url = '@' + homepage_url.split('@')[1].split('/')[0]

            tiktok_id = info.get('uploader_id') or info.get('channel_id', '')
            if not tiktok_id and 'entries' in info and info['entries']:
                first_entry = info['entries'][0]
                if first_entry:
                    tiktok_id = first_entry.get('uploader_id', '')

            fans_count = info.get('channel_follower_count', 0) or 0

            if fans_count == 0 and 'entries' in info:
                for entry in info['entries'][:10]:
                    if entry:
                        follower_count = entry.get('channel_follower_count', 0) or entry.get('like_count', 0)
                        if follower_count > 100:
                            fans_count = follower_count
                            break

            video_count = info.get('playlist_count', 0) or info.get('entry_count', 0) or 0
            signature = info.get('description', '') or ''
            avatar_url = info.get('thumbnail', '') or ''

            if not avatar_url and 'entries' in info and info['entries']:
                for entry in info['entries'][:5]:
                    if entry and entry.get('thumbnail'):
                        avatar_url = entry.get('thumbnail', '')
                        break

            return {
                "account_name": display_name,
                "username": username_from_url or display_name,
                "tiktok_id": tiktok_id,
                "fans_count": fans_count,
                "video_count": video_count,
                "signature": signature[:200] if signature else '',
                "avatar_url": avatar_url,
                "platform": self._detect_platform(homepage_url),
                "homepage_url": homepage_url
            }

        except Exception as e:
            error_str = str(e)
            print(f"\n[爬虫错误] 达人数据抓取失败")
            print(f"  URL: {homepage_url}")
            print(f"  原因: {error_str[:200]}")

            if any(keyword in error_str.lower() for keyword in ['ssl', 'certificate', 'eof', 'remote end']):
                print("\n💡 可能的原因:")
                print("  • 网络连接不稳定，请稍后重试")
                print("  • TikTok服务器暂时不可用")
                print("  • 如频繁出现，建议使用代理/VPN")

            return None

    def extract_video(self, video_url: str) -> Optional[Dict]:
        self._rate_limit()
        opts = self._get_opts(video_url)
        platform = self._detect_platform(video_url)
        print(f"🔍 开始抓取视频: platform={platform}, url={video_url}")
        print(f"   cookies: {opts.get('cookiefile', '无')}, player_client: {opts.get('extractor_args', {}).get('youtube', {}).get('player_client', 'default')}")

        def _do_extract():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(video_url, download=False)

        def _build_result(info):
            return {
                "influencer_name": info.get('uploader') or info.get('channel', ''),
                "video_title": info.get('title', ''),
                "publish_date": info.get('upload_date', ''),
                "play_count": info.get('view_count', 0),
                "like_count": info.get('like_count', 0),
                "comment_count": info.get('comment_count', 0),
                "share_count": info.get('repost_count', 0),
                "platform": platform,
                "video_url": video_url
            }

        try:
            info = self._retry_with_backoff(_do_extract, max_retries=3, url=video_url)
            result = _build_result(info)
            print(f"✅ 抓取成功: {result.get('influencer_name', 'N/A')} - 播放:{result.get('play_count', 0)}")
            self.last_error = None
            return result

        except Exception as e:
            error_str = str(e)
            self.last_error = error_str
            print(f"\n[爬虫错误] 视频数据抓取失败")
            print(f"  URL: {video_url}")
            print(f"  原因: {error_str[:300]}")

            if 'sign in' in error_str.lower() or 'bot' in error_str.lower():
                print("\n💡 被识别为机器人，尝试使用ios客户端重试...")
                try:
                    ios_opts = dict(self._base_opts)
                    ios_opts.update({
                        'extract_flat': False,
                        'extractor_args': {
                            'youtube': {
                                'player_client': ['ios'],
                            }
                        },
                    })
                    if self.cookies_file and os.path.exists(self.cookies_file):
                        ios_opts['cookiefile'] = self.cookies_file
                    with yt_dlp.YoutubeDL(ios_opts) as ydl:
                        info = ydl.extract_info(video_url, download=False)
                    result = _build_result(info)
                    print(f"✅ ios客户端抓取成功: {result.get('influencer_name', 'N/A')}")
                    self.last_error = None
                    return result
                except Exception as e2:
                    self.last_error = str(e2)
                    print(f"  ios客户端也失败: {str(e2)[:200]}")

                if self.cookies_file and os.path.exists(self.cookies_file):
                    print(f"\n💡 使用cookies重试...")
                    try:
                        cookie_opts = dict(self._base_opts)
                        cookie_opts.update({
                            'extract_flat': False,
                            'cookiefile': self.cookies_file,
                        })
                        with yt_dlp.YoutubeDL(cookie_opts) as ydl:
                            info = ydl.extract_info(video_url, download=False)
                        result = _build_result(info)
                        print(f"✅ cookies抓取成功: {result.get('influencer_name', 'N/A')}")
                        self.last_error = None
                        return result
                    except Exception as e3:
                        self.last_error = str(e3)
                        print(f"  cookies重试也失败: {str(e3)[:200]}")

            if 'format' in error_str.lower():
                print("\n💡 格式不可用，尝试使用更宽松的格式选项...")
                try:
                    fallback_opts = dict(opts)
                    fallback_opts['format'] = 'worst/worstvideo+worstaudio/best'
                    with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                        info = ydl.extract_info(video_url, download=False)
                    result = _build_result(info)
                    print(f"✅ 回退抓取成功: {result.get('influencer_name', 'N/A')}")
                    self.last_error = None
                    return result
                except Exception as e2:
                    self.last_error = str(e2)
                    print(f"  回退也失败: {str(e2)[:200]}")

            return None

    def _detect_platform(self, url: str) -> str:
        if 'tiktok.com' in url:
            return 'tiktok'
        elif 'instagram.com' in url:
            return 'ins'
        elif 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        else:
            return 'unknown'


def create_crawler(proxy: str = None) -> TopFlowCrawler:
    return TopFlowCrawler(proxy=proxy)


crawler = TopFlowCrawler()
