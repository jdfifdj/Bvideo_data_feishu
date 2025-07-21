import requests
import time
import hashlib
import urllib.parse
import json
from typing import Dict, Tuple
from runtime import Args
from typings.a11.a11 import Input, Output

# WBI签名生成相关常量
WBI_KEY = "560c52ccd288fed22173431c70775f83b407c0dfe424485a8e41741f14a3b87e"

def get_wts() -> int:
    """生成WTS时间戳（当前时间戳秒级）"""
    return int(time.time())

def get_mixin_key(orig: str) -> str:
    """对WBI_KEY进行字符混合，生成mixin_key"""
    return ''.join([orig[i] for i in [46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52]])

def get_w_rid(params: Dict[str, str], mixin_key: str) -> str:
    """生成W_RID签名"""
    # 对参数进行排序
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    # 拼接参数为字符串
    query = urllib.parse.urlencode(sorted_params)
    # 拼接mixin_key并计算MD5
    return hashlib.md5((query + mixin_key).encode()).hexdigest()

def generate_wbi_signature(params: Dict[str, str]) -> Tuple[int, str]:
    """生成WBI签名（wts和w_rid）"""
    wts = get_wts()
    mixin_key = get_mixin_key(WBI_KEY)
    # 添加wts到参数中
    params_with_wts = {**params, "wts": str(wts)}
    w_rid = get_w_rid(params_with_wts, mixin_key)
    return wts, w_rid


def timestamp_to_date(timestamp, format_str="%Y/%m/%d %H:%M:%S"):
    """
    将时间戳转换为指定格式的日期字符串
    
    参数:
        timestamp: 时间戳（秒级或毫秒级）
        format_str: 日期格式字符串，默认为"%Y/%m/%d"
    
    返回:
        格式化后的日期字符串
    """
    # 处理毫秒级时间戳
    if timestamp > 9999999999:
        timestamp = timestamp / 1000
    
    # 转换为时间元组
    time_tuple = time.localtime(timestamp)
    
    # 格式化为字符串
    return time.strftime(format_str, time_tuple)

def check_and_divide(number):
    if number == 0:
        return 0
    else:
        return number / 10000


def get_current_timestamp(milliseconds=False):
    """
    获取当前时间戳
    
    参数:
        milliseconds: 是否返回毫秒级时间戳，默认为False（秒级）
    
    返回:
        当前时间戳
    """
    timestamp = time.time()
    return int(timestamp * 1000) if milliseconds else int(timestamp)

