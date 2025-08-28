"""
Knowledge Management CLI Commands
Command-line interface for knowledge base administration
"""

import click
from flask.cli import with_appcontext
from datetime import datetime, timezone, timedelta
from app import db
from app.models import User, Role
from app.knowledge.models import (
    KnowledgeCategory, KnowledgeArticle, KnowledgeTag,
    KnowledgeStatus, KnowledgeType, VisibilityLevel
)

@click.group()
def knowledge():
    """Knowledge management commands."""
    pass

@knowledge.command()
@with_appcontext
def init_db():
    """Initialize knowledge base with default categories and settings."""
    click.echo('Initializing knowledge base...')
    
    # Create default categories
    default_categories = [
        {
            'name': 'Technical Solutions',
            'description': 'Technical troubleshooting and solutions',
            'icon': 'fa-wrench',
            'color': '#007bff',
            'children': [
                {'name': 'Network Issues', 'description': 'Network connectivity and configuration'},
                {'name': 'Software Problems', 'description': 'Application and software issues'},
                {'name': 'Hardware Issues', 'description': 'Hardware troubleshooting and repairs'},
                {'name': 'Security Incidents', 'description': 'Security-related problems and solutions'}
            ]
        },
        {
            'name': 'Procedures',
            'description': 'Standard operating procedures and workflows',
            'icon': 'fa-list-ol',
            'color': '#28a745',
            'children': [
                {'name': 'Installation Guides', 'description': 'Software and hardware installation procedures'},
                {'name': 'Configuration Steps', 'description': 'System and application configuration'},
                {'name': 'Maintenance Tasks', 'description': 'Regular maintenance procedures'},
                {'name': 'Emergency Procedures', 'description': 'Emergency response procedures'}
            ]
        },
        {
            'name': 'Frequently Asked Questions',
            'description': 'Common questions and answers',
            'icon': 'fa-question-circle',
            'color': '#ffc107',
            'children': [
                {'name': 'User Account Issues', 'description': 'Account access and permissions'},
                {'name': 'Password Problems', 'description': 'Password reset and security'},
                {'name': 'Service Requests', 'description': 'Common service request procedures'},
                {'name': 'General Usage', 'description': 'General system usage questions'}
            ]
        },
        {
            'name': 'Best Practices',
            'description': 'Recommended practices and guidelines',
            'icon': 'fa-star',
            'color': '#17a2b8',
            'children': [
                {'name': 'Security Guidelines', 'description': 'Security best practices'},
                {'name': 'Performance Optimization', 'description': 'System performance guidelines'},
                {'name': 'Code Standards', 'description': 'Development and coding standards'},
                {'name': 'Documentation Standards', 'description': 'Documentation best practices'}
            ]
        },
        {
            'name': 'Policies',
            'description': 'Organizational policies and compliance',
            'icon': 'fa-shield-alt',
            'color': '#dc3545',
            'children': [
                {'name': 'IT Policies', 'description': 'Information technology policies'},
                {'name': 'Security Policies', 'description': 'Security and compliance policies'},
                {'name': 'Access Control', 'description': 'User access and permission policies'},
                {'name': 'Data Management', 'description': 'Data handling and retention policies'}
            ]
        }
    ]
    
    created_count = 0
    for category_data in default_categories:
        # Check if category already exists
        existing = KnowledgeCategory.query.filter_by(name=category_data['name']).first()
        if not existing:
            parent_category = KnowledgeCategory(
                name=category_data['name'],
                description=category_data['description'],
                icon=category_data['icon'],
                color=category_data['color'],
                sort_order=created_count
            )
            db.session.add(parent_category)
            db.session.flush()  # Get the ID
            created_count += 1
            
            # Create child categories
            for i, child_data in enumerate(category_data.get('children', [])):
                existing_child = KnowledgeCategory.query.filter_by(
                    name=child_data['name'], parent_id=parent_category.id
                ).first()
                if not existing_child:
                    child_category = KnowledgeCategory(
                        name=child_data['name'],
                        description=child_data['description'],
                        parent_id=parent_category.id,
                        sort_order=i
                    )
                    db.session.add(child_category)
    
    # Create default tags
    default_tags = [
        'windows', 'linux', 'network', 'database', 'security', 'backup',
        'email', 'printer', 'software', 'hardware', 'password', 'access',
        'configuration', 'installation', 'troubleshooting', 'maintenance',
        'emergency', 'urgent', 'critical', 'routine'
    ]
    
    for tag_name in default_tags:
        existing_tag = KnowledgeTag.query.filter_by(name=tag_name).first()
        if not existing_tag:
            tag = KnowledgeTag(name=tag_name, color='#6c757d')
            db.session.add(tag)
    
    db.session.commit()
    click.echo(f'Created {created_count} categories and {len(default_tags)} tags.')

