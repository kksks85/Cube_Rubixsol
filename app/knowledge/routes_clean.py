"""
Knowledge Management Routes
KEDB-compliant knowledge base with comprehensive functionality
"""

from flask import (Blueprint, render_template, request, flash, redirect, url_for, 
                  jsonify, abort, send_file, current_app)
from flask_login import login_required, current_user
from sqlalchemy import and_, or_, desc, asc, func, text
from datetime import datetime, timezone, timedelta
import os
import uuid
from werkzeug.utils import secure_filename

from app import db
from app.models import User, Role
from app.knowledge.models import (
    KnowledgeArticle, KnowledgeCategory, KnowledgeTag, KnowledgeComment,
    KnowledgeRating, KnowledgeView, KnowledgeAttachment, KnowledgeSubscription,
    KnowledgeWorkflow, KnowledgeStatus, KnowledgeType, VisibilityLevel,
    article_tags
)
from app.knowledge.forms import (
    KnowledgeArticleForm, KnowledgeCategoryForm, KnowledgeSearchForm,
    KnowledgeCommentForm, KnowledgeRatingForm, KnowledgeFilterForm,
    IncidentToKnowledgeForm, KnowledgeSubscriptionForm, KnowledgeImportForm,
    KnowledgeExportForm, KnowledgeAnalyticsForm
)

knowledge = Blueprint('knowledge', __name__, url_prefix='/knowledge')