def get_video_stats(SESSDATA: str, bvid: str, wts: str, w_rid: str):
    """
    获取视频统计数据
    :param SESSDATA: 用户登录凭证
    :param bvid: 视频BV号
    :param wts: WBI签名时间戳
    :param w_rid: WBI签名结果
    :return: 格式化后的视频统计数据
    """

    # 准备API请求参数
    params = {
        'bvid': bvid
    }
    
    # 使用传入的wts和w_rid作为签名参数
    params['wts'] = wts
    params['w_rid'] = w_rid
    signed_params = params
    
    # 添加SESSDATA、wts和w_rid到headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.bilibili.com/',
        'Cookie': f'SESSDATA={SESSDATA}; wts={wts}; w_rid={w_rid}; bili_jct={SESSDATA.split('%')[0]}'
    }
    
    # 调用统计API
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.bilibili.com/',
        'Cookie': f'SESSDATA={SESSDATA}; wts={wts}; w_rid={w_rid}'
    }
    
    # 使用视频诊断比较API
    api_url = 'https://member.bilibili.com/x/web/data/archive_diagnose/compare'
    response = requests.get(api_url, params=signed_params, headers=headers)
    response.raise_for_status()
    
    # 检查API响应
    try:
        json_data = response.json()
        if not json_data:
            raise ValueError('API返回空响应')
        if 'code' in json_data and json_data['code'] != 0:
            raise ValueError(f'API返回错误: {json_data.get("message", "未知错误")}')
        if 'data' not in json_data:
            raise ValueError('API响应缺少data字段')
        if 'list' not in json_data['data']:
            raise ValueError('API响应data中缺少list字段')
        if len(json_data['data']['list']) == 0:
            raise ValueError('API响应数据列表为空')
    except ValueError as e:
        raise ValueError(f'API响应解析失败: {str(e)}')
        
    # 提取第一个视频数据
    video_data = json_data['data']['list'][0]
    
    # 获取stat字段数据
    stat_data = video_data.get('stat', {})

    #处理时间戳
    timedate = timestamp_to_date(video_data.get('pubtime'),"%Y/%m/%d %H:%M:%S")
    timedate2 = timestamp_to_date(get_current_timestamp(False),"%Y/%m/%d %H:%M:%S")




    
    # 格式化输出
    fields = {
        #'bvid': video_data.get('bvid', ''),
        "bvid": video_data.get('bvid', ''),
        'cover': video_data.get('cover', ''),
        #"封面网址":video_data.get('cover', ''),
        'title': video_data.get('title', ''),
        #"标题": video_data.get('title', ''),
        'pubtime': timedate,
        #"发布时间": timedate ,
        "updatetime": timedate2 ,
        'duration': video_data.get('duration', ''),
        #"视频长度（秒）": video_data.get('duration', ''),
        'play': stat_data.get('play', 0),
        #"播放量": stat_data.get('play', 0),
        #'vt': stat_data.get('vt', 0),
        #"未知": stat_data.get('vt', 0),
        'like': stat_data.get('like', 0),
        #"点赞": stat_data.get('like', 0),
        'comment': stat_data.get('comment', 0),
        #"评论数": stat_data.get('comment', 0),
        'dm': stat_data.get('dm', 0),
        #"弹幕数":stat_data.get('dm', 0),
        'fav': stat_data.get('fav', 0),
        #"收藏数": stat_data.get('fav', 0),
        'coin': stat_data.get('coin', 0),
        #"投币数": stat_data.get('coin', 0),
        'share': stat_data.get('share', 0),
        #"分享数": stat_data.get('share', 0),
        #'full_play_ratio': stat_data.get('full_play_ratio', 0)/10000,
        'full_play_ratio': check_and_divide(stat_data.get('full_play_ratio', 0)),
        # 完播比，用户平均在百分之多少退出
        #"完播比":stat_data.get('full_play_ratio', 0)/10000,
        'play_viewer_rate': stat_data.get('play_viewer_rate', 0),
        #"游客播放数": stat_data.get('play_viewer_rate', 0),
        'active_fans_rate': check_and_divide(stat_data.get('active_fans_rate', 0)),
        #"粉丝观看率":stat_data.get('active_fans_rate', 0)/10000,
        #'active_fans_med': stat_data.get('active_fans_med', 0),
        #"未知2"：stat_data.get('active_fans_med', 0),
        'tm_rate':check_and_divide(stat_data.get('tm_rate', 0)/10000),
        #"封标点击率":stat_data.get('tm_rate', 0)/10000,
        'tm_rate_med': check_and_divide(stat_data.get('tm_rate_med', 0)),
        #"你自己平均封标点击率": stat_data.get('tm_rate_med', 0)/10000,
        'tm_fan_simi_rate_med': check_and_divide(stat_data.get('tm_fan_simi_rate_med', 0)),
        #"同类up粉丝封标点击率" : stat_data.get('tm_fan_simi_rate_med', 0)/10000,
        'tm_viewer_simi_rate_med': check_and_divide(stat_data.get('tm_viewer_simi_rate_med', 0)),
        #"同类up游客封标点击率": stat_data.get('tm_viewer_simi_rate_med', 0)/10000,
        'tm_fan_rate': check_and_divide(stat_data.get('tm_fan_rate', 0)),
        #"粉丝封标点击率":stat_data.get('tm_fan_rate', 0)/10000,
        'tm_viewer_rate': check_and_divide(stat_data.get('tm_viewer_rate', 0)),
        #"游客封标点击率": stat_data.get('tm_viewer_rate', 0)/10000,
        'tm_pass_rate': check_and_divide(stat_data.get('tm_pass_rate', 0)),
        #"封标点击率超过n%同类稿件": stat_data.get('tm_pass_rate', 0)/10000,
        'tm_fan_pass_rate': check_and_divide(stat_data.get('tm_fan_pass_rate', 0)),
        #"粉丝封标点击率超过n%同类稿件": stat_data.get('tm_fan_pass_rate', 0)/10000,
        'tm_viewer_pass_rate': check_and_divide(stat_data.get('tm_viewer_pass_rate', 0)),
        #"游客封标点击率超过n%同类稿件":stat_data.get('tm_viewer_pass_rate', 0)/10000,
        'crash_rate': check_and_divide(stat_data.get('crash_rate', 0)),
        #"3秒退出率": stat_data.get('crash_rate', 0)/10000,
        #'crash_rate_med': stat_data.get('crash_rate_med', 0),
        #"未知3": stat_data.get('crash_rate_med', 0),
        'crash_fan_simi_rate_med': check_and_divide(stat_data.get('crash_fan_simi_rate_med', 0)),
        #"同类up粉丝3秒退出率": stat_data.get('crash_fan_simi_rate_med', 0)/10000,
        'crash_viewer_simi_rate_med': check_and_divide(stat_data.get('crash_viewer_simi_rate_med', 0)),
        #"同类up游客3秒退出率": stat_data.get('crash_viewer_simi_rate_med', 0)/10000,
        'crash_fan_rate': check_and_divide(stat_data.get('crash_fan_rate', 0)),
        #"粉丝3秒退出率": stat_data.get('crash_fan_rate', 0)/10000,
        'crash_viewer_rate': check_and_divide(stat_data.get('crash_viewer_rate', 0)),
        #"游客3秒退出率": stat_data.get('crash_viewer_rate', 0)/10000,
        'interact_rate': check_and_divide(stat_data.get('interact_rate', 0)),
        #"互动率": stat_data.get('interact_rate', 0)/10000,
        #'interact_rate_med': stat_data.get('interact_rate_med', 0),
        #"未知4": stat_data.get('interact_rate_med', 0),
        'interact_fan_simi_rate_med': check_and_divide(stat_data.get('interact_fan_simi_rate_med', 0)),
        #"同类up粉丝互动率": stat_data.get('interact_fan_simi_rate_med', 0)/10000,
        'interact_viewer_simi_rate_med': check_and_divide(stat_data.get('interact_viewer_simi_rate_med', 0)),
        #"同类up游客互动率": stat_data.get('interact_viewer_simi_rate_med', 0)/10000,
        'interact_fan_rate': check_and_divide(stat_data.get('interact_fan_rate', 0)),
        #"粉丝互动率":stat_data.get('interact_fan_rate', 0)/10000,
        'interact_viewer_rate': check_and_divide(stat_data.get('interact_viewer_rate', 0)),
        #"游客互动率": stat_data.get('interact_viewer_rate', 0)/10000,
        #'avg_play_time': stat_data.get('avg_play_time', 0),
        #平均播放时间|注意：此字段总是0，可能b站正在写代码，或者和播放量改播放时长有关？
        #"平均播放时间": stat_data.get('avg_play_time', 0),
        'total_new_attention_cnt': stat_data.get('total_new_attention_cnt', 0),
        #"涨粉": stat_data.get('total_new_attention_cnt', 0),
        'play_trans_fan_rate': check_and_divide(stat_data.get('play_trans_fan_rate', 0)),
        #"播转粉率": stat_data.get('play_trans_fan_rate', 0)/10000,
        'play_trans_fan_rate_med': check_and_divide( stat_data.get('play_trans_fan_rate_med', 0)),
        #"其他up平均播转粉率": stat_data.get('play_trans_fan_rate_med', 0)/10000,
    }
    
    return [{"fields": fields}]

from runtime import Args


def handler(args: Args[Input])->Output:
    cookie = args.input.cookie 
    params_input = args.input.params
    bvid = args.input.bvid
    
    # 处理params类型转换
    if isinstance(params_input, str):
        try:
            params = json.loads(params_input)
            args.logger.info(f"将字符串参数解析为字典: {params}")
        except json.JSONDecodeError:
            raise ValueError("params字符串格式不正确，无法解析为字典")
    elif params_input is None:
        params = {}
        args.logger.warning("未提供params参数，使用空字典")
    elif isinstance(params_input, dict):
        params = params_input
    else:
        raise TypeError(f"params类型错误，期望dict或str，实际为{type(params_input).__name__}")
    
    # 日志记录
    args.logger.info(f"开始生成WBI签名，参数: {params}")
    
    if not cookie:
        raise ValueError("Cookie不能为空，请确保已正确传入")
    
    # 生成签名
    wts, w_rid = generate_wbi_signature(params)

    SESSDATA = cookie


    try:
        fields = get_video_stats(SESSDATA, bvid, wts, w_rid)
        return {"fields": fields, "error": None}
    except Exception as e:
        return {"result": None, "error": str(e)}