@knowledge.command()
@with_appcontext
def create_sample_articles():
    """Create sample knowledge articles for testing."""
    click.echo('Creating sample knowledge articles...')
    
    # Get first admin user as author
    admin_user = User.query.filter(User.roles.any(Role.name == 'admin')).first()
    if not admin_user:
        click.echo('No admin user found. Please create an admin user first.')
        return
    
    # Get categories
    network_category = KnowledgeCategory.query.filter_by(name='Network Issues').first()
    software_category = KnowledgeCategory.query.filter_by(name='Software Problems').first()
    faq_category = KnowledgeCategory.query.filter_by(name='User Account Issues').first()
    
    sample_articles = [
        {
            'title': 'How to Reset Network Connection on Windows',
            'summary': 'Step-by-step guide to reset network connection when experiencing connectivity issues on Windows systems.',
            'description': 'Users experiencing network connectivity issues on Windows may need to reset their network connection to resolve the problem.',
            'solution': '''1. Press Windows + R to open Run dialog
2. Type "cmd" and press Ctrl + Shift + Enter to run as administrator
3. Run the following commands in order:
   - ipconfig /release
   - ipconfig /flushdns
   - ipconfig /renew
   - netsh winsock reset
   - netsh int ip reset
4. Restart the computer
5. Test network connectivity''',
            'resolution_steps': 'Follow the command sequence above, ensuring each command completes successfully before proceeding to the next.',
            'prevention_steps': 'Regular system updates and avoiding untrusted network connections can prevent most network issues.',
            'article_type': KnowledgeType.TROUBLESHOOTING,
            'category': network_category,
            'keywords': 'network, windows, connectivity, reset, ipconfig, netsh',
            'tags': ['network', 'windows', 'troubleshooting']
        },
        {
            'title': 'Password Reset Procedure for User Accounts',
            'summary': 'Standard procedure for resetting user passwords in the system.',
            'description': 'This procedure outlines the steps required to reset a user password when they cannot access their account.',
            'solution': '''For Self-Service Reset:
1. Go to the login page
2. Click "Forgot Password?"
3. Enter your username or email
4. Check your email for reset instructions
5. Follow the link and create a new password

For Administrator Reset:
1. Access user management system
2. Search for the user account
3. Select "Reset Password"
4. Generate temporary password
5. Communicate new password securely to user
6. Ensure user changes password on first login''',
            'article_type': KnowledgeType.PROCEDURE,
            'category': faq_category,
            'keywords': 'password, reset, user, account, access',
            'tags': ['password', 'access', 'procedure']
        },
        {
            'title': 'Troubleshooting Application Crashes',
            'summary': 'Common solutions for applications that crash frequently or fail to start.',
            'description': 'Application crashes can be caused by various factors including memory issues, corrupted files, or compatibility problems.',
            'problem_statement': 'Application crashes unexpectedly or fails to launch properly.',
            'cause': 'Common causes include insufficient memory, corrupted application files, outdated drivers, or system compatibility issues.',
            'solution': '''1. Check system requirements
   - Verify minimum RAM and storage requirements
   - Ensure OS compatibility

2. Update the application
   - Check for latest version
   - Install all available updates

3. Check system resources
   - Close unnecessary applications
   - Check available RAM and disk space

4. Reinstall the application
   - Uninstall completely
   - Download fresh copy from official source
   - Install with administrator privileges

5. Check event logs
   - Open Event Viewer
   - Look for application errors
   - Note error codes for further research''',
            'workaround': 'If the application continues to crash, try running it in compatibility mode or with reduced graphics settings.',
            'article_type': KnowledgeType.TROUBLESHOOTING,
            'category': software_category,
            'keywords': 'application, crash, software, troubleshooting, memory',
            'tags': ['software', 'troubleshooting', 'crash']
        }
    ]
    
    created_count = 0
    for article_data in sample_articles:
        # Check if article already exists
        existing = KnowledgeArticle.query.filter_by(title=article_data['title']).first()
        if not existing:
            article = KnowledgeArticle(
                title=article_data['title'],
                summary=article_data['summary'],
                description=article_data['description'],
                problem_statement=article_data.get('problem_statement'),
                cause=article_data.get('cause'),
                solution=article_data['solution'],
                resolution_steps=article_data.get('resolution_steps'),
                workaround=article_data.get('workaround'),
                prevention_steps=article_data.get('prevention_steps'),
                article_type=article_data['article_type'],
                category_id=article_data['category'].id if article_data['category'] else None,
                keywords=article_data['keywords'],
                author_id=admin_user.id,
                status=KnowledgeStatus.PUBLISHED,
                visibility=VisibilityLevel.PUBLIC,
                priority='MEDIUM',
                published_at=datetime.now(timezone.utc)
            )
            db.session.add(article)
            db.session.flush()
            
            # Add tags
            for tag_name in article_data.get('tags', []):
                tag = KnowledgeTag.query.filter_by(name=tag_name).first()
                if tag:
                    article.tags.append(tag)
            
            created_count += 1
    
    db.session.commit()
    click.echo(f'Created {created_count} sample articles.')

