import yt_dlp
from typing import Dict, Optional
import time
import random


class TopFlowCrawler:
    def __init__(self, proxy: str = None):
        self.proxy = proxy
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': False,
            'nocheckcertificate': True,
            'socket_timeout': 60,
            'retries': 5,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'extractor_args': {
                'tiktok': {
                    'api_hostname': ['api16-normal-c-useast1a.tiktokv.com']
                }
            }
        }

        if proxy:
            self.ydl_opts['proxy'] = proxy

    def _rate_limit(self):
        """请求频率限制"""
        time.sleep(random.uniform(1, 3))

    def _retry_with_backoff(self, func, max_retries: int = 3, url: str = ""):
        """带指数退避的重试机制"""
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    wait_time = min(2 ** attempt + random.uniform(0, 2), 30)
                    print(f"    ⏳ 第 {attempt}/{max_retries} 次重试... (等待 {wait_time:.1f}s)")
                    time.sleep(wait_time)
                
                result = func()
                if result:
                    return result
                    
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                if 'ssl' in error_msg or 'certificate' in error_msg:
                    print(f"    ⚠️ SSL错误 (尝试 {attempt}/{max_retries})")
                elif 'timeout' in error_msg or 'timed out' in error_msg:
                    print(f"    ⚠️ 连接超时 (尝试 {attempt}/{max_retries})")
                elif 'remote end closed' in error_msg or 'connection' in error_msg:
                    print(f"    ⚠️ 连接中断 (尝试 {attempt}/{max_retries})")
                else:
                    print(f"    ⚠️ 错误: {str(e)[:100]} (尝试 {attempt}/{max_retries})")
        
        raise last_error

    def extract_influencer(self, homepage_url: str) -> Optional[Dict]:
        """达人主页数据抓取（带自动重试）"""
        self._rate_limit()
        
        def _do_extract():
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
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
        """视频数据抓取（带自动重试）"""
        self._rate_limit()
        
        def _do_extract():
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                return ydl.extract_info(video_url, download=False)

        try:
            info = self._retry_with_backoff(_do_extract, max_retries=3, url=video_url)
            
            return {
                "influencer_name": info.get('uploader', ''),
                "video_title": info.get('title', ''),
                "publish_date": info.get('upload_date', ''),
                "play_count": info.get('view_count', 0),
                "like_count": info.get('like_count', 0),
                "comment_count": info.get('comment_count', 0),
                "share_count": info.get('repost_count', 0),
                "platform": self._detect_platform(video_url),
                "video_url": video_url
            }
            
        except Exception as e:
            error_str = str(e)
            print(f"\n[爬虫错误] 视频数据抓取失败")
            print(f"  URL: {video_url}")
            print(f"  原因: {error_str[:200]}")
            
            if any(keyword in error_str.lower() for keyword in ['ssl', 'certificate', 'eof', 'remote end']):
                print("\n💡 建议: 稍后重试或检查网络连接")
            
            return None

    def _detect_platform(self, url: str) -> str:
        """自动识别平台"""
        if 'tiktok.com' in url:
            return 'tiktok'
        elif 'instagram.com' in url:
            return 'ins'
        elif 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        else:
            return 'unknown'


def create_crawler(proxy: str = None) -> TopFlowCrawler:
    """创建爬虫实例（支持代理配置）"""
    return TopFlowCrawler(proxy=proxy)


crawler = TopFlowCrawler()
