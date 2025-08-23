"""
Reporting Engine Routes
"""

import json
import io
from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash, request, jsonify, send_file, abort
from flask_login import login_required, current_user
from sqlalchemy import desc
from app import db
from app.models import User
from app.reporting import bp
from app.reporting.forms import ReportBuilderForm, ReportFilterForm, SavedReportForm, ReportScheduleForm
from app.reporting.models import SavedReport, ReportSchedule, ReportExecutionLog
from app.reporting.engine import ReportEngine, ReportValidator

# Initialize report engine lazily
def get_report_engine():
    return ReportEngine()

@bp.route('/')
@login_required
def dashboard():
    """Reporting dashboard"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to access reporting.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get recent reports
    recent_reports = SavedReport.query.filter_by(created_by_id=current_user.id)\
                                    .order_by(desc(SavedReport.updated_at))\
                                    .limit(5).all()
    
    # Get public reports
    public_reports = SavedReport.query.filter_by(is_public=True)\
                                    .order_by(desc(SavedReport.view_count))\
                                    .limit(5).all()
    
    # Get recent executions
    recent_executions = ReportExecutionLog.query.filter_by(executed_by_id=current_user.id)\
                                               .order_by(desc(ReportExecutionLog.started_at))\
                                               .limit(10).all()
    
    # Get statistics
    stats = {
        'total_reports': SavedReport.query.filter_by(created_by_id=current_user.id).count(),
        'public_reports': SavedReport.query.filter_by(is_public=True).count(),
        'total_executions': ReportExecutionLog.query.filter_by(executed_by_id=current_user.id).count(),
        'scheduled_reports': ReportSchedule.query.filter_by(created_by_id=current_user.id, is_active=True).count()
    }
    
    return render_template('reporting/dashboard.html',
                         recent_reports=recent_reports,
                         public_reports=public_reports,
                         recent_executions=recent_executions,
                         stats=stats)

@bp.route('/builder')
@login_required
def report_builder():
    """Report builder interface"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to create reports.', 'error')
        return redirect(url_for('reporting.dashboard'))
    
    return render_template('reporting/builder.html',
                         available_tables=get_report_engine().available_tables)

@bp.route('/api/tables')
@login_required
def api_tables():
    """API endpoint to get available tables"""
    return jsonify(get_report_engine().available_tables)

@bp.route('/api/columns/<table_name>')
@login_required
def api_columns(table_name):
    """API endpoint to get columns for a table"""
    engine = get_report_engine()
    columns = engine.get_table_columns(table_name)
    column_info = []
    
    for col in columns:
        col_type = engine.get_column_type(table_name, col)
        column_info.append({
            'name': col,
            'display_name': col.replace('_', ' ').title(),
            'type': col_type
        })
    
    return jsonify(column_info)

@bp.route('/api/suggested-joins/<primary_table>/<target_table>')
@login_required
def api_suggested_joins(primary_table, target_table):
    """API endpoint to get suggested joins between tables"""
    suggestions = get_report_engine().get_suggested_joins(primary_table, target_table)
    return jsonify(suggestions)

@bp.route('/api/execute', methods=['POST'])
@login_required
def api_execute_report():
    """API endpoint to execute a report"""
    try:
        config = request.get_json()
        
        # Validate configuration
        errors = ReportValidator.validate_config(config)
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # Build and validate query
        engine = get_report_engine()
        query = engine.build_query(config)
        is_safe, safety_message = ReportValidator.validate_query_safety(query)
        
        if not is_safe:
            return jsonify({'success': False, 'error': safety_message}), 400
        
        # Execute query
        result = engine.execute_query(query)
        
        # Log execution
        if result['success']:
            log = ReportExecutionLog(
                executed_by_id=current_user.id,
                execution_time=result['execution_time'],
                row_count=result['row_count'],
                status='success'
            )
            db.session.add(log)
            db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/save', methods=['POST'])
