# Knowledge Management Routes - Additional Functionality

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, abort, send_file, current_app
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

def register_additional_routes(knowledge):
    """Register additional routes with the knowledge blueprint"""

    @knowledge.route('/article/<int:id>/comment', methods=['POST'])
    @login_required
    def add_comment(id):
    """Add comment to article"""
    article = KnowledgeArticle.query.get_or_404(id)
    
    if not article.can_user_view(current_user):
        abort(403)
    
    form = KnowledgeCommentForm()
    
    if form.validate_on_submit():
        comment = KnowledgeComment(
            article_id=id,
            user_id=current_user.id,
            content=form.content.data,
            is_internal=form.is_internal.data
        )
        
        db.session.add(comment)
        db.session.commit()
        
        flash('Comment added successfully.', 'success')
    else:
        flash('Error adding comment. Please check your input.', 'error')
    
    return redirect(url_for('knowledge.view_article', id=id))

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

@knowledge.route('/article/<int:id>/delete', methods=['POST'])
@login_required
def delete_article(id):
    """Delete article (admin only)"""
    article = KnowledgeArticle.query.get_or_404(id)
    
    if not (current_user.has_role('admin') or current_user.has_role('knowledge_admin') or
            (current_user == article.author and article.status == KnowledgeStatus.DRAFT)):
        abort(403)
    
    # Delete associated files
    for attachment in article.attachments:
        try:
            if os.path.exists(attachment.file_path):
                os.remove(attachment.file_path)
        except:
            pass
    
    db.session.delete(article)
    db.session.commit()
    
    flash(f'Article "{article.title}" has been deleted.', 'success')
    return redirect(url_for('knowledge.list_articles'))

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

