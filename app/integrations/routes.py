"""
Integration Routes
Web interface for managing third-party integrations
"""

from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timezone
import json
import traceback

from app.integrations import bp
from app.integrations.models import (IntegrationProvider, Integration, IntegrationMapping,
                                   IntegrationSyncLog, IntegrationWebhook)
from app.integrations.forms import (IntegrationProviderForm, IntegrationForm, ActiveDirectoryForm,
                                  JiraForm, IntegrationMappingForm, IntegrationWebhookForm,
                                  IntegrationTestForm, BulkSyncForm)
from app.integrations.services import IntegrationService, RESTIntegrationService
from app.integrations.services.active_directory import ActiveDirectoryService
from app.integrations.services.jira import JIRAService
from app import db
from app.models import User
from app.auth.decorators import admin_required


@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Integration management dashboard"""
    # Get integration statistics
    total_integrations = Integration.query.count()
    active_integrations = Integration.query.filter_by(is_enabled=True).count()
    
    # Get recent sync logs
    recent_logs = IntegrationSyncLog.query.order_by(
        IntegrationSyncLog.timestamp.desc()
    ).limit(10).all()
    
    # Get integrations by status
    integrations_by_status = {}
    all_integrations = Integration.query.all()
    for integration in all_integrations:
        status = integration.status
        if status not in integrations_by_status:
            integrations_by_status[status] = 0
        integrations_by_status[status] += 1
    
    return render_template('integrations/dashboard.html',
                         title='Integration Management',
                         total_integrations=total_integrations,
                         active_integrations=active_integrations,
                         recent_logs=recent_logs,
                         integrations_by_status=integrations_by_status)


@bp.route('/providers')
@login_required
@admin_required
def providers():
    """List integration providers"""
    providers = IntegrationProvider.query.order_by(IntegrationProvider.name).all()
    return render_template('integrations/providers.html',
                         title='Integration Providers',
                         providers=providers)


@bp.route('/providers/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_provider():
    """Create new integration provider"""
    form = IntegrationProviderForm()
    
    if form.validate_on_submit():
        try:
            provider = IntegrationProvider(
                name=form.name.data,
                display_name=form.display_name.data,
                provider_type=form.provider_type.data,
                description=form.description.data,
                configuration_schema=form.configuration_schema.data,
                is_active=form.is_active.data,
                is_built_in=form.is_built_in.data
            )
            
            db.session.add(provider)
            db.session.commit()
            
            flash(f'Integration provider "{provider.display_name}" created successfully.', 'success')
            return redirect(url_for('integrations.providers'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating provider: {str(e)}', 'error')
    
    return render_template('integrations/create_provider.html',
                         title='Create Integration Provider',
                         form=form)


@bp.route('/providers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_provider(id):
    """Edit integration provider"""
    provider = IntegrationProvider.query.get_or_404(id)
    form = IntegrationProviderForm(obj=provider)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(provider)
            provider.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            flash(f'Integration provider "{provider.display_name}" updated successfully.', 'success')
            return redirect(url_for('integrations.providers'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating provider: {str(e)}', 'error')
    
    return render_template('integrations/edit_provider.html',
                         title='Edit Integration Provider',
                         form=form, provider=provider)


@bp.route('/list')
@login_required
@admin_required
def list_integrations():
    """List all integrations"""
    integrations_list = Integration.query.order_by(Integration.name).all()
    return render_template('integrations/list.html',
                         title='Integrations',
                         integrations=integrations_list)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_integration():
    """Create new integration"""
    provider_id = request.args.get('provider_id', type=int)
    provider = None
    
    if provider_id:
        provider = IntegrationProvider.query.get_or_404(provider_id)
        
        # Use specialized forms for built-in providers
        if provider.name == 'active_directory':
            return redirect(url_for('integrations.create_ad_integration'))
        elif provider.name == 'jira':
            return redirect(url_for('integrations.create_jira_integration'))
    
    form = IntegrationForm()
    form.provider_id.choices = [(p.id, p.display_name) 
                               for p in IntegrationProvider.query.filter_by(is_active=True).all()]
    
    if provider:
        form.provider_id.data = provider.id
    
    if form.validate_on_submit():
        try:
            # Prepare configuration
            config = {}
            if form.base_url.data:
                config['base_url'] = form.base_url.data
            if form.configuration.data:
                config.update(json.loads(form.configuration.data))
            
            # Prepare credentials
            credentials = {}
            if form.username.data:
                credentials['username'] = form.username.data
            if form.password.data:
                credentials['password'] = form.password.data
            if form.api_key.data:
                credentials['api_key'] = form.api_key.data
            if form.token.data:
                credentials['token'] = form.token.data
            
            integration = Integration(
                name=form.name.data,
                description=form.description.data,
                provider_id=form.provider_id.data,
                sync_frequency=form.sync_frequency.data,
                is_enabled=form.is_enabled.data,
                created_by_id=current_user.id
            )
            
            integration.config_dict = config
            integration.credentials_dict = credentials
            
            db.session.add(integration)
            db.session.commit()
            
            flash(f'Integration "{integration.name}" created successfully.', 'success')
            return redirect(url_for('integrations.view_integration', id=integration.id))
            
        except json.JSONDecodeError:
            flash('Invalid JSON in configuration field.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating integration: {str(e)}', 'error')
    
    return render_template('integrations/create_integration.html',
                         title='Create Integration',
                         form=form, provider=provider)


@bp.route('/create/active-directory', methods=['GET', 'POST'])
@login_required
@admin_required
def create_ad_integration():
    """Create Active Directory integration"""
    form = ActiveDirectoryForm()
    
    if form.validate_on_submit():
        try:
            # Get or create AD provider
            provider = IntegrationProvider.query.filter_by(name='active_directory').first()
            if not provider:
                provider = IntegrationProvider(
                    name='active_directory',
                    display_name='Active Directory',
                    provider_type='LDAP',
                    description='Microsoft Active Directory / LDAP integration',
                    is_built_in=True,
                    is_active=True
                )
                db.session.add(provider)
                db.session.flush()
            
            # Prepare configuration
            config = {
                'domain_controller': form.domain_controller.data,
                'domain_name': form.domain_name.data,
                'base_dn': form.base_dn.data,
                'user_base_dn': form.user_base_dn.data or form.base_dn.data,
                'user_filter': form.user_filter.data,
                'group_base_dn': form.group_base_dn.data or form.base_dn.data,
                'group_filter': form.group_filter.data,
                'sync_users': form.sync_users.data,
                'sync_groups': form.sync_groups.data,
                'auto_create_users': form.auto_create_users.data,
                'auto_disable_users': form.auto_disable_users.data
            }
            
            # Prepare credentials
            credentials = {
                'bind_username': form.bind_username.data,
                'bind_password': form.bind_password.data
            }
            
            integration = Integration(
                name=form.name.data,
                description=form.description.data,
                provider_id=provider.id,
                sync_frequency=form.sync_frequency.data,
                is_enabled=form.is_enabled.data,
                created_by_id=current_user.id
            )
            
            integration.config_dict = config
            integration.credentials_dict = credentials
            
            db.session.add(integration)
            db.session.commit()
            
            flash(f'Active Directory integration "{integration.name}" created successfully.', 'success')
            return redirect(url_for('integrations.view_integration', id=integration.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating AD integration: {str(e)}', 'error')
    
    return render_template('integrations/create_ad.html',
                         title='Create Active Directory Integration',
                         form=form)


@bp.route('/create/jira', methods=['GET', 'POST'])
@login_required
@admin_required
def create_jira_integration():
    """Create JIRA integration"""
    form = JiraForm()
    
    if form.validate_on_submit():
        try:
            # Get or create JIRA provider
            provider = IntegrationProvider.query.filter_by(name='jira').first()
            if not provider:
                provider = IntegrationProvider(
                    name='jira',
                    display_name='Atlassian JIRA',
                    provider_type='REST',
                    description='Atlassian JIRA issue tracking integration',
                    is_built_in=True,
                    is_active=True
                )
                db.session.add(provider)
                db.session.flush()
            
            # Prepare configuration
            config = {
                'jira_url': form.jira_url.data.rstrip('/'),
                'default_project': form.default_project.data,
                'auto_create_issues': form.auto_create_issues.data,
                'sync_comments': form.sync_comments.data,
                'sync_status_changes': form.sync_status_changes.data
            }
            
            # Parse JSON fields
            try:
                config['issue_type_mapping'] = form.issue_type_mapping.data
                config['priority_mapping'] = form.priority_mapping.data
            except json.JSONDecodeError:
                flash('Invalid JSON in mapping fields.', 'error')
                return render_template('integrations/create_jira.html',
                                     title='Create JIRA Integration', form=form)
            
            # Prepare credentials
            credentials = {
                'username': form.username.data,
                'api_token': form.api_token.data
            }
            
            integration = Integration(
                name=form.name.data,
                description=form.description.data,
                provider_id=provider.id,
                sync_frequency=form.sync_frequency.data,
                is_enabled=form.is_enabled.data,
                created_by_id=current_user.id
            )
            
            integration.config_dict = config
            integration.credentials_dict = credentials
            
            db.session.add(integration)
            db.session.commit()
            
            flash(f'JIRA integration "{integration.name}" created successfully.', 'success')
            return redirect(url_for('integrations.view_integration', id=integration.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating JIRA integration: {str(e)}', 'error')
    
    return render_template('integrations/create_jira.html',
                         title='Create JIRA Integration',
                         form=form)


@bp.route('/<int:id>')
@login_required
@admin_required
def view_integration(id):
    """View integration details"""
    integration = Integration.query.get_or_404(id)
    
    # Get recent sync logs
    recent_logs = IntegrationSyncLog.query.filter_by(
        integration_id=id
    ).order_by(IntegrationSyncLog.timestamp.desc()).limit(20).all()
    
    # Get mappings
    mappings = IntegrationMapping.query.filter_by(integration_id=id).all()
    
    # Get webhooks
    webhooks = IntegrationWebhook.query.filter_by(integration_id=id).all()
    
    return render_template('integrations/view_integration.html',
                         title=f'Integration: {integration.name}',
                         integration=integration,
                         recent_logs=recent_logs,
                         mappings=mappings,
                         webhooks=webhooks)


@bp.route('/<int:id>/test', methods=['POST'])
@login_required
@admin_required
def test_integration(id):
    """Test integration connection"""
    integration = Integration.query.get_or_404(id)
    test_type = request.json.get('test_type', 'connection')
    
    try:
        # Get the appropriate service
        service = _get_integration_service(integration)
        
        if test_type == 'connection':
            success, message = service.test_connection()
        elif test_type == 'auth':
            success, message = service.authenticate()
        else:
            success, message = False, f"Unknown test type: {test_type}"
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Test error: {str(e)}"
        }), 500


@bp.route('/<int:id>/sync', methods=['POST'])
@login_required
@admin_required
def sync_integration(id):
    """Trigger manual sync for integration"""
    integration = Integration.query.get_or_404(id)
    entity_type = request.json.get('entity_type')
    force_update = request.json.get('force_update', False)
    
    try:
        # Get the appropriate service
        service = _get_integration_service(integration)
        
        # Trigger sync
        results = service.sync_data(entity_type, force_update)
        
        return jsonify(results)
        
    except Exception as e:
        error_msg = f"Sync error: {str(e)}"
        current_app.logger.error(f"Integration sync error for {integration.name}: {error_msg}")
        current_app.logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'message': error_msg,
            'records_processed': 0,
            'records_success': 0,
            'records_error': 1,
            'errors': [error_msg]
        }), 500


@bp.route('/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_integration(id):
    """Enable/disable integration"""
    integration = Integration.query.get_or_404(id)
    
    try:
        integration.is_enabled = not integration.is_enabled
        integration.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        status = "enabled" if integration.is_enabled else "disabled"
        flash(f'Integration "{integration.name}" {status} successfully.', 'success')
        
        return jsonify({
            'success': True,
            'is_enabled': integration.is_enabled,
            'message': f'Integration {status} successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f"Error toggling integration: {str(e)}"
        }), 500


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_integration(id):
    """Delete integration"""
    integration = Integration.query.get_or_404(id)
    
    try:
        integration_name = integration.name
        db.session.delete(integration)
        db.session.commit()
        
        flash(f'Integration "{integration_name}" deleted successfully.', 'success')
        return redirect(url_for('integrations.list_integrations'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting integration: {str(e)}', 'error')
        return redirect(url_for('integrations.view_integration', id=id))


@bp.route('/logs')
@login_required
@admin_required
def view_logs():
    """View integration sync logs"""
    page = request.args.get('page', 1, type=int)
    integration_id = request.args.get('integration_id', type=int)
    status = request.args.get('status')
    
    query = IntegrationSyncLog.query
    
    if integration_id:
        query = query.filter_by(integration_id=integration_id)
    if status:
        query = query.filter_by(status=status)
    
    logs = query.order_by(IntegrationSyncLog.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    # Get integrations for filter dropdown
    integrations_list = Integration.query.order_by(Integration.name).all()
    
    return render_template('integrations/logs.html',
                         title='Integration Logs',
                         logs=logs,
                         integrations=integrations_list,
                         current_integration_id=integration_id,
                         current_status=status)


def _get_integration_service(integration: Integration):
    """Get the appropriate service class for an integration"""
    provider_name = integration.provider.name
    
    if provider_name == 'active_directory':
        return ActiveDirectoryService(integration)
    elif provider_name == 'jira':
        return JIRAService(integration)
    elif integration.provider.provider_type == 'REST':
        return RESTIntegrationService(integration)
    else:
        # Default to base service
        return IntegrationService(integration)


# Initialize built-in providers
def init_builtin_providers():
    """Initialize built-in integration providers"""
    builtin_providers = [
        {
            'name': 'active_directory',
            'display_name': 'Active Directory',
            'provider_type': 'LDAP',
            'description': 'Microsoft Active Directory / LDAP integration for user and group synchronization',
            'is_built_in': True,
            'configuration_schema': json.dumps({
                'domain_controller': {'type': 'string', 'required': True},
                'domain_name': {'type': 'string', 'required': True},
                'base_dn': {'type': 'string', 'required': True},
                'bind_username': {'type': 'string', 'required': True},
                'bind_password': {'type': 'string', 'required': True, 'secure': True}
            })
        },
        {
            'name': 'jira',
            'display_name': 'Atlassian JIRA',
            'provider_type': 'REST',
            'description': 'Atlassian JIRA issue tracking integration',
            'is_built_in': True,
            'configuration_schema': json.dumps({
                'jira_url': {'type': 'string', 'required': True},
                'username': {'type': 'string', 'required': True},
                'api_token': {'type': 'string', 'required': True, 'secure': True},
                'default_project': {'type': 'string', 'required': False}
            })
        },
        {
            'name': 'generic_rest',
            'display_name': 'Generic REST API',
            'provider_type': 'REST',
            'description': 'Generic REST API integration',
            'is_built_in': True,
            'configuration_schema': json.dumps({
                'base_url': {'type': 'string', 'required': True},
                'auth_type': {'type': 'select', 'options': ['none', 'basic', 'bearer', 'api_key']},
                'api_key_header': {'type': 'string', 'default': 'X-API-Key'}
            })
        },
        {
            'name': 'soap_service',
            'display_name': 'SOAP Web Service',
            'provider_type': 'SOAP',
            'description': 'SOAP Web Service integration',
            'is_built_in': True,
            'configuration_schema': json.dumps({
                'wsdl_url': {'type': 'string', 'required': True},
                'service_url': {'type': 'string', 'required': True},
                'username': {'type': 'string', 'required': False},
                'password': {'type': 'string', 'required': False, 'secure': True}
            })
        }
    ]
    
    for provider_data in builtin_providers:
        provider = IntegrationProvider.query.filter_by(name=provider_data['name']).first()
        if not provider:
            provider = IntegrationProvider(**provider_data)
            db.session.add(provider)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error initializing built-in providers: {str(e)}")