@login_required
def api_save_report():
    """API endpoint to save a report"""
    try:
        data = request.get_json()
        config = data.get('config')
        metadata = data.get('metadata', {})
        
        # Validate configuration
        errors = ReportValidator.validate_config(config)
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # Create or update report
        report_id = data.get('report_id')
        if report_id:
            report = SavedReport.query.get_or_404(report_id)
            if report.created_by_id != current_user.id and not current_user.has_role('admin'):
                return jsonify({'success': False, 'error': 'Permission denied'}), 403
        else:
            report = SavedReport(created_by_id=current_user.id)
        
        report.name = metadata.get('name', 'Untitled Report')
        report.description = metadata.get('description', '')
        report.is_public = metadata.get('is_public', False)
        report.tags = metadata.get('tags', '')
        report.set_config(config)
        
        if not report_id:
            db.session.add(report)
        
        db.session.commit()
        
        return jsonify({'success': True, 'report_id': report.id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/saved')
@login_required
def saved_reports():
    """List saved reports"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to access reports.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get user's reports
    my_reports = SavedReport.query.filter_by(created_by_id=current_user.id)\
                                 .order_by(desc(SavedReport.updated_at)).all()
    
    # Get public reports
    public_reports = SavedReport.query.filter_by(is_public=True)\
                                     .order_by(desc(SavedReport.view_count)).all()
    
    return render_template('reporting/saved_reports.html',
                         my_reports=my_reports,
                         public_reports=public_reports)

@bp.route('/saved/<int:report_id>')
@login_required
def view_saved_report(report_id):
    """View and execute a saved report"""
    report = SavedReport.query.get_or_404(report_id)
    
    # Check permissions
    if not report.is_public and report.created_by_id != current_user.id:
        if not current_user.has_role('admin'):
            abort(403)
    
    # Increment view count
    report.increment_view_count()
    
    config = report.get_config()
    
    return render_template('reporting/view_report.html',
                         report=report,
                         config=json.dumps(config))

@bp.route('/saved/<int:report_id>/execute')
@login_required
def execute_saved_report(report_id):
    """Execute a saved report and return results"""
    report = SavedReport.query.get_or_404(report_id)
    
    # Check permissions
    if not report.is_public and report.created_by_id != current_user.id:
        if not current_user.has_role('admin'):
            abort(403)
    
    try:
        config = report.get_config()
        
        # Build and execute query
        engine = get_report_engine()
        query = engine.build_query(config)
        result = engine.execute_query(query)
        
        # Log execution
        if result['success']:
            log = ReportExecutionLog(
                report_id=report.id,
                executed_by_id=current_user.id,
                execution_time=result['execution_time'],
                row_count=result['row_count'],
                status='success'
            )
            db.session.add(log)
            db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/saved/<int:report_id>/export/<format>')
@login_required
def export_saved_report(report_id, format):
    """Export a saved report"""
    report = SavedReport.query.get_or_404(report_id)
    
    # Check permissions
    if not report.is_public and report.created_by_id != current_user.id:
        if not current_user.has_role('admin'):
            abort(403)
    
    if format not in ['csv', 'excel']:
        abort(400)
    
    try:
        config = report.get_config()
        
        # Build and execute query
        engine = get_report_engine()
        query = engine.build_query(config)
        result = engine.execute_query(query)
        
        if not result['success']:
            flash(f'Error executing report: {result.get("error")}', 'error')
            return redirect(url_for('reporting.view_saved_report', report_id=report_id))
        
        # Generate export
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join(c for c in report.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        if format == 'csv':
            content = engine.export_to_csv(result)
            filename = f"{safe_name}_{timestamp}.csv"
            mimetype = 'text/csv'
            
            return send_file(
                io.BytesIO(content.encode('utf-8')),
                as_attachment=True,
                download_name=filename,
                mimetype=mimetype
            )
        
        elif format == 'excel':
            content = engine.export_to_excel(result)
            filename = f"{safe_name}_{timestamp}.xlsx"
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            return send_file(
                io.BytesIO(content),
                as_attachment=True,
                download_name=filename,
                mimetype=mimetype
            )
    
    except Exception as e:
        flash(f'Error exporting report: {str(e)}', 'error')
        return redirect(url_for('reporting.view_saved_report', report_id=report_id))

@bp.route('/saved/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_saved_report(report_id):
    """Delete a saved report"""
    report = SavedReport.query.get_or_404(report_id)
    
    # Check permissions
    if report.created_by_id != current_user.id and not current_user.has_role('admin'):
        abort(403)
    
    report_name = report.name
    db.session.delete(report)
    db.session.commit()
    
    flash(f'Report "{report_name}" has been deleted.', 'success')
    return redirect(url_for('reporting.saved_reports'))

@bp.route('/schedules')
@login_required
def report_schedules():
    """List report schedules"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to access scheduled reports.', 'error')
        return redirect(url_for('reporting.dashboard'))
    
    schedules = ReportSchedule.query.order_by(desc(ReportSchedule.created_at)).all()
    
    return render_template('reporting/schedules.html', schedules=schedules)

@bp.route('/schedules/create/<int:report_id>', methods=['GET', 'POST'])
@login_required
def create_schedule(report_id):
    """Create a new report schedule"""
    if not current_user.has_role('admin'):
        abort(403)
    
    report = SavedReport.query.get_or_404(report_id)
    form = ReportScheduleForm()
    
    if form.validate_on_submit():
        schedule = ReportSchedule(
            name=form.name.data,
            report_id=report.id,
            frequency=form.frequency.data,
            export_format=form.format.data,
            is_active=form.is_active.data,
            created_by_id=current_user.id
        )
        
        # Process email recipients
        if form.email_recipients.data:
            recipients = [email.strip() for email in form.email_recipients.data.split('\n') if email.strip()]
            schedule.set_recipients_list(recipients)
        
        schedule.calculate_next_run()
        
        db.session.add(schedule)
        db.session.commit()
        
        flash(f'Schedule "{schedule.name}" has been created.', 'success')
        return redirect(url_for('reporting.report_schedules'))
    
    return render_template('reporting/create_schedule.html', form=form, report=report)

@bp.route('/api/export/<format>', methods=['POST'])
@login_required
def api_export_report(format):
    """API endpoint to export a report directly"""
    if format not in ['csv', 'excel']:
        abort(400)
    
    try:
        config = request.get_json()
        
        # Validate configuration
        errors = ReportValidator.validate_config(config)
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # Build and execute query
        engine = get_report_engine()
        query = engine.build_query(config)
        result = engine.execute_query(query)
        
        if not result['success']:
            return jsonify({'success': False, 'error': result.get('error')}), 400
        
        # Generate export
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'csv':
            content = engine.export_to_csv(result)
            filename = f"custom_report_{timestamp}.csv"
            mimetype = 'text/csv'
            
            return send_file(
                io.BytesIO(content.encode('utf-8')),
                as_attachment=True,
                download_name=filename,
                mimetype=mimetype
            )
        
        elif format == 'excel':
            content = engine.export_to_excel(result)
            filename = f"custom_report_{timestamp}.xlsx"
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            return send_file(
                io.BytesIO(content),
                as_attachment=True,
                download_name=filename,
                mimetype=mimetype
            )
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/quick-stats')
@login_required
def api_quick_stats():
    """API endpoint for quick dashboard statistics"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        # Get basic counts from main tables
        from app.models import WorkOrder, User, Company, Product
        
        stats = {
            'workorders': {
                'total': WorkOrder.query.count(),
                'recent': WorkOrder.query.filter(
                    WorkOrder.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                ).count()
            },
            'users': {
                'total': User.query.count(),
                'active': User.query.filter_by(is_active=True).count()
            },
            'companies': Company.query.count(),
            'products': Product.query.filter_by(is_active=True).count()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
