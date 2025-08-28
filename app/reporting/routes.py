"""
Reporting Routes
Flask routes for the reporting module
"""

from flask import render_template, request, jsonify, flash, redirect, url_for, make_response, send_file
from flask_login import login_required, current_user
from app.reporting import bp
from app.reporting.models import Report, ReportSchedule, ReportExecution, ReportShare
from app.reporting.engine import ReportEngine, ReportValidator
from app.reporting.forms import NewReportForm, ShareReportForm, ScheduleReportForm
from app import db
from datetime import datetime, timedelta
import json
import io
import pandas as pd


@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    """Reporting dashboard with statistics and recent activity"""
    
    # Get user's reports
    user_reports = Report.query.filter_by(created_by=current_user.id).all()
    
    # Calculate statistics
    stats = {
        'total_reports': len(user_reports),
        'active_reports': len([r for r in user_reports if r.status == 'active']),
        'scheduled_reports': ReportSchedule.query.filter(
            ReportSchedule.report_id.in_([r.id for r in user_reports]),
            ReportSchedule.is_active == True
        ).count(),
        'recent_executions': ReportExecution.query.filter(
            ReportExecution.report_id.in_([r.id for r in user_reports]),
            ReportExecution.executed_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
    }
    
    # Get recent reports
    recent_reports = Report.query.filter_by(created_by=current_user.id)\
                          .order_by(Report.updated_at.desc())\
                          .limit(5).all()
    
    # Get recent executions
    recent_executions = ReportExecution.query.join(Report)\
                                           .filter(Report.created_by == current_user.id)\
                                           .order_by(ReportExecution.executed_at.desc())\
                                           .limit(10).all()
    
    # Get scheduled reports
    scheduled_reports = ReportSchedule.query.join(Report)\
                                          .filter(Report.created_by == current_user.id,
                                                 ReportSchedule.is_active == True)\
                                          .order_by(ReportSchedule.next_run.asc())\
                                          .limit(5).all()
    
    return render_template('reporting/dashboard.html',
                         stats=stats,
                         recent_reports=recent_reports,
                         recent_executions=recent_executions,
                         scheduled_reports=scheduled_reports)


@bp.route('/reports')
@login_required
def reports_list():
    """List all reports for the current user"""
    
    # Get filter parameters
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    filter_type = request.args.get('filter', '')
    
    # Base query
    query = Report.query.filter_by(created_by=current_user.id)
    
    # Apply filters
    if search:
        query = query.filter(Report.name.contains(search))
    
    if category:
        query = query.filter_by(category=category)
    
    if status:
        query = query.filter_by(status=status)
    
    if filter_type == 'scheduled':
        query = query.join(ReportSchedule).filter(ReportSchedule.is_active == True)
    elif filter_type == 'shared':
        query = query.join(ReportShare).filter(ReportShare.is_active == True)
    
    # Get reports
    reports = query.order_by(Report.updated_at.desc()).all()
    
    return render_template('reporting/reports_list.html', reports=reports)


@bp.route('/reports/new', methods=['GET', 'POST'])
@login_required
def new_report():
    """Create a new report"""
    
    form = NewReportForm()
    
    if form.validate_on_submit():
        # Create new report
        report = Report(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            data_source=form.data_source.data,
            tags=form.tags.data,
            template_type=form.template.data,
            created_by=current_user.id
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash('Report created successfully!', 'success')
        return redirect(url_for('reporting.report_builder', id=report.id))
    
    return render_template('reporting/new_report.html', form=form)


@bp.route('/reports/<int:id>/builder')
@login_required
def report_builder(id):
    """Report builder interface"""
    
    report = Report.query.get_or_404(id)
    
    # Check if user owns the report
    if report.created_by != current_user.id:
        flash('You do not have permission to edit this report.', 'error')
        return redirect(url_for('reporting.reports_list'))
    
    # Get available tables
    engine = ReportEngine()
    available_tables = engine.get_available_tables()
    
    return render_template('reporting/report_builder.html',
                         report=report,
                         available_tables=available_tables)


@bp.route('/reports/<int:id>/execute', methods=['GET', 'POST'])
@login_required
def execute_report(id):
    """Execute a report"""
    
    report = Report.query.get_or_404(id)
    
    # Check if user owns the report or has access
    if report.created_by != current_user.id:
        flash('You do not have permission to execute this report.', 'error')
        return redirect(url_for('reporting.reports_list'))
    
    try:
        engine = ReportEngine()
        result = engine.execute_report(report)
        
        # Create execution record
        execution = ReportExecution(
            report_id=report.id,
            executed_by=current_user.id,
            status='completed',
            row_count=result.get('row_count', 0),
            execution_time=result.get('execution_time', 0)
        )
        db.session.add(execution)
        
        # Update report last execution
        report.last_execution = datetime.utcnow()
        report.execution_count = (report.execution_count or 0) + 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': result.get('data', []),
            'columns': result.get('columns', []),
            'row_count': result.get('row_count', 0),
            'execution_time': result.get('execution_time', 0)
        })
        
    except Exception as e:
        # Create failed execution record
        execution = ReportExecution(
            report_id=report.id,
            executed_by=current_user.id,
            status='failed',
            error_message=str(e)
        )
        db.session.add(execution)
        db.session.commit()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/tables')
