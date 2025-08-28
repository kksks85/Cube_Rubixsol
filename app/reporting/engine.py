"""
Reporting Engine
Core functionality for data processing and report generation
"""

from app import db
from app.models import User, WorkOrder, Product, Company, InventoryItem, UAVServiceIncident
from app.knowledge.models import KnowledgeArticle
import pandas as pd
import json
import time
import io
from sqlalchemy import text, inspect
from datetime import datetime
import csv
import xlsxwriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


class ReportEngine:
    """Core engine for report execution and data processing"""
    
    def __init__(self):
        self.inspector = inspect(db.engine)
    
    def get_available_tables(self):
        """Get all available tables with their metadata"""
        
        tables = {
            'work_orders': {
                'display_name': 'Work Orders',
                'description': 'All work order records',
                'model': WorkOrder
            },
            'products': {
                'display_name': 'Products',
                'description': 'Product catalog',
                'model': Product
            },
            'companies': {
                'display_name': 'Companies',
                'description': 'Company directory',
                'model': Company
            },
            'users': {
                'display_name': 'Users',
                'description': 'System users',
                'model': User
            },
            'inventory_items': {
                'display_name': 'Inventory Items',
                'description': 'Inventory management',
                'model': InventoryItem
            },
            'uav_service_incidents': {
                'display_name': 'UAV Service Incidents',
                'description': 'UAV service records',
                'model': UAVServiceIncident
            },
            'knowledge_articles': {
                'display_name': 'Knowledge Articles',
                'description': 'Knowledge base articles',
                'model': KnowledgeArticle
            }
        }
        
        return tables
    
    def get_table_columns(self, table_name):
        """Get columns for a specific table"""
        
        try:
            # Get table metadata from inspector
            columns = self.inspector.get_columns(table_name)
            
            result = []
            for col in columns:
                result.append({
                    'name': col['name'],
                    'display_name': col['name'].replace('_', ' ').title(),
                    'type': str(col['type']),
                    'nullable': col.get('nullable', True)
                })
            
            return result
            
        except Exception as e:
            # Fallback: try to get columns from the model
            tables = self.get_available_tables()
            if table_name in tables:
                model = tables[table_name]['model']
                columns = []
                for column in model.__table__.columns:
                    columns.append({
                        'name': column.name,
                        'display_name': column.name.replace('_', ' ').title(),
                        'type': str(column.type),
                        'nullable': column.nullable
                    })
                return columns
            
            raise Exception(f"Unable to get columns for table: {table_name}")
    
    def get_table_info(self, table_name):
        """Get detailed information about a table"""
        
        try:
            columns = self.get_table_columns(table_name)
            
            # Get row count
            result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = result.scalar()
            
            return {
                'table_name': table_name,
                'columns': columns,
                'column_count': len(columns),
                'row_count': row_count
            }
            
        except Exception as e:
            raise Exception(f"Unable to get table info: {str(e)}")
    
    def execute_report(self, report):
        """Execute a report and return results"""
        
        start_time = time.time()
        
        try:
            # Build the query
            query = self.build_query(report)
            
            # Execute query
            result = db.session.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert datetime objects to strings
                    if isinstance(value, datetime):
                        value = value.strftime('%Y-%m-%d %H:%M:%S')
                    row_dict[col] = value
                data.append(row_dict)
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'data': data,
                'columns': columns,
                'row_count': len(data),
                'execution_time': execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'error': str(e),
                'execution_time': execution_time
            }
    
    def build_query(self, report):
        """Build SQL query from report configuration"""
        
        if not report.data_source:
            raise Exception("No data source specified")
        
        table_name = report.data_source
        
        # Build SELECT clause
        if report.columns:
            try:
                columns = json.loads(report.columns)
                if columns and columns != ['*']:
                    select_clause = ', '.join(columns)
                else:
                    select_clause = '*'
            except:
                select_clause = '*'
        else:
            select_clause = '*'
        
        # Build WHERE clause
        where_clauses = []
        if report.filters:
            try:
                filters = json.loads(report.filters)
                for filter_config in filters:
                    if filter_config.get('field') and filter_config.get('operator'):
                        where_clause = self.build_filter_clause(filter_config)
                        if where_clause:
                            where_clauses.append(where_clause)
            except:
                pass  # Skip invalid filters
        
        # Construct final query
        query = f"SELECT {select_clause} FROM {table_name}"
        
        if where_clauses:
            query += f" WHERE {' AND '.join(where_clauses)}"
        
        # Add basic limit for safety
        query += " LIMIT 1000"
        
        return query
    
    def build_filter_clause(self, filter_config):
        """Build a WHERE clause from filter configuration"""
        
        field = filter_config['field']
        operator = filter_config['operator']
        value = filter_config.get('value', '')
        
        if operator == 'equals':
            return f"{field} = '{value}'"
        elif operator == 'not_equals':
            return f"{field} != '{value}'"
        elif operator == 'contains':
            return f"{field} LIKE '%{value}%'"
        elif operator == 'starts_with':
            return f"{field} LIKE '{value}%'"
        elif operator == 'ends_with':
            return f"{field} LIKE '%{value}'"
        elif operator == 'greater_than':
            return f"{field} > '{value}'"
        elif operator == 'less_than':
            return f"{field} < '{value}'"
        elif operator == 'is_null':
            return f"{field} IS NULL"
        elif operator == 'is_not_null':
            return f"{field} IS NOT NULL"
        
        return None
    
    def export_to_csv(self, report):
        """Export report data to CSV format"""
        
        result = self.execute_report(report)
        if not result['success']:
            raise Exception(result['error'])
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=result['columns'])
        writer.writeheader()
        writer.writerows(result['data'])
        
        return output.getvalue()
    
    def export_to_excel(self, report):
        """Export report data to Excel format"""
        
        result = self.execute_report(report)
        if not result['success']:
            raise Exception(result['error'])
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet(report.name[:31])  # Excel sheet name limit
        
        # Write headers
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC'})
        for col, header in enumerate(result['columns']):
            worksheet.write(0, col, header, header_format)
        
        # Write data
        for row_idx, row_data in enumerate(result['data'], 1):
            for col_idx, column in enumerate(result['columns']):
                worksheet.write(row_idx, col_idx, row_data.get(column, ''))
        
        workbook.close()
        output.seek(0)
        
        return output.getvalue()
    
    def export_to_pdf(self, report):
        """Export report data to PDF format"""
        
        result = self.execute_report(report)
        if not result['success']:
            raise Exception(result['error'])
        
        output = io.BytesIO()
        p = canvas.Canvas(output, pagesize=letter)
        width, height = letter
        
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, report.name)
        
        # Report info
        p.setFont("Helvetica", 10)
        y_position = height - 80
        p.drawString(50, y_position, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        y_position -= 15
        p.drawString(50, y_position, f"Records: {result['row_count']}")
        
        # Data (simplified for PDF)
        y_position -= 40
        p.setFont("Helvetica-Bold", 10)
        
        # Headers
        x_positions = [50 + i * 100 for i in range(min(6, len(result['columns'])))]  # Limit columns for PDF
        for i, header in enumerate(result['columns'][:6]):
            p.drawString(x_positions[i], y_position, header[:15])  # Truncate long headers
        
        y_position -= 20
        
        # Data rows (limit for PDF)
        p.setFont("Helvetica", 9)
        for row_data in result['data'][:20]:  # Limit rows for PDF
            for i, column in enumerate(result['columns'][:6]):
                value = str(row_data.get(column, ''))[:15]  # Truncate long values
                p.drawString(x_positions[i], y_position, value)
            y_position -= 15
            
            if y_position < 50:  # New page if needed
                p.showPage()
                y_position = height - 50
        
        if result['row_count'] > 20:
            y_position -= 20
            p.drawString(50, y_position, f"... and {result['row_count'] - 20} more records")
        
        p.save()
        output.seek(0)
        
        return output.getvalue()


class ReportValidator:
    """Validator for report configurations"""
    
    @staticmethod
    def validate_report_config(config):
        """Validate report configuration"""
        
        errors = []
        
        # Check required fields
        if not config.get('data_source'):
            errors.append("Data source is required")
        
        # Validate columns
        if config.get('columns'):
            try:
                columns = json.loads(config['columns']) if isinstance(config['columns'], str) else config['columns']
                if not isinstance(columns, list):
                    errors.append("Columns must be a list")
            except:
                errors.append("Invalid columns format")
        
        # Validate filters
        if config.get('filters'):
            try:
                filters = json.loads(config['filters']) if isinstance(config['filters'], str) else config['filters']
                if not isinstance(filters, list):
                    errors.append("Filters must be a list")
                else:
                    for i, filter_config in enumerate(filters):
                        if not isinstance(filter_config, dict):
                            errors.append(f"Filter {i+1} must be an object")
                        elif not filter_config.get('field'):
                            errors.append(f"Filter {i+1} missing field")
                        elif not filter_config.get('operator'):
                            errors.append(f"Filter {i+1} missing operator")
            except:
                errors.append("Invalid filters format")
        
        return errors