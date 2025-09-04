#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试 baostock 在 Windows 上的兼容性问题
"""

import sys
import os
print(f"Python 版本: {sys.version}")
print(f"操作系统: {os.name}")
print(f"工作目录: {os.getcwd()}")

try:
    import baostock as bs
    print("[OK] baostock import success")
    
    # 测试登录
    print("\n1. Testing baostock login...")
    lg = bs.login()
    print(f"Login result: error_code={lg.error_code}, error_msg='{lg.error_msg}'")
    
    if lg.error_code == '0':
        print("[OK] baostock login success")
        
        # 测试基本查询
        print("\n2. Testing stock basic info query...")
        try:
            rs = bs.query_stock_basic(code="sz.002815")
            print(f"Query result: error_code={rs.error_code}, error_msg='{rs.error_msg}'")
            
            if rs.error_code == '0':
                print("[OK] Query success, reading data...")
                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())
                print(f"[OK] Got {len(data_list)} records")
                if data_list:
                    print(f"Fields: {rs.fields}")
                    print(f"First record: {data_list[0]}")
            else:
                print(f"[ERROR] Query failed: {rs.error_msg}")
                
        except Exception as e:
            print(f"[ERROR] Query exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        # 登出
        print("\n3. Testing baostock logout...")
        logout_result = bs.logout()
        print(f"Logout result: error_code={logout_result.error_code}, error_msg='{logout_result.error_msg}'")
    else:
        print(f"[ERROR] baostock login failed: {lg.error_msg}")
        
except ImportError as e:
    print(f"[ERROR] baostock import failed: {e}")
except Exception as e:
    print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Debug completed ===")