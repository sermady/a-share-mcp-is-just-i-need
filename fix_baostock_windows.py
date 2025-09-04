#!/usr/bin/env python3
"""
修复 baostock 在 Windows 上的兼容性问题
"""

import sys
import os
import logging

# 尝试修复 Windows 兼容性问题
def fix_baostock_windows():
    """
    修复 baostock 在 Windows 上的 [WinError 1] 问题
    """
    print("正在应用 baostock Windows 兼容性修复...")
    
    # 方法1: 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # 方法2: 增加 DLL 搜索路径（如果需要）
    if hasattr(os, 'add_dll_directory') and sys.platform.startswith('win'):
        try:
            # 添加可能的 baostock DLL 路径
            python_path = os.path.dirname(sys.executable)
            possible_paths = [
                python_path,
                os.path.join(python_path, 'Library', 'bin'),
                os.path.join(python_path, 'Scripts'),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    os.add_dll_directory(path)
                    print(f"添加 DLL 路径: {path}")
        except Exception as e:
            print(f"DLL 路径设置警告: {e}")
    
    # 方法3: 修改 Python 路径
    try:
        import site
        site_packages = site.getsitepackages()
        for pkg_path in site_packages:
            if pkg_path not in sys.path:
                sys.path.insert(0, pkg_path)
        print(f"更新了 {len(site_packages)} 个包路径")
    except Exception as e:
        print(f"路径更新警告: {e}")
    
    print("Windows 兼容性修复完成")

def test_baostock_after_fix():
    """测试修复后的 baostock"""
    print("\n测试修复后的 baostock...")
    
    try:
        import baostock as bs
        print("✓ baostock 导入成功")
        
        # 测试基本功能
        lg = bs.login()
        if lg.error_code == '0':
            print("✓ 登录成功")
            
            # 测试查询
            rs = bs.query_stock_basic(code="sz.002815")
            if rs.error_code == '0':
                print("✓ 查询成功")
                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())
                print(f"✓ 获取到 {len(data_list)} 条记录")
                
                # 登出
                bs.logout()
                print("✓ 登出成功")
                
                print("\n修复成功！baostock 现在可以正常工作了。")
                return True
            else:
                print(f"✗ 查询失败: {rs.error_msg}")
        else:
            print(f"✗ 登录失败: {lg.error_msg}")
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
    return False

if __name__ == "__main__":
    # 应用修复
    fix_baostock_windows()
    
    # 测试修复效果
    if test_baostock_after_fix():
        print("\n🎉 修复成功！现在可以重新启动 MCP 服务器了。")
    else:
        print("\n❌ 修复失败，需要进一步调试。")