import os


def export_to_excel(df, output_path: str, project_name: str, filename: str = None) -> str:
    """
    Export the DataFrame as an Excel file.
    
    Args:
        df: DataFrame to export
        output_path: Output directory path
        project_name: Project name (unused, kept for compatibility)
        filename: Filename to use (e.g., UUID-based). If None, uses project_name.xlsx
    
    Returns:
        Full path to the exported Excel file
    """
    import pandas as pd

    os.makedirs(output_path, exist_ok=True)
    if filename is None:
        filename = f"{project_name}.xlsx"
    elif not filename.endswith('.xlsx'):
        filename = f"{filename}.xlsx"
    
    excel_path = os.path.join(output_path, filename)
    df.to_excel(excel_path, index=False)
    return excel_path
