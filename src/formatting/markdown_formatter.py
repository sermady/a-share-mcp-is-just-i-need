"""
Markdown formatting utilities for A-Share MCP Server.
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Configuration
MAX_MARKDOWN_ROWS = 50  # Max rows to display in Markdown output
MAX_MARKDOWN_COLS = 10  # Max columns to display


def format_df_to_markdown(df: pd.DataFrame, max_rows: int = MAX_MARKDOWN_ROWS, max_cols: int = MAX_MARKDOWN_COLS) -> str:
    """Formats a Pandas DataFrame to a Markdown string with truncation.

    Args:
        df: The DataFrame to format
        max_rows: Maximum rows to include in output
        max_cols: Maximum columns to include in output

    Returns:
        A markdown formatted string representation of the DataFrame
    """
    if df.empty:
        logger.warning("Attempted to format an empty DataFrame to Markdown.")
        return "(No data available to display)"

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
