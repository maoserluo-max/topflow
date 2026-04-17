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

    def _fetch_instagram_play_count(self, video_url: str, cookies_content: str = '') -> int:
        """通过多种方式补充获取 Instagram 播放量
        
        yt-dlp 在未登录和已登录路径下都可能不返回 Instagram 的播放量。
        依次尝试以下方案：
        A. GraphQL API（带 csrftoken 和 cookies）
        B. 使用 yt-dlp 重新提取（带 cookies，走登录路径获取 view_count）
        """
        # 从 URL 中提取 shortcode
        match = re.search(r'instagram\.com/(?:p|reels?|tv)/([^/?#&]+)', video_url)
        if not match:
            print(f"  Instagram: 无法从 URL 提取 shortcode: {video_url}")
            return 0
        shortcode = match.group(1)
        print(f"  Instagram: 开始补充获取 shortcode={shortcode} 的播放量...")

        # 方案A: GraphQL API（带 csrftoken）
        play_count = self._ig_graphql_play_count(shortcode, video_url, cookies_content)
        if play_count:
            return play_count

        # 方案B: 使用 yt-dlp 带.cookies 重新提取
        if cookies_content and cookies_content.strip():
            print(f"  Instagram: GraphQL 未获取到播放量，尝试使用 yt-dlp + cookies 重新提取...")
            play_count = self._ig_ytdlp_with_cookies(video_url, cookies_content)
            if play_count:
                return play_count

        print(f"  Instagram: 所有补充获取方案均未获取到播放量")
        return 0

    def _ig_graphql_play_count(self, shortcode: str, video_url: str, cookies_content: str = '') -> int:
        """方案A: 通过 Instagram GraphQL API 获取播放量"""
        try:
            import ssl
            from urllib.request import Request, urlopen
            from urllib.parse import urlencode
            from http.cookiejar import CookieJar

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            # 第一步：先访问 Instagram 页面获取 csrftoken
            csrf_token = ''
            cookie_header = ''
            ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

            try:
                homepage_req = Request('https://www.instagram.com/', headers={
                    'User-Agent': ua,
                    'Accept': 'text/html,application/xhtml+xml',
                })
                with urlopen(homepage_req, timeout=10, context=ctx) as resp:
                    set_cookies = resp.headers.get_all('Set-Cookie') or []
                    for sc in set_cookies:
                        if 'csrftoken=' in sc:
                            csrf_token = sc.split('csrftoken=')[1].split(';')[0]
                            break
            except Exception as e:
                print(f"  Instagram GraphQL: 获取 csrftoken 失败: {str(e)[:80]}")

            # 解析用户提供的 cookies
            user_cookies = ''
            if cookies_content and cookies_content.strip():
                user_cookies = self._parse_cookies_to_header(cookies_content)

            # 构建 Cookie 头：合并 csrftoken 和用户 cookies
            cookie_parts = []
            if csrf_token:
                cookie_parts.append(f'csrftoken={csrf_token}')
            if user_cookies:
                cookie_parts.append(user_cookies)
            cookie_header = '; '.join(cookie_parts)

            # 第二步：请求 GraphQL API
            variables = {
                'shortcode': shortcode,
                'child_comment_count': 3,
                'fetch_comment_count': 40,
                'parent_comment_count': 24,
                'has_threaded_comments': True,
            }
            query_params = urlencode({
                'doc_id': '8845758582119845',
                'variables': json.dumps(variables, separators=(',', ':')),
            })
            api_url = f'https://www.instagram.com/graphql/query/?{query_params}'
            headers = {
                'User-Agent': ua,
                'X-IG-App-ID': '936619743392459',
                'X-ASBD-ID': '198387',
                'X-IG-WWW-Claim': '0',
                'Origin': 'https://www.instagram.com',
                'Accept': '*/*',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': video_url,
            }
            if csrf_token:
                headers['X-CSRFToken'] = csrf_token
            if cookie_header:
                headers['Cookie'] = cookie_header

            req = Request(api_url, headers=headers)
            with urlopen(req, timeout=15, context=ctx) as resp:
                if resp.status != 200:
                    print(f"  Instagram GraphQL API 返回 {resp.status}")
                    return 0
                body = resp.read().decode('utf-8')

            data = json.loads(body)
            media = data.get('data', {}).get('xdt_shortcode_media', {})
            if not media:
                print(f"  Instagram GraphQL: 无 xdt_shortcode_media, keys={list(data.get('data', {}).keys())}")
                return 0

            play_count = (
                media.get('video_play_count')
                or media.get('video_view_count')
                or 0
            )
            if play_count:
                print(f"  Instagram GraphQL: 获取播放量成功: {play_count}")
            else:
                debug_keys = [k for k in media.keys() if any(w in k.lower() for w in ['view', 'play', 'count'])]
                print(f"  Instagram GraphQL: 未找到播放量, 相关键: {debug_keys}")
            return play_count

        except Exception as e:
            print(f"  Instagram GraphQL: 失败 {type(e).__name__}: {str(e)[:150]}")
            return 0

    def _ig_ytdlp_with_cookies(self, video_url: str, cookies_content: str) -> int:
        """方案B: 使用 yt-dlp 带 cookies 重新提取 Instagram 视频信息
        当有 cookies（特别是 sessionid）时，yt-dlp 会走 Instagram 的登录路径，
        在 _extract_product 方法中获取 view_count。
        """
        try:
            opts = dict(self._base_opts)
            opts['user_agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            if cookies_content and cookies_content.strip():
                opts['cookiefile'] = self._write_temp_cookies(cookies_content)

            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)

                if info:
                    # 从 yt-dlp 的 info 中获取播放量
                    play_count = (
                        info.get('view_count')
                        or info.get('play_count')
                        or info.get('video_view_count')
                        or 0
                    )
                    if play_count:
                        print(f"  Instagram yt-dlp+cookies: 获取播放量成功: {play_count}")
                    else:
                        print(f"  Instagram yt-dlp+cookies: 播放量仍为空 (view_count={info.get('view_count')}, play_count={info.get('play_count')})")
                    return play_count
            finally:
                self._cleanup_cookies(opts)

        except Exception as e:
            print(f"  Instagram yt-dlp+cookies: 失败 {str(e)[:150]}")
            return 0

    def _parse_cookies_to_header(self, cookies_content: str) -> str:
        """将 Netscape 格式的 cookies 文件内容解析为 HTTP Cookie 头"""
        parts = []
        for line in cookies_content.strip().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            fields = line.split('\t')
            if len(fields) >= 7:
                name = fields[5].strip()
                value = fields[6].strip()
                if name and value:
                    parts.append(f'{name}={value}')
        return '; '.join(parts) if parts else ''

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

            # Instagram: yt-dlp 在未登录和已登录路径下都可能不返回播放量
            # 未登录: extractor 不返回 view_count
            # 已登录: _extract_product 返回 view_count，但 Instagram API 对 reels 可能返回 None
            # 通过 GraphQL API 补充获取
            if platform == 'ins' and not result.get('play_count'):
                print(f"  Instagram 播放量为空，尝试通过 GraphQL API 补充获取...")
                extra_play = self._fetch_instagram_play_count(video_url, cookies_content)
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

            # Instagram 被 rate limit 时，yt-dlp 直接抛异常，但我们仍可尝试 GraphQL 补充
            if platform == 'ins' and ('rate-limit' in error_str.lower() or 'login' in error_str.lower()):
                print(f"  Instagram: yt-dlp 被 rate limit，尝试通过 GraphQL API 获取基础数据...")
                ig_match = re.search(r'instagram\.com/(?:p|reels?|tv)/([^/?#&]+)', video_url)
                if ig_match:
                    try:
                        extra_play = self._ig_graphql_play_count(ig_match.group(1), video_url, cookies_content)
                        if extra_play:
                            # 即使 yt-dlp 失败，GraphQL 仍可获取播放量
                            result = {
                                "influencer_name": '',
                                "video_title": '',
                                "publish_date": '',
                                "play_count": extra_play,
                                "like_count": 0,
                                "comment_count": 0,
                                "share_count": 0,
                                "platform": platform,
                                "video_url": video_url
                            }
                            print(f"✅ Instagram GraphQL 兜底成功: 播放:{extra_play}")
                            self.last_error = None
                            return result
                        else:
                            print(f"  Instagram GraphQL 兜底也未获取到播放量")
                    except Exception as e2:
                        print(f"  Instagram GraphQL 兜底失败: {str(e2)[:100]}")

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
