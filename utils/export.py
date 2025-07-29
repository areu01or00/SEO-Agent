import pandas as pd
import io
from typing import Union, List, Dict

def export_to_csv(data: Union[pd.DataFrame, List[Dict]]) -> str:
    """
    Export data to CSV format
    
    Args:
        data: DataFrame or list of dictionaries to export
        
    Returns:
        CSV string data
    """
    try:
        # Convert to DataFrame if needed
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data
        
        # Clean column names
        df.columns = [col.replace('_', ' ').title() for col in df.columns]
        
        # Format specific columns
        if 'Search Volume' in df.columns:
            df['Search Volume'] = df['Search Volume'].apply(lambda x: f"{x:,}" if pd.notnull(x) else "0")
        
        if 'Cpc' in df.columns:
            df['Cpc'] = df['Cpc'].apply(lambda x: f"${x:.2f}" if pd.notnull(x) else "$0.00")
        
        if 'Difficulty' in df.columns:
            df['Difficulty'] = df['Difficulty'].apply(lambda x: f"{x}%" if pd.notnull(x) else "0%")
        
        # Convert to CSV
        return df.to_csv(index=False)
        
    except Exception as e:
        raise Exception(f"CSV export failed: {str(e)}")

def export_to_excel(data: Union[pd.DataFrame, List[Dict]]) -> bytes:
    """
    Export data to Excel format
    
    Args:
        data: DataFrame or list of dictionaries to export
        
    Returns:
        Excel file as bytes
    """
    try:
        # Convert to DataFrame if needed
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Clean column names
        df.columns = [col.replace('_', ' ').title() for col in df.columns]
        
        # Create Excel buffer
        buffer = io.BytesIO()
        
        # Create Excel writer with formatting
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Write main data
            df.to_excel(writer, sheet_name='Keywords', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Keywords']
            
            # Format headers
            header_font = workbook.create_named_style('header')
            header_font.font.bold = True
            header_font.font.color = 'FFFFFF'
            header_font.fill.start_color = '366092'
            header_font.fill.end_color = '366092'
            header_font.fill.fill_type = 'solid'
            
            # Apply header formatting
            for cell in worksheet[1]:
                cell.style = header_font
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Format specific columns
            if 'Search Volume' in df.columns:
                vol_col = df.columns.get_loc('Search Volume') + 1
                for row in range(2, len(df) + 2):
                    cell = worksheet.cell(row=row, column=vol_col)
                    if cell.value and str(cell.value).replace(',', '').isdigit():
                        cell.number_format = '#,##0'
            
            if 'Cpc' in df.columns:
                cpc_col = df.columns.get_loc('Cpc') + 1
                for row in range(2, len(df) + 2):
                    cell = worksheet.cell(row=row, column=cpc_col)
                    cell.number_format = '$#,##0.00'
            
            if 'Difficulty' in df.columns:
                diff_col = df.columns.get_loc('Difficulty') + 1
                for row in range(2, len(df) + 2):
                    cell = worksheet.cell(row=row, column=diff_col)
                    if isinstance(cell.value, (int, float)):
                        cell.number_format = '0"%"'
        
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        # Fallback to simple Excel export
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data
        
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        return buffer.getvalue()

def export_to_json(data: Union[pd.DataFrame, List[Dict]]) -> str:
    """
    Export data to JSON format
    
    Args:
        data: DataFrame or list of dictionaries to export
        
    Returns:
        JSON string data
    """
    try:
        if isinstance(data, pd.DataFrame):
            return data.to_json(orient='records', indent=2)
        else:
            import json
            return json.dumps(data, indent=2)
            
    except Exception as e:
        raise Exception(f"JSON export failed: {str(e)}")

def create_keyword_report(
    keywords: List[Dict],
    seed_keyword: str,
    filters: Dict = None
) -> Dict[str, any]:
    """
    Create a comprehensive keyword report
    
    Args:
        keywords: List of keyword data
        seed_keyword: Original seed keyword
        filters: Applied filters
        
    Returns:
        Report dictionary with summary and data
    """
    try:
        df = pd.DataFrame(keywords)
        
        if df.empty:
            return {
                "summary": {
                    "seed_keyword": seed_keyword,
                    "total_keywords": 0,
                    "avg_search_volume": 0,
                    "avg_difficulty": 0,
                    "avg_cpc": 0
                },
                "data": [],
                "filters": filters or {}
            }
        
        # Calculate summary statistics
        summary = {
            "seed_keyword": seed_keyword,
            "total_keywords": len(df),
            "avg_search_volume": int(df['search_volume'].mean()) if 'search_volume' in df.columns else 0,
            "avg_difficulty": round(df['difficulty'].mean(), 1) if 'difficulty' in df.columns else 0,
            "avg_cpc": round(df['cpc'].mean(), 2) if 'cpc' in df.columns else 0,
            "max_search_volume": int(df['search_volume'].max()) if 'search_volume' in df.columns else 0,
            "min_difficulty": int(df['difficulty'].min()) if 'difficulty' in df.columns else 0
        }
        
        # Keyword type distribution
        if 'type' in df.columns:
            type_counts = df['type'].value_counts().to_dict()
            summary["keyword_types"] = type_counts
        
        return {
            "summary": summary,
            "data": keywords,
            "filters": filters or {},
            "generated_at": pd.Timestamp.now().isoformat()
        }
        
    except Exception as e:
        return {
            "summary": {"error": f"Report generation failed: {str(e)}"},
            "data": keywords,
            "filters": filters or {}
        }

def format_keyword_data_for_export(keywords: List[Dict]) -> pd.DataFrame:
    """
    Format keyword data for export with proper column names and types
    
    Args:
        keywords: Raw keyword data
        
    Returns:
        Formatted DataFrame
    """
    try:
        df = pd.DataFrame(keywords)
        
        if df.empty:
            return df
        
        # Rename columns for better readability
        column_mapping = {
            'keyword': 'Keyword',
            'search_volume': 'Search Volume',
            'difficulty': 'Difficulty (%)',
            'cpc': 'CPC ($)',
            'competition': 'Competition',
            'type': 'Keyword Type',
            'ai_insight': 'AI Insight'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Format numeric columns
        if 'Search Volume' in df.columns:
            df['Search Volume'] = pd.to_numeric(df['Search Volume'], errors='coerce').fillna(0).astype(int)
        
        if 'Difficulty (%)' in df.columns:
            df['Difficulty (%)'] = pd.to_numeric(df['Difficulty (%)'], errors='coerce').fillna(0).round(0).astype(int)
        
        if 'CPC ($)' in df.columns:
            df['CPC ($)'] = pd.to_numeric(df['CPC ($)'], errors='coerce').fillna(0).round(2)
        
        if 'Competition' in df.columns:
            df['Competition'] = pd.to_numeric(df['Competition'], errors='coerce').fillna(0).round(3)
        
        # Reorder columns for better presentation
        column_order = ['Keyword', 'Search Volume', 'Difficulty (%)', 'CPC ($)', 'Keyword Type', 'Competition']
        if 'AI Insight' in df.columns:
            column_order.append('AI Insight')
        
        # Only include columns that exist
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        return df
        
    except Exception as e:
        # Return original data if formatting fails
        return pd.DataFrame(keywords)