@knowledge.route('/admin/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create new category (admin only)"""
    if not (current_user.has_role('admin') or current_user.has_role('knowledge_admin')):
        abort(403)
    
    form = KnowledgeCategoryForm()
    form.parent_id.choices = [('', 'No Parent')] + [
        (c.id, c.full_path) for c in KnowledgeCategory.query.filter_by(is_active=True).all()
    ]
    
    if form.validate_on_submit():
        category = KnowledgeCategory(
            name=form.name.data,
            description=form.description.data,
            parent_id=form.parent_id.data if form.parent_id.data else None,
            icon=form.icon.data,
            color=form.color.data,
            sort_order=form.sort_order.data,
            is_active=form.is_active.data
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash(f'Category "{category.name}" created successfully.', 'success')
        return redirect(url_for('knowledge.list_categories'))
    
    return render_template('knowledge/create_category.html', form=form)

@knowledge.route('/admin/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    """Edit category (admin only)"""
    if not (current_user.has_role('admin') or current_user.has_role('knowledge_admin')):
        abort(403)
    
    category = KnowledgeCategory.query.get_or_404(id)
    form = KnowledgeCategoryForm(obj=category)
    
    # Exclude self and descendants from parent choices
    excluded_ids = [id]
    def get_descendants(cat_id):
        descendants = KnowledgeCategory.query.filter_by(parent_id=cat_id).all()
        for desc in descendants:
            excluded_ids.append(desc.id)
            get_descendants(desc.id)
    
    get_descendants(id)
    
    form.parent_id.choices = [('', 'No Parent')] + [
        (c.id, c.full_path) for c in KnowledgeCategory.query.filter_by(is_active=True).all()
        if c.id not in excluded_ids
    ]
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.parent_id = form.parent_id.data if form.parent_id.data else None
        category.icon = form.icon.data
        category.color = form.color.data
        category.sort_order = form.sort_order.data
        category.is_active = form.is_active.data
        
        db.session.commit()
        
        flash(f'Category "{category.name}" updated successfully.', 'success')
        return redirect(url_for('knowledge.list_categories'))
    
    return render_template('knowledge/edit_category.html', form=form, category=category)

@knowledge.route('/my-articles')
@login_required
def my_articles():
    """List current user's articles"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('KNOWLEDGE_ARTICLES_PER_PAGE', 20)
    
    articles = KnowledgeArticle.query.filter_by(author_id=current_user.id).order_by(
        desc(KnowledgeArticle.updated_at)
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('knowledge/my_articles.html', articles=articles)

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

@knowledge.route('/incident/<int:incident_id>/convert-to-knowledge', methods=['GET', 'POST'])
@login_required
def convert_incident_to_knowledge(incident_id):
    """Convert incident to knowledge article"""
    # Import here to avoid circular imports
    from app.models import ServiceIncident
    
    incident = ServiceIncident.query.get_or_404(incident_id)
    
    form = IncidentToKnowledgeForm()
    form.category_id.choices = [
        (c.id, c.full_path) for c in KnowledgeCategory.query.filter_by(is_active=True).all()
    ]
    
    if not form.is_submitted():
        # Pre-populate form with incident data
        form.incident_id.data = incident_id
        form.title.data = f"Solution: {incident.title}"
    
    if form.validate_on_submit():
        # Create knowledge article from incident
        article = KnowledgeArticle(
            title=form.title.data,
            summary=incident.description[:500] if incident.description else incident.title,
            description=incident.description if form.include_incident_details.data else "",
            solution=incident.resolution if form.include_resolution.data else "",
            workaround=incident.workaround if form.include_workaround.data else "",
            article_type=form.article_type.data,
            category_id=form.category_id.data,
            visibility=form.visibility.data,
            author_id=current_user.id,
            source_incident_id=incident_id,
            status=KnowledgeStatus.DRAFT,
            priority=incident.priority if hasattr(incident, 'priority') else 'MEDIUM'
        )
        
        # Add additional content
        if form.additional_content.data:
            if article.description:
                article.description += f"\n\n{form.additional_content.data}"
            else:
                article.description = form.additional_content.data
        
        # Add environment information
        if hasattr(incident, 'environment') and incident.environment:
            article.environment = incident.environment
        
        # Extract keywords from incident
        keywords = []
        if incident.title:
            keywords.extend(incident.title.split())
        if hasattr(incident, 'category') and incident.category:
            keywords.append(incident.category)
        if hasattr(incident, 'service') and incident.service:
            keywords.append(incident.service)
        
        article.keywords = ', '.join(set(keywords))
        
        db.session.add(article)
        db.session.commit()
        
        # Update incident to reference the new knowledge article
        incident.knowledge_article_id = article.id
        db.session.commit()
        
        flash(f'Knowledge article "{article.title}" created from incident {incident.id}.', 'success')
        return redirect(url_for('knowledge.view_article', id=article.id))
    
    return render_template('knowledge/convert_incident.html',
                         form=form,
                         incident=incident)

@knowledge.route('/subscribe/<subscription_type>/<int:subscription_id>', methods=['POST'])
@login_required
def subscribe(subscription_type, subscription_id):
    """Subscribe to category or article updates"""
    if subscription_type not in ['category', 'article']:
        abort(400)
    
    existing = KnowledgeSubscription.query.filter_by(
        user_id=current_user.id,
        subscription_type=subscription_type,
        subscription_id=subscription_id
    ).first()
    
    if existing:
        flash('You are already subscribed to updates.', 'info')
    else:
        subscription = KnowledgeSubscription(
            user_id=current_user.id,
            subscription_type=subscription_type,
            subscription_id=subscription_id
        )
        db.session.add(subscription)
        db.session.commit()
        flash('Successfully subscribed to updates!', 'success')
    
    return redirect(request.referrer or url_for('knowledge.index'))

@knowledge.route('/unsubscribe/<subscription_type>/<int:subscription_id>', methods=['POST'])
@login_required
def unsubscribe(subscription_type, subscription_id):
    """Unsubscribe from updates"""
    subscription = KnowledgeSubscription.query.filter_by(
        user_id=current_user.id,
        subscription_type=subscription_type,
        subscription_id=subscription_id
    ).first()
    
    if subscription:
        db.session.delete(subscription)
        db.session.commit()
        flash('Successfully unsubscribed from updates.', 'success')
    else:
        flash('Subscription not found.', 'error')
    
    return redirect(request.referrer or url_for('knowledge.index'))

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

# API Endpoints for AJAX functionality
@knowledge.route('/api/search-suggestions')
@login_required
def search_suggestions():
    """Get search suggestions for autocomplete"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    # Search in titles and keywords
    suggestions = []
    
    # Article titles
    articles = get_user_accessible_articles().filter(
        and_(
            KnowledgeArticle.title.ilike(f'%{query}%'),
            KnowledgeArticle.status == KnowledgeStatus.PUBLISHED
        )
    ).limit(5).all()
    
    for article in articles:
        suggestions.append({
            'type': 'article',
            'title': article.title,
            'url': url_for('knowledge.view_article', id=article.id)
        })
    
    # Categories
    categories = KnowledgeCategory.query.filter(
        and_(
            KnowledgeCategory.name.ilike(f'%{query}%'),
            KnowledgeCategory.is_active == True
        )
    ).limit(3).all()
    
    for category in categories:
        suggestions.append({
            'type': 'category',
            'title': category.name,
            'url': url_for('knowledge.view_category', id=category.id)
        })
    
    # Tags
    tags = KnowledgeTag.query.filter(
        KnowledgeTag.name.ilike(f'%{query}%')
    ).limit(3).all()
    
    for tag in tags:
        suggestions.append({
            'type': 'tag',
            'title': tag.name,
            'url': url_for('knowledge.search', tags=tag.name)
        })
    
    return jsonify(suggestions[:10])

@knowledge.route('/api/article/<int:id>/verify', methods=['POST'])
@login_required
def verify_article(id):
    """Mark article as verified"""
    if not (current_user.has_role('admin') or current_user.has_role('knowledge_admin')):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    article = KnowledgeArticle.query.get_or_404(id)
    article.last_verified_at = datetime.now(timezone.utc)
    article.verified_by_id = current_user.id
    
    db.session.commit()
    
    return jsonify({'success': True, 'verified_at': article.last_verified_at.isoformat()})

@knowledge.route('/api/tags/autocomplete')
@login_required
def tag_autocomplete():
    """Get tag suggestions for autocomplete"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 1:
        return jsonify([])
    
    tags = KnowledgeTag.query.filter(
        KnowledgeTag.name.ilike(f'%{query}%')
    ).order_by(desc(KnowledgeTag.usage_count)).limit(10).all()
    
    return jsonify([tag.name for tag in tags])

# Error Handlers
@knowledge.errorhandler(403)
def forbidden(error):
    return render_template('knowledge/errors/403.html'), 403

@knowledge.errorhandler(404)
def not_found(error):
    return render_template('knowledge/errors/404.html'), 404
