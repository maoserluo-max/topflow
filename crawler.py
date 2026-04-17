import yt_dlp
from typing import Dict, Optional
import time
import random
import os
import tempfile
import re
import json


class TopFlowCrawler:
    def __init__(self, proxy: str = None):
        self.proxy = proxy
        self.last_error = None
        self._base_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': False,
            'nocheckcertificate': True,
            'socket_timeout': 30,
            'retries': 3,
        }

        if proxy:
            self._base_opts['proxy'] = proxy

    def _get_opts(self, url: str = '', cookies_content: str = '') -> dict:
        opts = dict(self._base_opts)
        platform = self._detect_platform(url) if url else ''

        if platform == 'youtube':
            opts.update({
                'extract_flat': False,
                # 不再硬编码 player_client，让 yt-dlp 自动选择可用客户端
                # 避免因缺少 PO Token 导致格式不可用
            })
            # 尝试配置 deno 运行时路径（解决 YouTube n challenge）
            deno_path = self._find_deno()
            if deno_path:
                opts['js_runtimes'] = {'deno': {'path': deno_path}}
        else:
            opts['user_agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

        if cookies_content and cookies_content.strip():
            opts['cookiefile'] = self._write_temp_cookies(cookies_content)

        return opts

    def _find_deno(self) -> str:
        """查找 deno 可执行文件路径"""
        import shutil
        # 1. 直接在 PATH 中查找
        deno = shutil.which('deno')
        if deno:
            return deno
        # 2. 常见安装路径
        import os
        common_paths = [
            os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WinGet\Packages\DenoLand.Deno_Microsoft.Winget.Source_8wekyb3d8bbwe\deno.exe'),
            os.path.expanduser('~/.deno/bin/deno.exe'),
            r'C:\Program Files\Deno\deno.exe',
        ]
        for p in common_paths:
            # 使用 glob 模式匹配 WinGet 的包目录名
            if '*' in p:
                import glob
                matches = glob.glob(p)
                if matches:
                    return matches[0]
            elif os.path.isfile(p):
                return p
        # 3. 在 WinGet Packages 下模糊搜索
        winget_dir = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WinGet\Packages')
        if os.path.isdir(winget_dir):
            for d in os.listdir(winget_dir):
                if d.lower().startswith('denoland'):
                    candidate = os.path.join(winget_dir, d, 'deno.exe')
                    if os.path.isfile(candidate):
                        return candidate
        return ''

    def _fetch_instagram_play_count(self, video_url: str) -> int:
        """通过 Instagram GraphQL API 补充获取播放量
        
        yt-dlp 在未登录状态下不返回 Instagram 的播放量，
        因为 yt-dlp 的 Instagram extractor 在非登录路径中遗漏了 view_count 字段。
        GraphQL API 返回 video_play_count（更准确）和 video_view_count。
        """
        try:
            import requests as req
            # 从 URL 中提取 shortcode
            match = re.search(r'instagram\.com/(?:p|reels?|tv)/([^/?#&]+)', video_url)
            if not match:
                return 0
            shortcode = match.group(1)

            variables = {
                'shortcode': shortcode,
                'child_comment_count': 3,
                'fetch_comment_count': 40,
                'parent_comment_count': 24,
                'has_threaded_comments': True,
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'X-IG-App-ID': '936619743392459',
                'X-ASBD-ID': '198387',
                'X-IG-WWW-Claim': '0',
                'Origin': 'https://www.instagram.com',
                'Accept': '*/*',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': video_url,
            }
            r = req.get(
                'https://www.instagram.com/graphql/query/',
                headers=headers,
                params={
                    'doc_id': '8845758582119845',
                    'variables': json.dumps(variables, separators=(',', ':')),
                },
                timeout=15,
            )
            if r.status_code != 200:
                print(f"  Instagram GraphQL API 返回 {r.status_code}")
                return 0

            data = r.json()
            media = data.get('data', {}).get('xdt_shortcode_media', {})
            if not media:
                return 0

            # video_play_count 是 reels 的播放次数（更准确）
            # video_view_count 是视频观看次数
            play_count = (
                media.get('video_play_count')
                or media.get('video_view_count')
                or 0
            )
            if play_count:
                print(f"  Instagram GraphQL 补充获取播放量: {play_count}")
            return play_count

        except Exception as e:
            print(f"  Instagram GraphQL 补充获取播放量失败: {str(e)[:100]}")
            return 0

    def _write_temp_cookies(self, content: str) -> str:
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, prefix='ydl_cookies_')
        tmp.write(content)
        tmp.close()
        return tmp.name

    def _cleanup_cookies(self, opts: dict):
        cookiefile = opts.get('cookiefile')
        if cookiefile and os.path.exists(cookiefile) and 'ydl_cookies_' in cookiefile:
            try:
                os.unlink(cookiefile)
            except Exception:
                pass

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

    def extract_influencer(self, homepage_url: str, cookies_content: str = '') -> Optional[Dict]:
        self._rate_limit()
        opts = self._get_opts(homepage_url, cookies_content)

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
            return None

        finally:
            self._cleanup_cookies(opts)

    def extract_video(self, video_url: str, cookies_content: str = '') -> Optional[Dict]:
        self._rate_limit()
        opts = self._get_opts(video_url, cookies_content)
        platform = self._detect_platform(video_url)
        print(f"🔍 开始抓取视频: platform={platform}, url={video_url}")
        print(f"   cookies: {'有' if cookies_content and cookies_content.strip() else '无'}, player_client: {opts.get('extractor_args', {}).get('youtube', {}).get('player_client', 'default')}")

        def _do_extract():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(video_url, download=False)

        def _build_result(info):
            # Instagram 播放数字段可能在不同位置
            # view_count 是标准字段，但 Instagram 可能返回 play_count 或 video_view_count
            play_count = (
                info.get('view_count')
                or info.get('play_count')
                or info.get('video_view_count')
                or 0
            )
            return {
                "influencer_name": info.get('uploader') or info.get('channel', ''),
                "video_title": info.get('title', ''),
                "publish_date": info.get('upload_date', ''),
                "play_count": play_count,
                "like_count": info.get('like_count', 0),
                "comment_count": info.get('comment_count', 0),
                "share_count": info.get('repost_count', 0),
                "platform": platform,
                "video_url": video_url
            }

        try:
            info = self._retry_with_backoff(_do_extract, max_retries=3, url=video_url)
            result = _build_result(info)

            # Instagram: yt-dlp 未登录时不返回播放量，通过 GraphQL API 补充
            if platform == 'ins' and not result.get('play_count'):
                extra_play = self._fetch_instagram_play_count(video_url)
                if extra_play:
                    result['play_count'] = extra_play

            print(f"✅ 抓取成功: {result.get('influencer_name', 'N/A')} - 播放:{result.get('play_count', 0)}")
            self.last_error = None
            return result

        except Exception as e:
            error_str = str(e)
            self.last_error = error_str
            print(f"\n[爬虫错误] 视频数据抓取失败")
            print(f"  URL: {video_url}")
            print(f"  原因: {error_str[:300]}")

            if platform == 'youtube':
                # YouTube 格式不可用时，依次尝试不同 player_client
                fallback_clients = [
                    ['ios'], ['mweb'], ['android'],
                    ['web'], ['web_safari', 'ios'],
                ]
                for clients in fallback_clients:
                    client_name = ','.join(clients)
                    print(f"\n💡 尝试使用 {client_name} 客户端重试...")
                    try:
                        fallback_opts = dict(self._base_opts)
                        fallback_opts.update({
                            'extract_flat': False,
                            'extractor_args': {
                                'youtube': {
                                    'player_client': clients,
                                }
                            },
                        })
                        deno_path = self._find_deno()
                        if deno_path:
                            fallback_opts['js_runtimes'] = {'deno': {'path': deno_path}}
                        if cookies_content and cookies_content.strip():
                            fallback_opts['cookiefile'] = self._write_temp_cookies(cookies_content)
                        with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                            info = ydl.extract_info(video_url, download=False)
                        result = _build_result(info)
                        print(f"✅ {client_name} 客户端抓取成功: {result.get('influencer_name', 'N/A')}")
                        self.last_error = None
                        self._cleanup_cookies(fallback_opts)
                        return result
                    except Exception as e2:
                        print(f"  {client_name} 客户端也失败: {str(e2)[:200]}")
                        self._cleanup_cookies(fallback_opts)
                        continue
            elif 'sign in' in error_str.lower() or 'bot' in error_str.lower():
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
                    if cookies_content and cookies_content.strip():
                        ios_opts['cookiefile'] = self._write_temp_cookies(cookies_content)
                    with yt_dlp.YoutubeDL(ios_opts) as ydl:
                        info = ydl.extract_info(video_url, download=False)
                    result = _build_result(info)
                    print(f"✅ ios客户端抓取成功: {result.get('influencer_name', 'N/A')}")
                    self.last_error = None
                    self._cleanup_cookies(ios_opts)
                    return result
                except Exception as e2:
                    self.last_error = str(e2)
                    print(f"  ios客户端也失败: {str(e2)[:200]}")
                    self._cleanup_cookies(ios_opts)

            return None

        finally:
            self._cleanup_cookies(opts)

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


crawler = create_crawler()
