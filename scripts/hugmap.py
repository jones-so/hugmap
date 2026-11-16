#!/usr/bin/env python3
"""巨图引擎标准库客户端。密钥仅通过环境变量读取，不随跨域下载转发。"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ORIGIN = 'https://www.hugmap.com'

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def request(path, method='GET', params=None, key=None):
    url = ORIGIN + path + ('?' + urllib.parse.urlencode(params) if params else '')
    headers = {'Accept': 'application/json'}
    if key:
        headers['X-API-Key'] = key
    try:
        response = urllib.request.build_opener(NoRedirect).open(
            urllib.request.Request(url, headers=headers, method=method), timeout=120)
        return response
    except urllib.error.HTTPError as error:
        if error.code in (301, 302, 303, 307, 308):
            return error
        try:
            message = json.loads(error.read()).get('error', '请求失败')
        except (ValueError, AttributeError):
            message = '请求失败'
        # 错误正文不包含请求头；不要输出密钥或签名下载 URL。
        raise RuntimeError('HTTP %s: %s' % (error.code, message)) from None

def download(args, key):
    destination = Path(args.output)
    if destination.exists():
        raise RuntimeError('输出文件已存在，请选择其他路径')
    path = '/api/v1/opportunities/%s/attachments/%s/download' % (
        urllib.parse.quote(args.id, safe=''), urllib.parse.quote(args.attachment_id, safe=''))
    with request(path, params={'redirect': 'false'}, key=key) as response:
        delivery = json.load(response)
    if delivery.get('requiresVerification'):
        raise RuntimeError('该附件要求在官方页面完成验证，请访问公告详情中的官方入口')
    target = urllib.parse.urljoin(ORIGIN, delivery['downloadUrl'])
    parsed = urllib.parse.urlsplit(target)
    if parsed.scheme != 'https' or parsed.username or parsed.password:
        raise RuntimeError('下载地址不符合 HTTPS 交付要求')
    # 全新请求，不将 X-API-Key 转发到官方站点、OSS 或一次性交付地址。
    partial = destination.with_name(destination.name + '.' + os.urandom(6).hex() + '.part')
    try:
        with urllib.request.urlopen(target, timeout=120) as response, partial.open('xb') as stream:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                stream.write(chunk)
        # link 的目标已存在时失败，避免下载过程中覆盖用户新建的文件。
        os.link(partial, destination)
        partial.unlink()
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    return {'savedTo': str(destination)}

def main(argv=None):
    parser = argparse.ArgumentParser(description='巨图引擎 API / Skill 客户端（北京时间每日 100 次）')
    commands = parser.add_subparsers(dest='command', required=True)
    search = commands.add_parser('search', help='检索公告')
    search.add_argument('--query')
    search.add_argument('--region')
    search.add_argument('--category')
    search.add_argument('--limit', type=int, default=25)
    search.add_argument('--cursor')
    search.add_argument('--filter', action='append', default=[], metavar='NAME=VALUE')
    detail = commands.add_parser('detail', help='完整详情'); detail.add_argument('id')
    file = commands.add_parser('download', help='下载附件'); file.add_argument('id'); file.add_argument('attachment_id'); file.add_argument('--output', required=True)
    for name in ('dictionaries', 'metrics', 'usage'):
        commands.add_parser(name)
    watchlist = commands.add_parser('watchlist', help='查询个人关注'); watchlist.add_argument('--cursor'); watchlist.add_argument('--limit', type=int, default=25)
    for name in ('follow', 'unfollow'):
        command = commands.add_parser(name); command.add_argument('id')
    args = parser.parse_args(argv)
    key = os.environ.get('HUGMAP_API_KEY', '').strip()
    if args.command in ('watchlist', 'follow', 'unfollow') and not key:
        parser.error('个人关注需要设置环境变量 HUGMAP_API_KEY')
    if args.command == 'download':
        result = download(args, key)
    else:
        path = '/api/v1/' + ('opportunities' if args.command in ('search', 'detail') else args.command)
        method = 'GET'; params = {}
        if args.command == 'search':
            params = {name: getattr(args, name) for name in ('query', 'region', 'category', 'limit', 'cursor') if getattr(args, name) is not None}
            for entry in args.filter:
                name, separator, value = entry.partition('=')
                if not separator or not name:
                    parser.error('--filter 必须为 NAME=VALUE')
                params[name] = value
        elif args.command == 'detail':
            path += '/' + urllib.parse.quote(args.id, safe='')
        elif args.command == 'watchlist':
            params = {'limit': args.limit}
            if args.cursor: params['cursor'] = args.cursor
        elif args.command in ('follow', 'unfollow'):
            path = '/api/v1/watchlist/' + urllib.parse.quote(args.id, safe='')
            method = 'PUT' if args.command == 'follow' else 'DELETE'
        with request(path, method, params, key) as response:
            result = json.load(response)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, urllib.error.URLError, OSError) as error:
        print(str(error) if isinstance(error, RuntimeError) else '网络或文件操作失败，请检查连接与输出路径', file=sys.stderr)
        sys.exit(1)
