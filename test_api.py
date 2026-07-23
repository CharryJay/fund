#!/usr/bin/env python3
"""
测试股票数据接口是否能正确获取数据
用于验证 index.html 中使用的 Yahoo Finance API 是否可用
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta

# CORS 代理服务（与 index.html 中相同）
CORS_PROXY = 'https://api.allorigins.win/raw?url='

# Yahoo Finance API 基础 URL
YAHOO_FINANCE_BASE = 'https://query1.finance.yahoo.com/v8/finance/chart/'

def convert_to_yahoo_symbol(stock_code):
    """将港股代码转换为 Yahoo Finance 格式"""
    stock_code = stock_code.upper()
    if stock_code.startswith('HK'):
        number_part = stock_code[2:]
        return f"{number_part}.HK"
    if '.HK' in stock_code or '.SS' in stock_code or '.SZ' in stock_code:
        return stock_code
    return f"{stock_code}.HK"

def fetch_stock_data_from_yahoo(symbol, start_date, end_date):
    """从 Yahoo Finance 获取股票数据"""
    yahoo_symbol = convert_to_yahoo_symbol(symbol)
    
    # 转换日期为时间戳
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
    
    # 构建 URL
    url = (f"{YAHOO_FINANCE_BASE}{yahoo_symbol}?period1={start_timestamp}"
           f"&period2={end_timestamp}&interval=1d&includePreClose=false"
           f"&range=1d&useYield=false")
    
    print(f"\n正在获取 {symbol} ({yahoo_symbol}) 的数据...")
    print(f"API URL: {url}")
    
    try:
        # 使用 CORS 代理
        full_url = CORS_PROXY + urllib.parse.quote(url)
        print(f"通过代理访问：{full_url[:100]}...")
        
        req = urllib.request.Request(
            full_url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if not data.get('chart') or not data['chart'].get('result') or len(data['chart']['result']) == 0:
                print(f"⚠️ 未找到 {symbol} 的数据")
                return None
            
            result = data['chart']['result'][0]
            timestamps = result.get('timestamp', [])
            quotes = result.get('indicators', {}).get('quote', [{}])[0]
            closes = quotes.get('close', [])
            
            stock_data = []
            for i in range(len(timestamps)):
                if closes[i] is not None:
                    date_str = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
                    stock_data.append({
                        'date': date_str,
                        'price': closes[i],
                        'code': symbol
                    })
            
            print(f"✓ 成功获取 {len(stock_data)} 条数据")
            if stock_data:
                print(f"  首条数据：{stock_data[0]['date']} - 价格：{stock_data[0]['price']:.2f}")
                print(f"  末条数据：{stock_data[-1]['date']} - 价格：{stock_data[-1]['price']:.2f}")
            
            return stock_data
            
    except Exception as e:
        print(f"✗ 获取数据失败：{e}")
        return None

def test_api():
    """测试 API 是否可用"""
    print("=" * 60)
    print("股票数据接口测试工具")
    print("=" * 60)
    
    # 设置测试日期范围（最近 30 天）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    print(f"\n测试日期范围：{start_date_str} 至 {end_date_str}")
    
    # 测试几个港股代码
    test_symbols = ['HK3033', 'HK0700', 'HK9988', 'HK07552']
    
    results = {}
    success_count = 0
    
    for symbol in test_symbols:
        data = fetch_stock_data_from_yahoo(symbol, start_date_str, end_date_str)
        if data and len(data) > 0:
            results[symbol] = {'status': 'success', 'data_points': len(data)}
            success_count += 1
        else:
            results[symbol] = {'status': 'failed', 'data_points': 0}
    
    # 打印测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    print(f"测试股票数：{len(test_symbols)}")
    print(f"成功获取：{success_count}")
    print(f"失败：{len(test_symbols) - success_count}")
    print(f"成功率：{success_count / len(test_symbols) * 100:.1f}%")
    print()
    
    for symbol, result in results.items():
        status_icon = "✓" if result['status'] == 'success' else "✗"
        print(f"{status_icon} {symbol}: {result['status']} ({result['data_points']} 条数据)")
    
    print()
    if success_count > 0:
        print("✅ 数据接口工作正常，可以获取真实股票数据")
        print("💡 提示：index.html 会通过 CORS 代理访问 Yahoo Finance API")
        print("   如果某些股票获取失败，系统会自动降级使用模拟数据")
    else:
        print("⚠️ 所有股票数据获取失败，系统将使用模拟数据")
        print("💡 这可能是因为网络问题或 API 限制")
    
    print("=" * 60)
    return success_count > 0

if __name__ == '__main__':
    test_api()