@knowledge.command()
@with_appcontext
def update_metrics():
    """Update knowledge base metrics and statistics."""
    click.echo('Updating knowledge base metrics...')
    
    # Update tag usage counts
    tags = KnowledgeTag.query.all()
    for tag in tags:
        tag.usage_count = len(tag.articles)
    
    # Update article average ratings
    articles = KnowledgeArticle.query.all()
    for article in articles:
        ratings = [r.rating for r in article.ratings]
        if ratings:
            article.average_rating = sum(ratings) / len(ratings)
        else:
            article.average_rating = 0.0
    
    db.session.commit()
    click.echo('Metrics updated successfully.')

@knowledge.command()
@with_appcontext
def cleanup_expired():
    """Archive expired knowledge articles."""
    click.echo('Checking for expired articles...')
    
    now = datetime.now(timezone.utc)
    expired_articles = KnowledgeArticle.query.filter(
        KnowledgeArticle.expires_at < now,
        KnowledgeArticle.status != KnowledgeStatus.ARCHIVED
    ).all()
    
    archived_count = 0
    for article in expired_articles:
        article.status = KnowledgeStatus.EXPIRED
        archived_count += 1
        click.echo(f'Marked as expired: {article.title}')
    
    db.session.commit()
    click.echo(f'Marked {archived_count} articles as expired.')

@knowledge.command()
@click.option('--days', default=365, help='Articles older than this many days')
@with_appcontext
def find_stale(days):
    """Find articles that haven't been updated in specified days."""
    click.echo(f'Finding articles not updated in the last {days} days...')
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    stale_articles = KnowledgeArticle.query.filter(
        KnowledgeArticle.updated_at < cutoff_date,
        KnowledgeArticle.status == KnowledgeStatus.PUBLISHED
    ).all()
    
    click.echo(f'Found {len(stale_articles)} stale articles:')
    for article in stale_articles:
        days_old = (datetime.now(timezone.utc) - article.updated_at).days
        click.echo(f'  - {article.kb_id}: {article.title} (last updated {days_old} days ago)')

@knowledge.command()
@with_appcontext
def export_stats():
    """Export knowledge base statistics."""
    click.echo('Knowledge Base Statistics:')
    click.echo('=' * 50)
    
    # Article counts by status
    for status in KnowledgeStatus:
        count = KnowledgeArticle.query.filter_by(status=status).count()
        click.echo(f'{status.value}: {count}')
    
    click.echo()
    
    # Article counts by type
    click.echo('Articles by Type:')
    for article_type in KnowledgeType:
        count = KnowledgeArticle.query.filter_by(article_type=article_type).count()
        click.echo(f'{article_type.value}: {count}')
    
    click.echo()
    
    # Category statistics
    click.echo('Articles by Category:')
    categories = KnowledgeCategory.query.filter_by(is_active=True).all()
    for category in categories:
        count = category.article_count
        click.echo(f'{category.name}: {count}')
    
    click.echo()
    
    # Recent activity
    recent_articles = KnowledgeArticle.query.filter(
        KnowledgeArticle.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
    ).count()
    click.echo(f'Articles created in last 30 days: {recent_articles}')

def init_knowledge_cli(app):
    """Initialize CLI commands."""
    app.cli.add_command(knowledge)
