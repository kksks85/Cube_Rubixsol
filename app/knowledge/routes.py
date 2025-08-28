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

@knowledge.route('/article/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    """Edit knowledge article"""
    article = KnowledgeArticle.query.get_or_404(id)
    
    # Check if user has permission to edit
    if not article.can_user_edit(current_user):
        abort(403)
    
    form = KnowledgeArticleForm(obj=article)
    
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
        # Update article
        article.title = form.title.data
        article.summary = form.summary.data
        article.description = form.description.data
        article.solution = form.solution.data
        article.article_type = form.article_type.data
        article.category_id = form.category_id.data if form.category_id.data else None
        article.priority = form.priority.data
        article.visibility = form.visibility.data
        article.keywords = form.keywords.data
        article.updated_at = datetime.utcnow()
        
        # Handle tags
        # Clear existing tags
        article.tags.clear()
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag = KnowledgeTag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = KnowledgeTag(name=tag_name)
                    db.session.add(tag)
                article.tags.append(tag)
        
        # Create workflow entry if status changed
        if hasattr(form, 'status') and form.status.data != article.status:
            create_workflow_entry(article, article.status, form.status.data, form.workflow_comments.data)
            article.status = form.status.data
        
        db.session.commit()
        
        flash(f'Knowledge article "{article.title}" has been updated successfully.', 'success')
        return redirect(url_for('knowledge.view_article', id=article.id))
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        # Set tags field
        form.tags.data = ', '.join([tag.name for tag in article.tags])
    
    return render_template('knowledge/edit.html', form=form, article=article)

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

@knowledge.route('/admin/pending-review')
@login_required
def pending_review():
    """List articles pending review"""
    if not (current_user.has_role('admin') or current_user.has_role('knowledge_admin') or
            current_user.has_role('knowledge_reviewer')):
        abort(403)
    
    query = KnowledgeArticle.query.filter_by(status=KnowledgeStatus.REVIEW)
    
    # Regular reviewers only see articles assigned to them
    if not (current_user.has_role('admin') or current_user.has_role('knowledge_admin')):
        query = query.filter_by(reviewer_id=current_user.id)
    
    articles = query.order_by(KnowledgeArticle.created_at).all()
    
    return render_template('knowledge/pending_review.html', articles=articles)

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

@knowledge.route('/admin/analytics')
@login_required
def analytics():
    """Knowledge base analytics dashboard"""
    if not (current_user.has_role('admin') or current_user.has_role('knowledge_admin')):
        abort(403)
    
    form = KnowledgeAnalyticsForm()
    
    # Default to last 30 days
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    if request.args.get('date_range'):
        days = int(request.args.get('date_range', 30))
        start_date = end_date - timedelta(days=days)
    
    # Article statistics
    total_articles = KnowledgeArticle.query.count()
    published_articles = KnowledgeArticle.query.filter_by(status=KnowledgeStatus.PUBLISHED).count()
    draft_articles = KnowledgeArticle.query.filter_by(status=KnowledgeStatus.DRAFT).count()
    pending_review = KnowledgeArticle.query.filter_by(status=KnowledgeStatus.REVIEW).count()
    
    # View statistics
    total_views = db.session.query(func.sum(KnowledgeArticle.view_count)).scalar() or 0
    recent_views = KnowledgeView.query.filter(
        KnowledgeView.viewed_at >= start_date
    ).count()
    
    # Top articles by views
    top_articles = KnowledgeArticle.query.filter_by(
        status=KnowledgeStatus.PUBLISHED
    ).order_by(desc(KnowledgeArticle.view_count)).limit(10).all()
    
    # Top categories
    category_stats = db.session.query(
        KnowledgeCategory.name,
        func.count(KnowledgeArticle.id).label('article_count'),
        func.sum(KnowledgeArticle.view_count).label('total_views')
    ).join(
        KnowledgeArticle, KnowledgeCategory.id == KnowledgeArticle.category_id
    ).filter(
        KnowledgeArticle.status == KnowledgeStatus.PUBLISHED
    ).group_by(
        KnowledgeCategory.id, KnowledgeCategory.name
    ).order_by(desc('total_views')).limit(10).all()
    
    # Author statistics
    author_stats = db.session.query(
        User.username,
        func.count(KnowledgeArticle.id).label('article_count'),
        func.avg(KnowledgeArticle.average_rating).label('avg_rating')
    ).join(
        KnowledgeArticle, User.id == KnowledgeArticle.author_id
    ).filter(
        KnowledgeArticle.status == KnowledgeStatus.PUBLISHED
    ).group_by(
        User.id, User.username
    ).order_by(desc('article_count')).limit(10).all()
    
    # Recent activity
    recent_articles = KnowledgeArticle.query.filter(
        KnowledgeArticle.created_at >= start_date
    ).order_by(desc(KnowledgeArticle.created_at)).limit(10).all()
    
    return render_template('knowledge/analytics.html',
                         form=form,
                         total_articles=total_articles,
                         published_articles=published_articles,
                         draft_articles=draft_articles,
                         pending_review=pending_review,
                         total_views=total_views,
                         recent_views=recent_views,
                         top_articles=top_articles,
                         category_stats=category_stats,
                         author_stats=author_stats,
                         recent_articles=recent_articles,
                         start_date=start_date,
                         end_date=end_date)

@knowledge.route('/admin/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create new category (admin only)"""
    if not (current_user.has_role('admin') or current_user.has_role('knowledge_admin')):
        abort(403)
    
    try:
        form = KnowledgeCategoryForm()
        
        # Populate choices safely
        try:
            categories = KnowledgeCategory.query.filter_by(is_active=True).all()
            choices = [('', 'No Parent')]
            for c in categories:
                try:
                    choices.append((c.id, c.full_path))
                except Exception as e:
                    print(f"Error with category {c.id}: {e}")
                    choices.append((c.id, c.name))  # Fallback to just name
            form.parent_id.choices = choices
        except Exception as e:
            print(f"Error populating choices: {e}")
            form.parent_id.choices = [('', 'No Parent')]
        
        if request.method == 'POST':
            print(f"Form data received: {request.form}")
            if form.validate_on_submit():
                try:
                    category = KnowledgeCategory(
                        name=form.name.data,
                        description=form.description.data,
                        parent_id=form.parent_id.data,
                        icon=form.icon.data or 'fas fa-folder',
                        color=form.color.data or '#007bff',
                        sort_order=form.sort_order.data or 0,
                        is_active=form.is_active.data
                    )
                    
                    db.session.add(category)
                    db.session.commit()
                    
                    flash(f'Category "{category.name}" created successfully.', 'success')
                    return redirect(url_for('knowledge.list_categories'))
                except Exception as e:
                    print(f"Error saving category: {e}")
                    db.session.rollback()
                    flash(f'Error creating category: {str(e)}', 'error')
            else:
                print(f"Form validation errors: {form.errors}")
        
        return render_template('knowledge/create_category.html', form=form)
        
    except Exception as e:
        # Log the error and show a proper error message
        print(f"Error in create_category: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading category form: {str(e)}', 'error')
        # Return a minimal form
        try:
            minimal_form = KnowledgeCategoryForm()
            minimal_form.parent_id.choices = [('', 'No Parent')]
            return render_template('knowledge/create_category.html', form=minimal_form)
        except:
            abort(500)

# Error Handlers
@knowledge.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

# Additional Routes
@knowledge.route('/article/<int:id>/rate', methods=['POST'])
@login_required
def rate_article(id):
    """Rate article"""
    article = KnowledgeArticle.query.get_or_404(id)
    
    if not article.can_user_view(current_user):
        abort(403)
    
    form = KnowledgeRatingForm()
    
    if form.validate_on_submit():
        # Check if user already rated this article
        existing_rating = KnowledgeRating.query.filter_by(
            article_id=id, user_id=current_user.id
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = form.rating.data
            existing_rating.is_helpful = form.is_helpful.data
            existing_rating.feedback = form.feedback.data
        else:
            # Create new rating
            rating = KnowledgeRating(
                article_id=id,
                user_id=current_user.id,
                rating=form.rating.data,
                is_helpful=form.is_helpful.data,
                feedback=form.feedback.data
            )
            db.session.add(rating)
        
        # Update article helpfulness counters
        if form.is_helpful.data:
            article.helpful_count += 1
        else:
            article.not_helpful_count += 1
        
        # Recalculate average rating
        ratings = KnowledgeRating.query.filter_by(article_id=id).all()
        if ratings:
            article.average_rating = sum(r.rating for r in ratings) / len(ratings)
        
        db.session.commit()
        
        flash('Thank you for rating this article!', 'success')
    
    return redirect(url_for('knowledge.view_article', id=id))


@knowledge.route('/article/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    """Add comment to knowledge article"""
    article = KnowledgeArticle.query.get_or_404(id)
    
    # Check if user can view the article (and thus comment)
    if not article.can_user_view(current_user):
        abort(403)
    
    form = KnowledgeCommentForm()
    if form.validate_on_submit():
        comment = KnowledgeComment(
            article_id=id,
            user_id=current_user.id,
            content=form.content.data,
            is_internal=form.is_internal.data if hasattr(form, 'is_internal') else False
        )
        
        db.session.add(comment)
        db.session.commit()
        
        flash('Comment added successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('knowledge.view_article', id=id))


@knowledge.route('/subscribe/<subscription_type>/<int:subscription_id>', methods=['POST'])
@login_required
def subscribe(subscription_type, subscription_id):
    """Subscribe to knowledge article or category updates"""
    
    # Validate subscription type
    if subscription_type not in ['article', 'category']:
        flash('Invalid subscription type.', 'error')
        return redirect(request.referrer or url_for('knowledge.index'))
    
    # Check if subscription already exists
    existing_subscription = KnowledgeSubscription.query.filter_by(
        user_id=current_user.id,
        subscription_type=subscription_type,
        subscription_id=subscription_id
    ).first()
    
    if existing_subscription:
        flash('You are already subscribed to this item.', 'info')
    else:
        # Validate that the target exists
        if subscription_type == 'article':
            target = KnowledgeArticle.query.get(subscription_id)
            if not target or not target.can_user_view(current_user):
                flash('Article not found or access denied.', 'error')
                return redirect(request.referrer or url_for('knowledge.index'))
        elif subscription_type == 'category':
            target = KnowledgeCategory.query.get(subscription_id)
            if not target:
                flash('Category not found.', 'error')
                return redirect(request.referrer or url_for('knowledge.index'))
        
        # Create subscription
        subscription = KnowledgeSubscription(
            user_id=current_user.id,
            subscription_type=subscription_type,
            subscription_id=subscription_id
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        flash('Successfully subscribed! You will receive notifications for updates.', 'success')
    
    return redirect(request.referrer or url_for('knowledge.index'))


@knowledge.route('/article/<int:id>/update-status', methods=['POST'])
@login_required
def update_status(id):
    """Update article workflow status"""
    article = KnowledgeArticle.query.get_or_404(id)
    
    # Check permissions
    if not article.can_user_edit(current_user):
        flash('You do not have permission to update this article status.', 'error')
        return redirect(url_for('knowledge.view_article', id=id))
    
    new_status = request.form.get('status')
    comments = request.form.get('comments', '')
    
    # Validate status
    try:
        new_status_enum = KnowledgeStatus(new_status)
    except ValueError:
        flash('Invalid status.', 'error')
        return redirect(url_for('knowledge.view_article', id=id))
    
    # Check workflow permissions
    if not can_user_transition_status(current_user, article.status, new_status_enum):
        flash('You do not have permission to make this status transition.', 'error')
        return redirect(url_for('knowledge.view_article', id=id))
    
    # Update status
    old_status = article.status
    article.status = new_status_enum
    article.updated_at = datetime.now(timezone.utc)
    
    # Update specific fields based on status
    if new_status_enum == KnowledgeStatus.PUBLISHED:
        article.published_at = datetime.now(timezone.utc)
        article.published_by = current_user.id
    elif new_status_enum == KnowledgeStatus.APPROVED:
        article.approved_at = datetime.now(timezone.utc)
        article.approved_by = current_user.id
    elif new_status_enum == KnowledgeStatus.REVIEW:
        article.reviewed_at = datetime.now(timezone.utc)
        article.reviewed_by = current_user.id
    
    # Create workflow entry
    create_workflow_entry(article, old_status, new_status_enum, comments)
    
    db.session.commit()
    
    flash(f'Article status updated to {new_status_enum.value.title()}.', 'success')
    return redirect(url_for('knowledge.view_article', id=id))


def can_user_transition_status(user, from_status, to_status):
    """Check if user can transition from one status to another"""
    # Authors can move DRAFT to REVIEW
    if from_status == KnowledgeStatus.DRAFT and to_status == KnowledgeStatus.REVIEW:
        return True
    
    # Reviewers can approve/reject
    if user.has_role('knowledge_reviewer') or user.has_role('knowledge_admin') or user.has_role('admin'):
        if from_status == KnowledgeStatus.REVIEW and to_status in [KnowledgeStatus.APPROVED, KnowledgeStatus.DRAFT]:
            return True
        if from_status == KnowledgeStatus.APPROVED and to_status == KnowledgeStatus.PUBLISHED:
            return True
        if to_status == KnowledgeStatus.ARCHIVED:
            return True
    
    # Admins can do any transition
    if user.has_role('knowledge_admin') or user.has_role('admin'):
        return True
    
    return False


@knowledge.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404
