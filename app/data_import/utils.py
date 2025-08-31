"""
Data Import Utilities
Helper functions for data import operations
"""

import pandas as pd
import json
import os
import re
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from flask import current_app
from app import db
from app.models import (User, Product, Company, WorkOrder, Category, Priority, 
                       InventoryItem, InventoryCategory, ProductCategory, 
                       UAVServiceIncident, AssignmentGroup, ImportBatch, 
                       ImportBatchRow, ImportTemplate, ImportStatus)
from sqlalchemy import inspect

class DataImportProcessor:
    """Main class for processing data imports"""
    
    def __init__(self):
        self.supported_tables = {
            'users': User,
            'products': Product,
            'companies': Company,
            'inventory_items': InventoryItem,
            'inventory_categories': InventoryCategory,
            'workorders': WorkOrder,
            'product_categories': ProductCategory,
            'uav_service_incidents': UAVServiceIncident,
            'assignment_groups': AssignmentGroup,
        }
    
    def get_table_schema(self, table_name):
        """Get database schema for a table"""
        if table_name not in self.supported_tables:
            return None
        
        model = self.supported_tables[table_name]
        inspector = inspect(db.engine)
        columns = inspector.get_columns(model.__tablename__)
        
        schema = {}
        for col in columns:
            schema[col['name']] = {
                'type': str(col['type']),
                'nullable': col['nullable'],
                'primary_key': col.get('primary_key', False),
                'autoincrement': col.get('autoincrement', False)
            }
        
        return schema
    
    def generate_excel_template(self, table_name, include_sample_data=True):
        """Generate Excel template for a specific table"""
        schema = self.get_table_schema(table_name)
        if not schema:
            return None
        
        # Filter out system fields that shouldn't be in templates
        excluded_fields = ['id', 'created_at', 'updated_at', 'password_hash']
        template_columns = {k: v for k, v in schema.items() 
                          if k not in excluded_fields and not v['autoincrement']}
        
        # Create DataFrame with column headers
        df = pd.DataFrame(columns=list(template_columns.keys()))
        
        if include_sample_data:
            sample_data = self._get_sample_data(table_name, template_columns)
            if sample_data:
                df = pd.DataFrame(sample_data)
        
        return df
    
    def _get_sample_data(self, table_name, columns):
        """Generate sample data for templates"""
        sample_data = {}
        
        if table_name == 'users':
            sample_data = {
                'username': ['john.doe', 'jane.smith'],
                'email': ['john.doe@company.com', 'jane.smith@company.com'],
                'first_name': ['John', 'Jane'],
                'last_name': ['Doe', 'Smith'],
                'is_active': [True, True],
                'role_id': [2, 2]  # Assuming role ID 2 is user
            }
        elif table_name == 'products':
            sample_data = {
                'product_code': ['UAV-001', 'UAV-002'],
                'product_name': ['DJI Mavic Air 2', 'DJI Mini 3 Pro'],
                'serial_number': ['MA2001', 'MP3001'],
                'description': ['Professional drone for aerial photography', 'Compact drone for beginners'],
                'manufacturer': ['DJI', 'DJI'],
                'max_flight_time': [34, 47],
                'max_range': [10, 12],
                'weight': [570, 249],
                'owner_company_id': [1, 1]  # Assuming company ID 1 exists
            }
        elif table_name == 'companies':
            sample_data = {
                'name': ['Acme Drones Inc', 'SkyTech Solutions'],
                'registration_number': ['REG001', 'REG002'],
                'email': ['contact@acmedrones.com', 'info@skytech.com'],
                'phone': ['+1-555-0001', '+1-555-0002'],
                'city': ['New York', 'Los Angeles'],
                'country': ['USA', 'USA']
            }
        elif table_name == 'inventory_items':
            sample_data = {
                'part_number': ['PROP-001', 'BAT-001'],
                'name': ['Carbon Fiber Propeller', 'LiPo Battery 4S 5000mAh'],
                'description': ['High-quality carbon fiber propeller', 'High-capacity lithium polymer battery'],
                'manufacturer': ['Generic', 'Tattu'],
                'quantity_in_stock': [50, 25],
                'minimum_stock_level': [10, 5],
                'unit_cost': [15.99, 89.99],
                'condition': ['new', 'new'],
                'category_id': [1, 2]  # Assuming category IDs exist
            }
        
        # Filter sample data to only include columns that exist in the table
        filtered_sample = {}
        for key, value in sample_data.items():
            if key in columns:
                filtered_sample[key] = value
        
        return filtered_sample
    
    def analyze_excel_file(self, file_path, target_table):
        """Analyze uploaded Excel file and return structure info"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Get table schema
            schema = self.get_table_schema(target_table)
            if not schema:
                return None, "Unsupported table"
            
            analysis = {
                'total_rows': len(df),
                'columns': list(df.columns),
                'sample_data': df.head(5).to_dict('records'),
                'schema': schema,
                'suggested_mapping': self._suggest_column_mapping(df.columns, schema)
            }
            
            return analysis, None
        except Exception as e:
            return None, str(e)
    
    def _suggest_column_mapping(self, excel_columns, db_schema):
        """Suggest mapping between Excel columns and database fields"""
        mapping = {}
        
        for excel_col in excel_columns:
            # Clean column name for comparison
            clean_excel = self._clean_column_name(excel_col)
            
            # Find best match in database schema
            best_match = None
            best_score = 0
            
            for db_field in db_schema.keys():
                clean_db = self._clean_column_name(db_field)
                score = self._calculate_similarity(clean_excel, clean_db)
                
                if score > best_score and score > 0.6:  # Threshold for suggesting
                    best_match = db_field
                    best_score = score
            
            if best_match:
                mapping[excel_col] = best_match
        
        return mapping
    
    def _clean_column_name(self, name):
        """Clean column name for comparison"""
        # Convert to lowercase, remove special characters, replace spaces with underscores
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', str(name).lower())
        clean_name = re.sub(r'\s+', '_', clean_name.strip())
        return clean_name
    
    def _calculate_similarity(self, str1, str2):
        """Calculate similarity between two strings"""
        # Simple similarity calculation based on common substrings
        if str1 == str2:
            return 1.0
        
        # Check if one string contains the other
        if str1 in str2 or str2 in str1:
            return 0.8
        
        # Check for common words
        words1 = set(str1.split('_'))
        words2 = set(str2.split('_'))
        common_words = words1.intersection(words2)
        
        if common_words:
            return len(common_words) / max(len(words1), len(words2))
        
        return 0.0
    
    def validate_import_data(self, batch_id):
        """Validate data in an import batch"""
        batch = ImportBatch.query.get(batch_id)
        if not batch:
            return False, "Batch not found"
        
        schema = self.get_table_schema(batch.target_table)
        if not schema:
            return False, "Invalid target table"
        
        mapping = batch.mapping_config_dict
        validation_errors = []
        valid_count = 0
        
        for row in batch.rows:
            row_errors = []
            mapped_data = {}
            original_data = row.original_data_dict
            
            # Apply column mapping
            for excel_col, db_field in mapping.items():
                if excel_col in original_data:
                    mapped_data[db_field] = original_data[excel_col]
            
            # Validate required fields
            for field_name, field_info in schema.items():
                if not field_info['nullable'] and field_name not in mapped_data:
                    if not field_info['autoincrement'] and field_name not in ['id', 'created_at', 'updated_at']:
                        row_errors.append(f"Required field '{field_name}' is missing")
            
            # Validate data types and constraints
            for field_name, value in mapped_data.items():
                if field_name in schema:
                    field_type = schema[field_name]['type']
                    validation_error = self._validate_field_value(field_name, value, field_type, batch.target_table)
                    if validation_error:
                        row_errors.append(validation_error)
            
            # Update row validation status
            row.mapped_data_dict = mapped_data
            row.validation_errors_list = row_errors
            row.is_valid = len(row_errors) == 0
            
            if row.is_valid:
                valid_count += 1
        
        # Update batch statistics
        batch.valid_rows = valid_count
        batch.invalid_rows = batch.total_rows - valid_count
        batch.status = ImportStatus.VALIDATING
        
        db.session.commit()
        return True, f"Validation complete: {valid_count}/{batch.total_rows} rows valid"
    
    def _validate_field_value(self, field_name, value, field_type, table_name):
        """Validate individual field value"""
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None  # Empty values are handled by nullable check
        
        try:
            # Basic type validation
            if 'INTEGER' in field_type.upper():
                int(value)
            elif 'FLOAT' in field_type.upper() or 'NUMERIC' in field_type.upper():
                float(value)
            elif 'BOOLEAN' in field_type.upper():
                if isinstance(value, str):
                    value_lower = value.lower()
                    if value_lower not in ['true', 'false', '1', '0', 'yes', 'no']:
                        return f"Invalid boolean value for {field_name}: {value}"
            elif 'DATE' in field_type.upper():
                if isinstance(value, str):
                    pd.to_datetime(value)
            
            # Table-specific validation
            if table_name == 'users' and field_name == 'email':
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(value)):
                    return f"Invalid email format: {value}"
            
            return None
        except (ValueError, TypeError) as e:
            return f"Invalid value for {field_name}: {value} ({str(e)})"
    
    def process_import_batch(self, batch_id, user_id):
        """Process an approved import batch"""
        batch = ImportBatch.query.get(batch_id)
        if not batch:
            return False, "Batch not found"
        
        if batch.status != ImportStatus.APPROVED:
            return False, "Batch not approved for processing"
        
        model_class = self.supported_tables.get(batch.target_table)
        if not model_class:
            return False, "Unsupported table"
        
        batch.status = ImportStatus.PROCESSING
        batch.started_at = datetime.now(timezone.utc)
        db.session.commit()
        
        processed_count = 0
        error_count = 0
        
        try:
            for row in batch.rows.filter_by(is_valid=True):
                try:
                    # Create new record
                    mapped_data = row.mapped_data_dict
                    
                    # Add audit fields
                    if hasattr(model_class, 'created_by_id'):
                        mapped_data['created_by_id'] = user_id
                    
                    new_record = model_class(**mapped_data)
                    db.session.add(new_record)
                    db.session.flush()  # Get the ID
                    
                    # Update row status
                    row.is_processed = True
                    row.processing_result = 'success'
                    row.created_record_id = new_record.id
                    row.processed_at = datetime.now(timezone.utc)
                    
                    processed_count += 1
                    
                except Exception as e:
                    row.is_processed = True
                    row.processing_result = 'failed'
                    row.processing_error = str(e)
                    row.processed_at = datetime.now(timezone.utc)
                    error_count += 1
                    
                    # Rollback this record but continue with others
                    db.session.rollback()
            
            # Update batch status
            batch.processed_rows = processed_count
            batch.status = ImportStatus.COMPLETED
            batch.completed_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return True, f"Import completed: {processed_count} records created, {error_count} errors"
            
        except Exception as e:
            batch.status = ImportStatus.FAILED
            db.session.rollback()
            return False, f"Import failed: {str(e)}"

# Helper functions
def save_uploaded_file(file, batch_name):
    """Save uploaded file and return file path"""
    if not file:
        return None
    
    # Create uploads directory if it doesn't exist
    upload_dir = os.path.join(current_app.instance_path, 'uploads', 'imports')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{secure_filename(batch_name)}_{timestamp}_{secure_filename(file.filename)}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    file.save(file_path)
    return file_path

def create_import_batch_from_excel(file_path, batch_name, target_table, description, user_id):
    """Create import batch from Excel file"""
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Create import batch
        batch = ImportBatch(
            batch_name=batch_name,
            target_table=target_table,
            file_name=os.path.basename(file_path),
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            total_rows=len(df),
            created_by_id=user_id
        )
        db.session.add(batch)
        db.session.flush()  # Get batch ID
        
        # Create batch rows
        for index, row in df.iterrows():
            # Convert row to dictionary, handling NaN values
            row_data = {}
            for col, value in row.items():
                if pd.isna(value):
                    row_data[col] = None
                else:
                    row_data[col] = value
            
            batch_row = ImportBatchRow(
                batch_id=batch.id,
                row_number=index + 1,
                original_data_dict=row_data
            )
            db.session.add(batch_row)
        
        db.session.commit()
        return batch, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)
