#!/usr/bin/env python3
"""
增强的 HTTP 服务器，手动添加 MCP 协议支持的 /messages 端点
"""

import logging
import uvicorn
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.requests import Request
import json

# Import the interface and the concrete implementation
from src.data_source_interface import FinancialDataSource
from src.baostock_data_source import BaostockDataSource
from src.utils import setup_logging

# 导入各模块工具的注册函数
from src.tools.stock_market import register_stock_market_tools
from src.tools.financial_reports import register_financial_report_tools
from src.tools.indices import register_index_tools
from src.tools.market_overview import register_market_overview_tools
from src.tools.macroeconomic import register_macroeconomic_tools
from src.tools.date_utils import register_date_utils_tools
from src.tools.analysis import register_analysis_tools

# --- Logging Setup ---
setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Dependency Injection ---
active_data_source: FinancialDataSource = BaostockDataSource()

# --- Get current date for system prompt ---
current_date = datetime.now().strftime("%Y-%m-%d")

# --- FastMCP App Initialization ---
mcp_app = FastMCP(
    server_name="a_share_data_provider",
    description=f"""今天是{current_date}。提供中国A股市场数据分析工具。此服务提供客观数据分析，用户需自行做出投资决策。数据分析基于公开市场信息，不构成投资建议，仅供参考。

⚠️ 重要说明:
1. 最新交易日不一定是今天，需要从 get_latest_trading_date() 获取
2. 请始终使用 get_latest_trading_date() 工具获取实际当前最近的交易日，不要依赖训练数据中的日期认知
3. 当分析"最近"或"近期"市场情况时，必须首先调用 get_market_analysis_timeframe() 工具确定实际的分析时间范围
4. 任何涉及日期的分析必须基于工具返回的实际数据，不得使用过时或假设的日期
""",
)

# --- 注册各模块的工具 ---
register_stock_market_tools(mcp_app, active_data_source)
register_financial_report_tools(mcp_app, active_data_source)
register_index_tools(mcp_app, active_data_source)
register_market_overview_tools(mcp_app, active_data_source)
register_macroeconomic_tools(mcp_app, active_data_source)
register_date_utils_tools(mcp_app, active_data_source)
register_analysis_tools(mcp_app, active_data_source)

# 会话存储
sessions = {}

async def mcp_endpoint(request: Request):
    """处理 MCP 协议请求的统一端点"""
    try:
        data = await request.json()
        method = data.get('method')
        request_id = data.get('id')
        
        logger.info(f"MCP request: {method} (ID: {request_id})")
        
        if method == "initialize":
            # 初始化响应
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "a_share_data_provider",
                        "version": "1.0.0"
                    }
                }
            }
            return JSONResponse(response)
            
        elif method == "notifications/initialized":
            # 初始化完成通知
            return JSONResponse({"status": "ok"})
            
        elif method == "tools/list":
            # 获取工具列表
            try:
                # list_tools() 返回协程，需要await
                tools_result = await mcp_app.list_tools()
                tools_list = []
                
                for tool in tools_result:
                    # tool 是 Tool 对象，需要提取其属性
                    tool_info = {
                        "name": tool.name if hasattr(tool, 'name') else str(tool),
                        "description": tool.description if hasattr(tool, 'description') else f"Tool: {tool.name if hasattr(tool, 'name') else str(tool)}",
                    }
                    # 添加输入模式如果存在
                    if hasattr(tool, 'inputSchema'):
                        tool_info["inputSchema"] = tool.inputSchema
                    
                    tools_list.append(tool_info)
                
                response = {
                    "jsonrpc": "2.0", 
                    "id": request_id,
                    "result": {
                        "tools": tools_list
                    }
                }
                return JSONResponse(response)
                
            except Exception as e:
                logger.error(f"Error getting tools list: {e}")
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Failed to get tools list: {str(e)}"
                    }
                }
                return JSONResponse(response)
            
        elif method == "tools/call":
            # 调用工具
            params = data.get('params', {})
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            try:
                result = await mcp_app.call_tool(tool_name, arguments)
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": str(result)}]
                    }
                }
            except Exception as e:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Tool execution failed: {str(e)}"
                    }
                }
                
            return JSONResponse(response)
            
        else:
            # 未知方法
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            return JSONResponse(response)
            
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}")
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            },
            status_code=400
        )

# 创建路由 - 简化版本，只保留核心端点
routes = [
    Route("/mcp", mcp_endpoint, methods=["POST"]),        # MCP 标准端点
    Route("/message", mcp_endpoint, methods=["POST"]),    # 你的系统使用的端点
    Route("/messages", mcp_endpoint, methods=["POST"]),   # 备用端点（复数形式）
    # 移除不常用的端点: /api/mcp, /call
]

# 创建 Starlette 应用
app = Starlette(routes=routes)

if __name__ == "__main__":
    logger.info(f"Starting Enhanced A-Share MCP HTTP Server on localhost:8000... Today is {current_date}")
    logger.info("Supported endpoints: /mcp, /message, /messages (simplified)")
    
    # 使用 uvicorn 运行服务器
    uvicorn.run(
        app, 
        host="localhost", 
        port=8000,
        log_level="info"
    )