# Utility Functions
def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_attachment(file, article_id):
    """Save uploaded file and create attachment record"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'knowledge')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Create attachment record
        attachment = KnowledgeAttachment(
            article_id=article_id,
            filename=unique_filename,
            original_filename=filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            mime_type=file.content_type,
            uploaded_by_id=current_user.id
        )
        db.session.add(attachment)
        return attachment
    return None

def record_article_view(article_id, user_id=None):
    """Record article view for analytics"""
    view = KnowledgeView(
        article_id=article_id,
        user_id=user_id,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string[:500]
    )
    db.session.add(view)
    
    # Increment view count
    article = KnowledgeArticle.query.get(article_id)
    if article:
        article.view_count += 1
        db.session.commit()

def create_workflow_entry(article, from_status, to_status, comments=None):
    """Create workflow tracking entry"""
    workflow = KnowledgeWorkflow(
        article_id=article.id,
        from_status=from_status,
        to_status=to_status,
        user_id=current_user.id,
        comments=comments
    )
    db.session.add(workflow)

def get_user_accessible_articles():
    """Get articles accessible to current user based on visibility"""
    base_query = KnowledgeArticle.query
    
    if current_user.has_role('admin') or current_user.has_role('knowledge_admin'):
        return base_query
    
    # Build visibility filter
    visibility_conditions = [
        KnowledgeArticle.visibility == VisibilityLevel.PUBLIC,
        KnowledgeArticle.author_id == current_user.id
    ]
    
    return base_query.filter(or_(*visibility_conditions))

# Main Routes
@knowledge.route('/')
@login_required
def index():
    """Knowledge base home page with dashboard"""
    # Get recent articles
    recent_articles = get_user_accessible_articles().filter(
        KnowledgeArticle.status == KnowledgeStatus.PUBLISHED
    ).order_by(desc(KnowledgeArticle.created_at)).limit(10).all()
    
    # Get popular articles
    popular_articles = get_user_accessible_articles().filter(
        KnowledgeArticle.status == KnowledgeStatus.PUBLISHED
    ).order_by(desc(KnowledgeArticle.view_count)).limit(10).all()
    
    # Get categories with article counts
    categories = KnowledgeCategory.query.filter_by(is_active=True, parent_id=None).all()
    
    # Get user statistics
    user_stats = {
        'total_articles': get_user_accessible_articles().filter(
            KnowledgeArticle.status == KnowledgeStatus.PUBLISHED
        ).count(),
        'my_articles': KnowledgeArticle.query.filter_by(author_id=current_user.id).count(),
        'pending_review': 0,
        'subscriptions': 0
    }
    
    return render_template('knowledge/index.html',
                         recent_articles=recent_articles,
                         popular_articles=popular_articles,
                         categories=categories,
                         user_stats=user_stats)

@knowledge.route('/search')
@login_required
def search():
    """Advanced search functionality"""
    form = KnowledgeSearchForm()
    
    # Populate form choices
    form.category_id.choices = [('', 'All Categories')] + [
        (c.id, c.name) for c in KnowledgeCategory.query.filter_by(is_active=True).all()
    ]
    form.author_id.choices = [('', 'All Authors')] + [
        (u.id, u.username) for u in User.query.all()
    ]
    
    articles = []
    total_count = 0
    pagination = None
    
    return render_template('knowledge/search.html',
                         form=form,
                         articles=articles,
                         total_count=total_count,
                         pagination=pagination)

@knowledge.route('/articles')
@login_required
def list_articles():
    """List all articles with filtering"""
    filter_form = KnowledgeFilterForm()
    
    # Build query
    query = get_user_accessible_articles()
    
    # Default sorting
    query = query.order_by(desc(KnowledgeArticle.updated_at))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    articles = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('knowledge/list.html',
                         articles=articles,
                         filter_form=filter_form)

@knowledge.route('/article/<int:id>')
@login_required
def view_article(id):
    """View individual article"""
    article = KnowledgeArticle.query.get_or_404(id)
    
    # Check access permissions
    if not article.can_user_view(current_user):
        abort(403)
    
    # Record view
    record_article_view(article.id, current_user.id)
    
    # Get comments
    comments = KnowledgeComment.query.filter_by(article_id=id).order_by(
        KnowledgeComment.created_at
    ).all()
    
    # Get user's rating
    user_rating = None
    
    # Forms
    comment_form = KnowledgeCommentForm()
    rating_form = KnowledgeRatingForm()
    
    # Related articles
    related_articles = []
    
    return render_template('knowledge/view.html',
                         article=article,
                         comments=comments,
                         user_rating=user_rating,
                         comment_form=comment_form,
                         rating_form=rating_form,
                         related_articles=related_articles)

@knowledge.route('/article/create', methods=['GET', 'POST'])
@login_required
def create_article():
    """Create new knowledge article"""
    form = KnowledgeArticleForm()
    
    # Populate form choices
    form.category_id.choices = [('', 'Select Category')] + [
        (c.id, c.name) for c in KnowledgeCategory.query.filter_by(is_active=True).all()
    ]
    form.reviewer_id.choices = [('', 'Select Reviewer')] + [
        (u.id, u.username) for u in User.query.all()
    ]
    form.visibility_roles.choices = [
        (r.id, r.name.replace('_', ' ').title()) for r in Role.query.all()
    ]
    form.visibility_users.choices = [
        (u.id, f"{u.username} ({u.email})") for u in User.query.all()
    ]
    
    if form.validate_on_submit():
        # Create article
        article = KnowledgeArticle(
            title=form.title.data,
            summary=form.summary.data,
            description=form.description.data,
            solution=form.solution.data,
            article_type=form.article_type.data,
            category_id=form.category_id.data if form.category_id.data else None,
            priority=form.priority.data,
            visibility=form.visibility.data,
            keywords=form.keywords.data,
            author_id=current_user.id,
            status=KnowledgeStatus.DRAFT
        )
        
        db.session.add(article)
        db.session.flush()  # Get the article ID
        
        # Handle tags
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag = KnowledgeTag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = KnowledgeTag(name=tag_name)
                    db.session.add(tag)
                article.tags.append(tag)
        
        # Create workflow entry
        create_workflow_entry(article, None, article.status, form.workflow_comments.data)
        
        db.session.commit()
        
        flash(f'Knowledge article "{article.title}" has been created successfully.', 'success')
        return redirect(url_for('knowledge.view_article', id=article.id))
    
    return render_template('knowledge/create.html', form=form)

@knowledge.route('/my-articles')
@login_required
def my_articles():
    """List current user's articles"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    articles = KnowledgeArticle.query.filter_by(author_id=current_user.id).order_by(
        desc(KnowledgeArticle.updated_at)
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('knowledge/my_articles.html', articles=articles)

@knowledge.route('/categories')
@login_required
def list_categories():
    """List all knowledge categories"""
    categories = KnowledgeCategory.query.filter_by(is_active=True).order_by(
        KnowledgeCategory.sort_order, KnowledgeCategory.name
    ).all()
    
    return render_template('knowledge/categories.html', categories=categories)

@knowledge.route('/category/<int:id>')
@login_required
def view_category(id):
    """View articles in category"""
    category = KnowledgeCategory.query.get_or_404(id)
    
    # Get articles in this category
    articles = get_user_accessible_articles().filter(
        and_(
            KnowledgeArticle.category_id == id,
            KnowledgeArticle.status == KnowledgeStatus.PUBLISHED
        )
    ).order_by(desc(KnowledgeArticle.updated_at)).all()
    
    # Get subcategories
    subcategories = KnowledgeCategory.query.filter_by(
        parent_id=id, is_active=True
    ).order_by(KnowledgeCategory.sort_order, KnowledgeCategory.name).all()
    
    return render_template('knowledge/category.html',
                         category=category,
                         articles=articles,
                         subcategories=subcategories)

# API Endpoints
@knowledge.route('/api/search-suggestions')
@login_required
def search_suggestions():
    """Get search suggestions for autocomplete"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    suggestions = []
    return jsonify(suggestions[:10])

# Error Handlers
@knowledge.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

@knowledge.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404