@login_required
def api_tables():
    """API endpoint to get available tables"""
    
    try:
        engine = ReportEngine()
        tables = engine.get_available_tables()
        return jsonify({
            'success': True,
            'tables': tables
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/tables/<table_name>/columns')
@login_required
def api_table_columns(table_name):
    """API endpoint to get table columns"""
    
    try:
        engine = ReportEngine()
        columns = engine.get_table_columns(table_name)
        return jsonify(columns)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/tables/<table_name>/info')
@login_required
def api_table_info(table_name):
    """API endpoint to get table information"""
    
    try:
        engine = ReportEngine()
        info = engine.get_table_info(table_name)
        return jsonify({
            'success': True,
            **info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/reports/<int:id>/execute', methods=['POST'])
@login_required
def api_execute_report(id):
    """API endpoint to execute a report with configuration"""
    
    print(f"API Execute Report called for ID: {id}")
    print(f"Request data: {request.get_json()}")
    
    try:
        report = Report.query.get_or_404(id)
        print(f"Report found: {report.name}")
        
        # Check permissions
        if report.created_by != current_user.id:
            print("Permission denied - user not owner")
            return jsonify({
                'success': False,
                'error': 'Permission denied'
            }), 403

        try:
            # Get configuration from request
            config = request.get_json() or {}
            print(f"Configuration received: {config}")
            
            # Update report configuration
            if config.get('data_source'):
                report.data_source = config['data_source']
                print(f"Updated data_source to: {report.data_source}")
            if config.get('columns'):
                report.columns = json.dumps(config['columns'])
                print(f"Updated columns to: {report.columns}")
            if config.get('filters'):
                report.filters = json.dumps(config['filters'])
                print(f"Updated filters to: {report.filters}")
            if config.get('visualizations'):
                report.visualizations = json.dumps(config['visualizations'])
                print(f"Updated visualizations to: {report.visualizations}")
            
            db.session.commit()
            print("Database committed successfully")
            
            # Execute report
            print("Creating ReportEngine...")
            engine = ReportEngine()
            print("Executing report...")
            result = engine.execute_report(report)
            print(f"Report execution result: {result}")
            
            # Create execution record
            execution = ReportExecution(
                report_id=report.id,
                executed_by=current_user.id,
                status='completed',
                row_count=result.get('row_count', 0),
                execution_time=result.get('execution_time', 0)
            )
            db.session.add(execution)
            
            # Update report
            report.last_execution = datetime.utcnow()
            report.execution_count = (report.execution_count or 0) + 1
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': result.get('data', []),
                'columns': result.get('columns', []),
                'row_count': result.get('row_count', 0),
                'execution_time': result.get('execution_time', 0)
            })
            
        except Exception as e:
            print(f"ERROR during report execution: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Create failed execution record
            try:
                execution = ReportExecution(
                    report_id=report.id,
                    executed_by=current_user.id,
                    status='failed',
                    error_message=str(e)
                )
                db.session.add(execution)
                db.session.commit()
            except:
                pass  # Ignore errors when logging failed execution
            
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    except Exception as e:
        print(f"OUTER ERROR in api_execute_report: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@bp.route('/api/reports/<int:id>/save', methods=['POST'])
@login_required
def api_save_report(id):
    """API endpoint to save report configuration"""
    
    report = Report.query.get_or_404(id)
    
    # Check permissions
    if report.created_by != current_user.id:
        return jsonify({
            'success': False,
            'error': 'Permission denied'
        }), 403
    
    try:
        # Get configuration from request
        config = request.get_json() or {}
        
        # Update report configuration
        if config.get('data_source'):
            report.data_source = config['data_source']
        if config.get('columns'):
            report.columns = config['columns']
        if config.get('filters'):
            report.filters = config['filters']
        if config.get('visualizations'):
            report.visualizations = config['visualizations']
        
        report.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Report saved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/reports/<int:id>/export/<format>')
@login_required
def export_report(id, format):
    """Export report in specified format"""
    
    report = Report.query.get_or_404(id)
    
    # Check permissions
    if report.created_by != current_user.id:
        return redirect(url_for('reporting.reports_list'))
    
    try:
        engine = ReportEngine()
        
        if format == 'csv':
            output = engine.export_to_csv(report)
            response = make_response(output)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename="{report.name}.csv"'
            return response
            
        elif format == 'excel':
            output = engine.export_to_excel(report)
            response = make_response(output)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename="{report.name}.xlsx"'
            return response
            
        elif format == 'pdf':
            output = engine.export_to_pdf(report)
            response = make_response(output)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="{report.name}.pdf"'
            return response
            
        else:
            flash('Invalid export format', 'error')
            return redirect(url_for('reporting.report_builder', id=id))
            
    except Exception as e:
        flash(f'Export failed: {str(e)}', 'error')
        return redirect(url_for('reporting.report_builder', id=id))


@bp.route('/reports/<int:id>/share', methods=['GET', 'POST'])
@login_required
def share_report(id):
    """Share a report"""
    
    report = Report.query.get_or_404(id)
    
    # Check permissions
    if report.created_by != current_user.id:
        flash('You do not have permission to share this report.', 'error')
        return redirect(url_for('reporting.reports_list'))
    
    form = ShareReportForm()
    
    if form.validate_on_submit():
        # Create share record
        expires_at = None
        if form.expires_in.data:
            expires_at = datetime.utcnow() + timedelta(days=int(form.expires_in.data))
        
        share = ReportShare(
            report_id=report.id,
            shared_by=current_user.id,
            share_type=form.share_type.data,
            permissions=form.permissions.data,
            recipients=form.recipients.data,
            message=form.message.data,
            expires_at=expires_at
        )
        
        db.session.add(share)
        db.session.commit()
        
        flash('Report shared successfully!', 'success')
        return redirect(url_for('reporting.report_builder', id=id))
    
    return render_template('reporting/share_report.html', form=form, report=report)


@bp.route('/reports/<int:id>/schedule', methods=['GET', 'POST'])
@login_required
def schedule_report(id):
    """Schedule a report"""
    
    report = Report.query.get_or_404(id)
    
    # Check permissions
    if report.created_by != current_user.id:
        flash('You do not have permission to schedule this report.', 'error')
        return redirect(url_for('reporting.reports_list'))
    
    form = ScheduleReportForm()
    
    if form.validate_on_submit():
        # Calculate next run time
        next_run = datetime.utcnow().replace(
            hour=int(form.hour.data),
            minute=0,
            second=0,
            microsecond=0
        )
        
        # Adjust for frequency
        if form.frequency.data == 'daily':
            if next_run <= datetime.utcnow():
                next_run += timedelta(days=1)
        elif form.frequency.data == 'weekly':
            # Calculate next occurrence of the specified day
            pass  # Implementation depends on requirements
        
        # Create schedule
        schedule = ReportSchedule(
            report_id=report.id,
            frequency=form.frequency.data,
            day_of_week=form.day_of_week.data,
            day_of_month=form.day_of_month.data,
            hour=int(form.hour.data),
            export_format=form.format.data,
            email_recipients=form.email_recipients.data,
            include_data=form.include_data.data,
            next_run=next_run
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        flash('Report scheduled successfully!', 'success')
        return redirect(url_for('reporting.report_builder', id=id))
    
    return render_template('reporting/schedule_report.html', form=form, report=report)


@bp.route('/reports/<int:id>/duplicate', methods=['POST'])
@login_required
def duplicate_report(id):
    """Duplicate a report"""
    
    original = Report.query.get_or_404(id)
    
    # Check permissions
    if original.created_by != current_user.id:
        return jsonify({
            'success': False,
            'error': 'Permission denied'
        }), 403
    
    try:
        # Create duplicate
        duplicate = Report(
            name=f"{original.name} (Copy)",
            description=original.description,
            category=original.category,
            data_source=original.data_source,
            columns=original.columns,
            filters=original.filters,
            visualizations=original.visualizations,
            tags=original.tags,
            template_type=original.template_type,
            created_by=current_user.id
        )
        
        db.session.add(duplicate)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'report_id': duplicate.id,
            'message': 'Report duplicated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/reports/<int:id>', methods=['DELETE'])
@login_required
def api_delete_report(id):
    """API endpoint to delete a report"""
    
    report = Report.query.get_or_404(id)
    
    # Check permissions
    if report.created_by != current_user.id:
        return jsonify({
            'success': False,
            'error': 'Permission denied'
        }), 403
    
    try:
        # Delete related records
        ReportExecution.query.filter_by(report_id=id).delete()
        ReportSchedule.query.filter_by(report_id=id).delete()
        ReportShare.query.filter_by(report_id=id).delete()
        
        # Delete report
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Report deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500