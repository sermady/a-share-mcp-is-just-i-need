#!/usr/bin/env python3
"""
独立的 HTTP 服务器，用于将 A-Share MCP 服务部署为 web 服务
在 localhost:8000 上运行
"""

import logging
import uvicorn
from datetime import datetime
from mcp.server.fastmcp import FastMCP

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

# --- 创建 ASGI 应用 ---
# 使用 FastMCP 的 SSE 传输方式
app = mcp_app.sse_app

if __name__ == "__main__":
    logger.info(f"Starting A-Share MCP HTTP Server on localhost:8000... Today is {current_date}")
    
    # 使用 uvicorn 运行服务器
    uvicorn.run(
        app, 
        host="localhost", 
        port=8000,
        log_level="info"
    )