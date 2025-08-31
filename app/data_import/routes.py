"""
Data Import Routes
Routes for the data import module
"""

import os
import json
from flask import render_template, redirect, url_for, flash, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app.data_import import bp
from app.data_import.forms import UploadForm, MappingForm, ApprovalForm, ProcessForm, TemplateForm
from app.models import ImportBatch, ImportBatchRow, ImportTemplate, ImportStatus, User
from app.data_import.utils import (DataImportProcessor, save_uploaded_file, 
                                 create_import_batch_from_excel)
from app import db
from datetime import datetime
import pandas as pd

@bp.route('/dashboard')
@login_required
def dashboard():
    """Data import dashboard"""
    # Get import statistics
    stats = {
        'total_batches': ImportBatch.query.count(),
        'pending_approval': ImportBatch.query.filter_by(status=ImportStatus.PENDING).count(),
        'processing': ImportBatch.query.filter_by(status=ImportStatus.IMPORTING).count(),
        'completed_today': ImportBatch.query.filter(
            ImportBatch.import_completed_at >= datetime.now().date()
        ).count()
    }
    
    # Get recent batches
    recent_batches = ImportBatch.query.order_by(ImportBatch.created_at.desc()).limit(10).all()
    
    # Get pending approvals (for admins)
    pending_approvals = []
    if current_user.role.name in ['admin', 'manager']:
        pending_approvals = ImportBatch.query.filter_by(
            status=ImportStatus.VALIDATED
        ).order_by(ImportBatch.created_at.desc()).limit(5).all()
    
    return render_template('data_import/dashboard.html',
                         stats=stats,
                         recent_batches=recent_batches,
                         pending_approvals=pending_approvals)

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload and analyze data file"""
    form = UploadForm()
    
    if form.validate_on_submit():
        try:
            # Save uploaded file
            file_path = save_uploaded_file(form.file.data, form.batch_name.data)
            if not file_path:
                flash('Failed to save uploaded file', 'error')
                return redirect(url_for('data_import.upload'))
            
            # Create import batch
            batch, error = create_import_batch_from_excel(
                file_path=file_path,
                batch_name=form.batch_name.data,
                target_table=form.target_table.data,
                description=form.description.data,
                user_id=current_user.id
            )
            
            if error:
                flash(f'Error creating import batch: {error}', 'error')
                return redirect(url_for('data_import.upload'))
            
            flash(f'File uploaded successfully! Batch ID: {batch.id}', 'success')
            return redirect(url_for('data_import.mapping', batch_id=batch.id))
            
        except Exception as e:
            flash(f'Error uploading file: {str(e)}', 'error')
    
    return render_template('data_import/upload.html', form=form)

@bp.route('/mapping/<int:batch_id>', methods=['GET', 'POST'])
@login_required
def mapping(batch_id):
    """Configure column mapping for import batch"""
    batch = ImportBatch.query.get_or_404(batch_id)
    
    # Check permissions
    if batch.created_by_id != current_user.id and current_user.role.name not in ['admin', 'manager']:
        flash('You do not have permission to access this batch', 'error')
        return redirect(url_for('data_import.dashboard'))
    
    # Analyze the uploaded file
    processor = DataImportProcessor()
    analysis, error = processor.analyze_excel_file(batch.file_path, batch.target_table)
    
    if error:
        flash(f'Error analyzing file: {error}', 'error')
        return redirect(url_for('data_import.dashboard'))
    
    form = MappingForm()
    form.batch_id.data = batch_id
    
    if form.validate_on_submit():
        try:
            # Save mapping configuration
            mapping_config = json.loads(form.mapping_config.data)
            batch.mapping_config_dict = mapping_config
            
            # Validate the data
            success, message = processor.validate_import_data(batch_id)
            if success:
                batch.status = ImportStatus.VALIDATING
                db.session.commit()
                flash(f'Mapping applied and validation completed: {message}', 'success')
                return redirect(url_for('data_import.review', batch_id=batch_id))
            else:
                flash(f'Validation failed: {message}', 'error')
                
        except json.JSONDecodeError:
            flash('Invalid mapping configuration format', 'error')
        except Exception as e:
            flash(f'Error applying mapping: {str(e)}', 'error')
    
    return render_template('data_import/mapping.html',
                         form=form,
                         batch=batch,
                         analysis=analysis)

@bp.route('/review/<int:batch_id>')
@login_required
def review(batch_id):
    """Review import batch validation results"""
    batch = ImportBatch.query.get_or_404(batch_id)
    
    # Check permissions
    if batch.created_by_id != current_user.id and current_user.role.name not in ['admin', 'manager']:
        flash('You do not have permission to access this batch', 'error')
        return redirect(url_for('data_import.dashboard'))
    
    # Get validation results
    valid_rows = batch.rows.filter_by(is_valid=True).limit(100).all()
    invalid_rows = batch.rows.filter_by(is_valid=False).limit(100).all()
    
    return render_template('data_import/review.html',
                         batch=batch,
                         valid_rows=valid_rows,
                         invalid_rows=invalid_rows)

@bp.route('/approve/<int:batch_id>', methods=['GET', 'POST'])
@login_required
def approve(batch_id):
    """Approve or reject import batch"""
    # Check admin permissions
    if current_user.role.name not in ['admin', 'manager']:
        flash('You do not have permission to approve import batches', 'error')
        return redirect(url_for('data_import.dashboard'))
    
    batch = ImportBatch.query.get_or_404(batch_id)
    form = ApprovalForm()
    form.batch_id.data = batch_id
    
    if form.validate_on_submit():
        try:
            action = form.action.data
            
            if action == 'approve':
                batch.status = ImportStatus.APPROVED
                batch.approved_by_id = current_user.id
                batch.approved_at = datetime.now()
                batch.approval_notes = form.approval_notes.data
                flash('Import batch approved successfully', 'success')
            elif action == 'reject':
                batch.status = ImportStatus.REJECTED
                batch.approved_by_id = current_user.id
                batch.approved_at = datetime.now()
                batch.approval_notes = form.approval_notes.data
                flash('Import batch rejected', 'warning')
            
            db.session.commit()
            return redirect(url_for('data_import.dashboard'))
            
        except Exception as e:
            flash(f'Error updating batch status: {str(e)}', 'error')
    
    return render_template('data_import/approve.html', form=form, batch=batch)

@bp.route('/process/<int:batch_id>', methods=['GET', 'POST'])
@login_required
def process_batch(batch_id):
    """Process approved import batch"""
    batch = ImportBatch.query.get_or_404(batch_id)
    
    # Check permissions
    if batch.created_by_id != current_user.id and current_user.role.name not in ['admin', 'manager']:
        flash('You do not have permission to process this batch', 'error')
        return redirect(url_for('data_import.dashboard'))
    
    if batch.status != ImportStatus.APPROVED:
        flash('Batch must be approved before processing', 'error')
        return redirect(url_for('data_import.review', batch_id=batch_id))
    
    form = ProcessForm()
    form.batch_id.data = batch_id
    
    if form.validate_on_submit():
        try:
            processor = DataImportProcessor()
            success, message = processor.process_import_batch(batch_id, current_user.id)
            
            if success:
                flash(f'Import completed successfully: {message}', 'success')
            else:
                flash(f'Import failed: {message}', 'error')
                
            return redirect(url_for('data_import.view_batch', batch_id=batch_id))
            
        except Exception as e:
            flash(f'Error processing batch: {str(e)}', 'error')
    
    return render_template('data_import/process.html', form=form, batch=batch)

@bp.route('/batch/<int:batch_id>')
@login_required
def view_batch(batch_id):
    """View import batch details"""
    batch = ImportBatch.query.get_or_404(batch_id)
    
    # Check basic permissions
    if batch.created_by_id != current_user.id and current_user.role.name not in ['admin', 'manager']:
        flash('You do not have permission to view this batch', 'error')
        return redirect(url_for('data_import.dashboard'))
    
    # Get row details with pagination
    page = request.args.get('page', 1, type=int)
    rows = batch.rows.paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('data_import/view_batch.html', batch=batch, rows=rows)

@bp.route('/batches')
@login_required
def list_batches():
    """List all import batches"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = ImportBatch.query
    
    # Apply filters
    if status_filter:
        query = query.filter_by(status=ImportStatus(status_filter))
    
    # Apply permissions
    if current_user.role.name not in ['admin', 'manager']:
        query = query.filter_by(created_by_id=current_user.id)
    
    batches = query.order_by(ImportBatch.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('data_import/list_batches.html', 
                         batches=batches, 
                         status_filter=status_filter)

@bp.route('/templates')
@login_required
def list_templates():
    """List import templates"""
    templates = ImportTemplate.query.filter_by(is_active=True).order_by(ImportTemplate.name).all()
    return render_template('data_import/list_templates.html', templates=templates)

@bp.route('/templates/create', methods=['GET', 'POST'])
@login_required
def create_template():
    """Create import template"""
    # Check admin permissions
    if current_user.role.name not in ['admin', 'manager']:
        flash('You do not have permission to create templates', 'error')
        return redirect(url_for('data_import.list_templates'))
    
    form = TemplateForm()
    
    if form.validate_on_submit():
        try:
            template = ImportTemplate(
                name=form.name.data,
                target_table=form.target_table.data,
                description=form.description.data,
                column_mapping=form.column_mapping.data,
                validation_rules=form.validation_rules.data,
                is_active=form.is_active.data,
                created_by_id=current_user.id
            )
            db.session.add(template)
            db.session.commit()
            
            flash('Template created successfully', 'success')
            return redirect(url_for('data_import.list_templates'))
            
        except Exception as e:
            flash(f'Error creating template: {str(e)}', 'error')
    
    return render_template('data_import/create_template.html', form=form)

@bp.route('/templates/<int:template_id>/download')
@login_required
def download_template(template_id):
    """Download Excel template"""
    template = ImportTemplate.query.get_or_404(template_id)
    
    try:
        processor = DataImportProcessor()
        df = processor.generate_excel_template(template.target_table, include_sample_data=True)
        
        if df is None:
            flash('Error generating template', 'error')
            return redirect(url_for('data_import.list_templates'))
        
        # Save to temporary file
        temp_path = os.path.join(current_app.instance_path, 'temp')
        os.makedirs(temp_path, exist_ok=True)
        
        filename = f"{template.name}_{template.target_table}_template.xlsx"
        file_path = os.path.join(temp_path, filename)
        
        df.to_excel(file_path, index=False)
        
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f'Error downloading template: {str(e)}', 'error')
        return redirect(url_for('data_import.list_templates'))

@bp.route('/api/table-schema/<table_name>')
@login_required
def api_table_schema(table_name):
    """API endpoint to get table schema"""
    processor = DataImportProcessor()
    schema = processor.get_table_schema(table_name)
    
    if schema:
        return jsonify({'success': True, 'schema': schema})
    else:
        return jsonify({'success': False, 'error': 'Table not found'}), 404

@bp.route('/api/suggest-mapping', methods=['POST'])
@login_required
def api_suggest_mapping():
    """API endpoint to suggest column mapping"""
    data = request.get_json()
    excel_columns = data.get('excel_columns', [])
    target_table = data.get('target_table', '')
    
    processor = DataImportProcessor()
    schema = processor.get_table_schema(target_table)
    
    if schema:
        mapping = processor._suggest_column_mapping(excel_columns, schema)
        return jsonify({'success': True, 'mapping': mapping})
    else:
        return jsonify({'success': False, 'error': 'Table not found'}), 404
