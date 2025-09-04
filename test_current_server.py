#!/usr/bin/env python3
"""
测试当前运行的 MCP 服务器
"""
import json
import requests

def test_current_server():
    base_url = "http://localhost:8000"
    
    print("=== Testing Current MCP Server ===")
    print(f"Server URL: {base_url}")
    
    # 测试1: 初始化
    print("\n1. Testing MCP initialization...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    
    try:
        response = requests.post(f"{base_url}/message", json=init_request, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Result: {result}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # 测试2: 工具列表
    print("\n2. Testing tools/list...")
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        response = requests.post(f"{base_url}/message", json=tools_request, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            tools = result.get('result', {}).get('tools', [])
            print(f"Found {len(tools)} tools")
            for tool in tools[:3]:  # 只显示前3个
                print(f"  - {tool.get('name')}: {tool.get('description', '')[:60]}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # 测试3: 调用具体工具
    print("\n3. Testing get_stock_basic_info...")
    call_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_stock_basic_info",
            "arguments": {"code": "sz.002815"}
        }
    }
    
    try:
        response = requests.post(f"{base_url}/message", json=call_request, timeout=15)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if 'result' in result:
                content = result['result'].get('content', [])
                if content:
                    print(f"Success: Got {len(content)} content items")
                    print(f"First content: {content[0].get('text', '')[:200]}...")
                else:
                    print("Success but no content")
            elif 'error' in result:
                print(f"Tool error: {result['error']}")
        else:
            print(f"HTTP Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print("\n=== Test Completed ===")

if __name__ == "__main__":
    test_current_server()