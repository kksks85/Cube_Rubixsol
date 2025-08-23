"""
Reporting Engine Core Classes
"""

import json
from datetime import datetime, timezone
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import io
import csv
from app import db
from app.models import *

class ReportEngine:
    """Core reporting engine for dynamic query building and execution"""
    
    def __init__(self):
        self.available_tables = self._get_available_tables()
        self.table_schemas = self._get_table_schemas()
    
    def _get_available_tables(self):
        """Get list of available database tables"""
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Filter out internal tables and add display names
        table_mapping = {
            'workorders': 'Work Orders',
            'users': 'Users',
            'companies': 'Companies',
            'products': 'Products',
            'priorities': 'Priorities',
            'statuses': 'Statuses',
            'categories': 'Categories',
            'workorder_activities': 'Work Order Activities',
            'product_categories': 'Product Categories',
            'product_specifications': 'Product Specifications',
            'saved_reports': 'Saved Reports',
            'report_schedules': 'Report Schedules',
            'report_execution_logs': 'Report Execution Logs'
        }
        
        return {table: table_mapping.get(table, table.replace('_', ' ').title()) 
                for table in tables if not table.startswith('alembic')}
    
    def _get_table_schemas(self):
        """Get schema information for all tables"""
        inspector = inspect(db.engine)
        schemas = {}
        
        for table_name in self.available_tables.keys():
            try:
                columns = inspector.get_columns(table_name)
                schemas[table_name] = {
                    'columns': {col['name']: {
                        'type': str(col['type']),
                        'nullable': col['nullable'],
                        'primary_key': col.get('primary_key', False)
                    } for col in columns},
                    'foreign_keys': inspector.get_foreign_keys(table_name)
                }
            except Exception as e:
                print(f"Error getting schema for {table_name}: {e}")
                schemas[table_name] = {'columns': {}, 'foreign_keys': []}
        
        return schemas
    
    def get_table_columns(self, table_name):
        """Get columns for a specific table"""
        if table_name in self.table_schemas:
            return list(self.table_schemas[table_name]['columns'].keys())
        return []
    
    def get_enhanced_table_columns(self, table_name):
        """Get columns for a table including suggested foreign key relationships"""
        base_columns = self.get_table_columns(table_name)
        enhanced_columns = []
        
        # Add base columns
        for col in base_columns:
            enhanced_columns.append({
                'name': col,
                'display_name': col.replace('_', ' ').title(),
                'type': self.get_column_type(table_name, col),
                'is_foreign_key': False
            })
        
        # Add suggested foreign key relationships
        if table_name in self.table_schemas:
            foreign_keys = self.table_schemas[table_name].get('foreign_keys', [])
            for fk in foreign_keys:
                fk_column = fk['constrained_columns'][0]
                referenced_table = fk['referred_table']
                
                # Suggest common display columns for referenced tables
                if referenced_table == 'statuses':
                    enhanced_columns.append({
                        'name': f"{referenced_table}.name",
                        'display_name': "Status Name",
                        'type': 'VARCHAR',
                        'is_foreign_key': True,
                        'join_info': {
                            'table': referenced_table,
                            'local_key': fk_column,
                            'foreign_key': 'id'
                        }
                    })
                elif referenced_table == 'priorities':
                    enhanced_columns.append({
                        'name': f"{referenced_table}.name",
                        'display_name': "Priority Name",
                        'type': 'VARCHAR',
                        'is_foreign_key': True,
                        'join_info': {
                            'table': referenced_table,
                            'local_key': fk_column,
                            'foreign_key': 'id'
                        }
                    })
                elif referenced_table == 'users':
                    enhanced_columns.extend([
                        {
                            'name': f"{referenced_table}.username",
                            'display_name': "User Name",
                            'type': 'VARCHAR',
                            'is_foreign_key': True,
                            'join_info': {
                                'table': referenced_table,
                                'local_key': fk_column,
                                'foreign_key': 'id'
                            }
                        },
                        {
                            'name': f"{referenced_table}.first_name",
                            'display_name': "First Name",
                            'type': 'VARCHAR',
                            'is_foreign_key': True,
                            'join_info': {
                                'table': referenced_table,
                                'local_key': fk_column,
                                'foreign_key': 'id'
                            }
                        },
                        {
                            'name': f"{referenced_table}.last_name",
                            'display_name': "Last Name",
                            'type': 'VARCHAR',
                            'is_foreign_key': True,
                            'join_info': {
                                'table': referenced_table,
                                'local_key': fk_column,
                                'foreign_key': 'id'
                            }
                        }
                    ])
        
        return enhanced_columns
    
    def get_column_type(self, table_name, column_name):
        """Get the data type of a specific column"""
        if table_name in self.table_schemas and column_name in self.table_schemas[table_name]['columns']:
            return self.table_schemas[table_name]['columns'][column_name]['type']
        return 'VARCHAR'
    
    def build_query(self, config):
        """Build SQL query from configuration"""
        try:
            query_parts = []
            required_joins = set()
            
            # SELECT clause
            columns = config.get('columns', [])
            if not columns:
                raise ValueError("No columns specified")
            
            primary_table = config.get('primary_table')
            if not primary_table:
                raise ValueError("No primary table specified")
            
            # Get available columns and enhanced columns for validation
            available_columns = self.get_table_columns(primary_table)
            enhanced_columns = self.get_enhanced_table_columns(primary_table)
            
            # Create a lookup for enhanced columns
            enhanced_lookup = {col['name']: col for col in enhanced_columns}
            
            # Handle column aliases and aggregations
            formatted_columns = []
            for col in columns:
                # Handle both string column names and column objects
                if isinstance(col, dict):
                    column_name = col.get('name', col)
                else:
                    column_name = col
                
                # Check if this is a foreign key column that needs a JOIN
                if column_name in enhanced_lookup and enhanced_lookup[column_name].get('is_foreign_key'):
                    join_info = enhanced_lookup[column_name]['join_info']
                    required_joins.add((
                        join_info['table'], 
                        f"{primary_table}.{join_info['local_key']}", 
                        f"{join_info['table']}.{join_info['foreign_key']}"
                    ))
                    formatted_columns.append(column_name)
                else:
                    # Extract column name without table prefix for validation
                    base_column_name = column_name.split('.')[-1] if '.' in column_name else column_name
                    
                    # Validate column exists in primary table
                    if base_column_name not in available_columns:
                        raise ValueError(f"Column '{base_column_name}' does not exist in table '{primary_table}'. Available columns: {', '.join(available_columns)}")
                        
                    if '.' not in column_name:
                        column_name = f"{primary_table}.{column_name}"
                    formatted_columns.append(column_name)
            
            query_parts.append(f"SELECT {', '.join(formatted_columns)}")
            
            # FROM clause
            query_parts.append(f"FROM {primary_table}")
            
            # Add required JOINs for foreign key columns
            for join_table, local_key, foreign_key in required_joins:
                query_parts.append(f"LEFT JOIN {join_table} ON {local_key} = {foreign_key}")
            
            # Additional JOIN clauses from config
            joins = config.get('joins', [])
            for join in joins:
                join_type = join.get('type', 'INNER')
                join_table = join.get('table')
                join_condition = join.get('condition')
                
                if join_table and join_condition:
                    query_parts.append(f"{join_type} JOIN {join_table} ON {join_condition}")
            
            # WHERE clause
            filters = config.get('filters', [])
            if filters:
                where_conditions = []
                for filter_config in filters:
                    condition = self._build_filter_condition(filter_config)
                    if condition:
                        where_conditions.append(condition)
                
                if where_conditions:
                    query_parts.append(f"WHERE {' AND '.join(where_conditions)}")
            
            # GROUP BY clause
            group_by = config.get('group_by', [])
            if group_by:
                query_parts.append(f"GROUP BY {', '.join(group_by)}")
            
            # ORDER BY clause
            order_by = config.get('order_by')
            sorting = config.get('sorting', {})
            
            if order_by:
                direction = config.get('order_direction', 'ASC')
                query_parts.append(f"ORDER BY {order_by} {direction}")
            elif sorting and sorting.get('column'):
                sort_column = sorting.get('column')
                sort_order = sorting.get('order', 'ASC')
                # Add table prefix if not present
                if '.' not in sort_column:
                    sort_column = f"{config['primary_table']}.{sort_column}"
                query_parts.append(f"ORDER BY {sort_column} {sort_order}")
            
            # LIMIT clause
            limit = config.get('limit')
            if limit and isinstance(limit, int) and limit > 0:
                query_parts.append(f"LIMIT {limit}")
            
            return ' '.join(query_parts)
            
        except Exception as e:
            raise Exception(f"Error building query: {str(e)}")
    
    def _build_filter_condition(self, filter_config):
        """Build a single filter condition"""
        column = filter_config.get('column')
        operator = filter_config.get('operator')
        value = filter_config.get('value')
        value2 = filter_config.get('value2')
        
        if not column or not operator:
            return None
        
        # Handle different operators
        if operator == 'eq':
            return f"{column} = '{value}'"
        elif operator == 'ne':
            return f"{column} != '{value}'"
        elif operator == 'gt':
            return f"{column} > '{value}'"
        elif operator == 'ge':
            return f"{column} >= '{value}'"
        elif operator == 'lt':
            return f"{column} < '{value}'"
        elif operator == 'le':
            return f"{column} <= '{value}'"
        elif operator == 'like':
            return f"{column} LIKE '%{value}%'"
        elif operator == 'ilike':
            return f"LOWER({column}) LIKE LOWER('%{value}%')"
        elif operator == 'in':
            values = [f"'{v.strip()}'" for v in value.split(',')]
            return f"{column} IN ({', '.join(values)})"
        elif operator == 'not_in':
            values = [f"'{v.strip()}'" for v in value.split(',')]
            return f"{column} NOT IN ({', '.join(values)})"
        elif operator == 'between':
            return f"{column} BETWEEN '{value}' AND '{value2}'"
        elif operator == 'is_null':
            return f"{column} IS NULL"
        elif operator == 'is_not_null':
            return f"{column} IS NOT NULL"
        elif operator == 'starts_with':
            return f"{column} LIKE '{value}%'"
        elif operator == 'ends_with':
            return f"{column} LIKE '%{value}'"
        
        return None
    
    def execute_query(self, query, params=None):
        """Execute a SQL query and return results"""
        try:
            start_time = datetime.now()
            
            # Execute query
            result = db.session.execute(text(query), params or {})
            
            # Convert to list of dictionaries
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'data': rows,
                'columns': list(columns),
                'row_count': len(rows),
                'execution_time': execution_time,
                'query': query
            }
            
        except SQLAlchemyError as e:
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'query': query
            }
    
    def export_to_csv(self, data, filename=None):
        """Export data to CSV format"""
        if not data or not data.get('data'):
            return None
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data['columns'])
        writer.writeheader()
        writer.writerows(data['data'])
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
    
    def export_to_excel(self, data, filename=None):
        """Export data to Excel format"""
        if not data or not data.get('data'):
            return None
        
        df = pd.DataFrame(data['data'])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Report', index=False)
        
        excel_content = output.getvalue()
        output.close()
        
        return excel_content
    
    def get_suggested_joins(self, primary_table, target_table):
        """Suggest possible join conditions between tables"""
        suggestions = []
        
        primary_fks = self.table_schemas.get(primary_table, {}).get('foreign_keys', [])
        target_fks = self.table_schemas.get(target_table, {}).get('foreign_keys', [])
        
        # Check if primary table has FK to target table
        for fk in primary_fks:
            if fk['referred_table'] == target_table:
                suggestions.append({
                    'condition': f"{primary_table}.{fk['constrained_columns'][0]} = {target_table}.{fk['referred_columns'][0]}",
                    'type': 'INNER',
                    'description': f"Join on {fk['constrained_columns'][0]}"
                })
        
        # Check if target table has FK to primary table
        for fk in target_fks:
            if fk['referred_table'] == primary_table:
                suggestions.append({
                    'condition': f"{target_table}.{fk['constrained_columns'][0]} = {primary_table}.{fk['referred_columns'][0]}",
                    'type': 'INNER',
                    'description': f"Join on {fk['constrained_columns'][0]}"
                })
        
        return suggestions

