"""
Markdown formatting utilities for A-Share MCP Server.
"""
import pandas as pd
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Configuration
# Common number of trading days per year. Max rows to display in Markdown output
MAX_MARKDOWN_ROWS = 250
MAX_MARKDOWN_COLS = 20  # Max columns to display


def format_df_to_markdown(df: pd.DataFrame, max_rows: int = None, max_cols: int = MAX_MARKDOWN_COLS,
                          start_date: str = None, end_date: str = None) -> str:
    """Formats a Pandas DataFrame to a Markdown string with truncation.

    Args:
        df: The DataFrame to format
        max_rows: Maximum rows to include in output. If None, will be dynamically calculated based on date range
        max_cols: Maximum columns to include in output
        start_date: Optional start date string (format: YYYY-MM-DD) for dynamic row calculation
        end_date: Optional end date string (format: YYYY-MM-DD) for dynamic row calculation

    Returns:
        A markdown formatted string representation of the DataFrame
    """
    if df.empty:
        logger.warning("Attempted to format an empty DataFrame to Markdown.")
        return "(No data available to display)"

    # Calculate dynamic max_rows based on date range if provided
    if max_rows is None:
        max_rows = _calculate_dynamic_max_rows(df, start_date, end_date)
        logger.debug(f"Dynamically calculated max_rows: {max_rows}")

    original_rows, original_cols = df.shape
    truncated = False
    truncation_notes = []

    if original_rows > max_rows:
        df_display = pd.concat(
            [df.head(max_rows // 2), df.tail(max_rows - max_rows // 2)])
        truncation_notes.append(
            f"rows truncated to {max_rows} (from {original_rows})")
        truncated = True
    else:
        df_display = df

    if original_cols > max_cols:
        # Select first and last columns for display
        cols_to_show = df_display.columns[:max_cols // 2].tolist() + \
            df_display.columns[-(max_cols - max_cols // 2):].tolist()
        # Ensure no duplicate columns if original_cols is small but > max_cols
        cols_to_show = sorted(list(set(cols_to_show)),
                              key=list(df_display.columns).index)
        df_display = df_display[cols_to_show]
        truncation_notes.append(
            f"columns truncated to {len(cols_to_show)} (from {original_cols})")
        truncated = True

    try:
        markdown_table = df_display.to_markdown(index=False)
    except Exception as e:
        logger.error(
            f"Error converting DataFrame to Markdown: {e}", exc_info=True)
        return "Error: Could not format data into Markdown table."

    if truncated:
        notes = "; ".join(truncation_notes)
        logger.debug(
            f"Markdown table generated with truncation notes: {notes}")
        return f"Note: Data truncated ({notes}).\n\n{markdown_table}"
    else:
        logger.debug("Markdown table generated without truncation.")
        return markdown_table


def _calculate_dynamic_max_rows(df: pd.DataFrame, start_date: str = None, end_date: str = None) -> int:
    """Calculate a dynamic max_rows value based on the date range or DataFrame content.

    Args:
        df: The DataFrame to analyze
        start_date: Start date string in YYYY-MM-DD format
        end_date: End date string in YYYY-MM-DD format

    Returns:
        Appropriate max_rows value
    """
    # 首先检查 DataFrame 的实际行数
    actual_rows = len(df)

    # 计算基于日期的估计行数
    estimated_rows = MAX_MARKDOWN_ROWS  # 默认值

    # 如果 DataFrame 有 'date' 列，尝试使用它计算
    if 'date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['date']) or isinstance(df['date'].iloc[0], str):
        try:
            if isinstance(df['date'].iloc[0], str):
                date_series = pd.to_datetime(df['date'])
            else:
                date_series = df['date']

            min_date = date_series.min()
            max_date = date_series.max()
            date_range = (max_date - min_date).days

            # 估计交易日（大约每年 250 个交易日）
            estimated_rows = int(date_range * 250 / 365) + 1

        except Exception as e:
            logger.warning(
                f"Error calculating dynamic rows from DataFrame date column: {e}")

    # 如果提供了 start_date 和 end_date
    elif start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            date_range = (end - start).days

            # 估计交易日（大约每年 250 个交易日）
            estimated_rows = int(date_range * 250 / 365) + 1

        except Exception as e:
            logger.warning(
                f"Error calculating dynamic rows from start/end dates: {e}")

    # 确保估计行数不超过最大行数
    estimated_rows = min(estimated_rows, MAX_MARKDOWN_ROWS)

    # 如果实际行数小于估计行数，直接返回实际行数；否则返回估计行数
    return min(actual_rows, estimated_rows)