class ReportValidator:
    """Validates report configurations and queries"""
    
    @staticmethod
    def validate_config(config):
        """Validate report configuration"""
        errors = []
        
        # Check required fields
        if not config.get('primary_table'):
            errors.append("Primary table is required")
        
        if not config.get('columns'):
            errors.append("At least one column must be selected")
        
        # Validate filters
        filters = config.get('filters', [])
        for i, filter_config in enumerate(filters):
            if not filter_config.get('column'):
                errors.append(f"Filter {i+1}: Column is required")
            if not filter_config.get('operator'):
                errors.append(f"Filter {i+1}: Operator is required")
            
            # Check if value is required for operator
            operator = filter_config.get('operator')
            if operator not in ['is_null', 'is_not_null'] and not filter_config.get('value'):
                errors.append(f"Filter {i+1}: Value is required for {operator} operator")
            
            if operator == 'between' and not filter_config.get('value2'):
                errors.append(f"Filter {i+1}: Second value is required for between operator")
        
        return errors
    
    @staticmethod
    def validate_query_safety(query):
        """Basic validation to prevent dangerous queries"""
        import re
        
        # Define dangerous SQL patterns that should be blocked
        dangerous_patterns = [
            r'\bDROP\s+TABLE\b',
            r'\bDROP\s+DATABASE\b', 
            r'\bDELETE\s+FROM\b',
            r'\bINSERT\s+INTO\b',
            r'\bUPDATE\s+\w+\s+SET\b',
            r'\bALTER\s+TABLE\b',
            r'\bCREATE\s+TABLE\b',
            r'\bCREATE\s+DATABASE\b',
            r'\bTRUNCATE\s+TABLE\b',
            r'\bEXEC\b',
            r'\bEXECUTE\b',
            r'\bDECLARE\b',
            r';\s*DROP\b',
            r';\s*DELETE\b',
            r';\s*INSERT\b',
            r';\s*UPDATE\b',
            r';\s*ALTER\b',
            r';\s*CREATE\b',
            r';\s*TRUNCATE\b'
        ]
        
        query_upper = query.upper()
        
        # Check for dangerous patterns
        for pattern in dangerous_patterns:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return False, f"Query contains potentially dangerous SQL pattern"
        
        # Allow SELECT queries only (our reporting engine should only generate SELECT)
        if not query_upper.strip().startswith('SELECT'):
            return False, "Only SELECT queries are allowed"
        
        return True, "Query appears safe"
