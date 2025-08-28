"""
Knowledge Management Models
Following KEDB (Knowledge-Enabled Database) best practices
"""

from datetime import datetime, timezone
from sqlalchemy import event
from app import db
from app.models import User
import enum

class KnowledgeStatus(enum.Enum):
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"
    EXPIRED = "EXPIRED"

class KnowledgeType(enum.Enum):
    SOLUTION = "SOLUTION"
    PROCEDURE = "PROCEDURE"
    FAQ = "FAQ"
    TROUBLESHOOTING = "TROUBLESHOOTING"
    BEST_PRACTICE = "BEST_PRACTICE"
    POLICY = "POLICY"
    TUTORIAL = "TUTORIAL"
    REFERENCE = "REFERENCE"

class VisibilityLevel(enum.Enum):
    PUBLIC = "PUBLIC"          # All authenticated users
    DEPARTMENT = "DEPARTMENT"  # Users in same department
    ROLE_BASED = "ROLE_BASED" # Specific roles only
    PRIVATE = "PRIVATE"       # Author and designated users only
    RESTRICTED = "RESTRICTED" # Admin approval required

class KnowledgeCategory(db.Model):
    """Knowledge Base Categories with hierarchical structure"""
    __tablename__ = 'knowledge_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('knowledge_categories.id'))
    icon = db.Column(db.String(50))
    color = db.Column(db.String(7))  # Hex color code
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    parent = db.relationship('KnowledgeCategory', remote_side=[id], backref='children')
    articles = db.relationship('KnowledgeArticle', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<KnowledgeCategory {self.name}>'
    
    @property
    def full_path(self):
        """Get full category path"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
    
    @property
    def article_count(self):
        """Count published articles in this category"""
        return self.articles.filter_by(status=KnowledgeStatus.PUBLISHED).count()

class KnowledgeTag(db.Model):
    """Tags for knowledge articles"""
    __tablename__ = 'knowledge_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    color = db.Column(db.String(7))  # Hex color code
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<KnowledgeTag {self.name}>'

# Association table for article tags
article_tags = db.Table('knowledge_article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('knowledge_articles.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('knowledge_tags.id'), primary_key=True)
)

# Association table for article visibility roles
article_visibility_roles = db.Table('knowledge_article_visibility_roles',
    db.Column('article_id', db.Integer, db.ForeignKey('knowledge_articles.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

# Association table for article visibility users
article_visibility_users = db.Table('knowledge_article_visibility_users',
    db.Column('article_id', db.Integer, db.ForeignKey('knowledge_articles.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class KnowledgeArticle(db.Model):
    """Main Knowledge Base Article following KEDB best practices"""
    __tablename__ = 'knowledge_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    kb_id = db.Column(db.String(20), unique=True, nullable=False)  # KB-YYYY-NNNN format
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    solution = db.Column(db.Text)
    workaround = db.Column(db.Text)
    
    # KEDB Standard Fields
    problem_statement = db.Column(db.Text)
    environment = db.Column(db.Text)
    cause = db.Column(db.Text)
    resolution_steps = db.Column(db.Text)
    prevention_steps = db.Column(db.Text)
    related_documents = db.Column(db.Text)
    
    # Classification
    article_type = db.Column(db.Enum(KnowledgeType), nullable=False, default=KnowledgeType.SOLUTION)
    status = db.Column(db.Enum(KnowledgeStatus), nullable=False, default=KnowledgeStatus.DRAFT)
    visibility = db.Column(db.Enum(VisibilityLevel), nullable=False, default=VisibilityLevel.PUBLIC)
    priority = db.Column(db.String(20), default='MEDIUM')  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Categorization
    category_id = db.Column(db.Integer, db.ForeignKey('knowledge_categories.id'))
    keywords = db.Column(db.Text)  # Comma-separated keywords for search
    
    # User Management
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Lifecycle Management
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    reviewed_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    published_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Quality Metrics
    view_count = db.Column(db.Integer, default=0)
    helpful_count = db.Column(db.Integer, default=0)
    not_helpful_count = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0.0)
    last_verified_at = db.Column(db.DateTime)
    verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Version Control
    version = db.Column(db.String(10), default='1.0')
    parent_article_id = db.Column(db.Integer, db.ForeignKey('knowledge_articles.id'))
    
    # Source Integration (Optional - comment out for now)
    # source_incident_id = db.Column(db.Integer, db.ForeignKey('service_incidents.id'))
    # source_workorder_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'))
    
    # Relationships
    author = db.relationship('User', foreign_keys=[author_id], backref='authored_articles')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviewed_articles')
    approver = db.relationship('User', foreign_keys=[approver_id], backref='approved_articles')
    verified_by = db.relationship('User', foreign_keys=[verified_by_id], backref='verified_articles')
    
    tags = db.relationship('KnowledgeTag', secondary=article_tags, backref='articles')
    visibility_roles = db.relationship('Role', secondary=article_visibility_roles, backref='visible_articles')
    visibility_users = db.relationship('User', secondary=article_visibility_users, backref='accessible_articles')
    
    parent_article = db.relationship('KnowledgeArticle', remote_side=[id], backref='child_versions')
    comments = db.relationship('KnowledgeComment', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    attachments = db.relationship('KnowledgeAttachment', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('KnowledgeRating', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    views = db.relationship('KnowledgeView', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<KnowledgeArticle {self.kb_id}: {self.title}>'
    
    @property
    def helpfulness_percentage(self):
        """Calculate helpfulness percentage"""
        total_feedback = self.helpful_count + self.not_helpful_count
        if total_feedback == 0:
            return 0
        return round((self.helpful_count / total_feedback) * 100, 1)
    
    @property
    def is_expired(self):
        """Check if article is expired"""
        if self.expires_at:
            return datetime.now(timezone.utc) > self.expires_at
        return False
    
    @property
    def days_since_verification(self):
        """Days since last verification"""
        if self.last_verified_at:
            return (datetime.now(timezone.utc) - self.last_verified_at).days
        return None
    
    def can_user_view(self, user):
        """Check if user can view this article"""
        if self.status != KnowledgeStatus.PUBLISHED:
            return user == self.author or user.has_role('admin') or user.has_role('knowledge_admin')
        
        if self.visibility == VisibilityLevel.PUBLIC:
            return True
        elif self.visibility == VisibilityLevel.DEPARTMENT:
            return user.department == self.author.department
        elif self.visibility == VisibilityLevel.ROLE_BASED:
            return user.role in self.visibility_roles
        elif self.visibility == VisibilityLevel.PRIVATE:
            return user == self.author or user in self.visibility_users
        elif self.visibility == VisibilityLevel.RESTRICTED:
            return user.has_role('admin') or user.has_role('knowledge_admin')
        
        return False
    
    def can_user_edit(self, user):
        """Check if user can edit this article"""
        if user.has_role('admin') or user.has_role('knowledge_admin'):
            return True
        if user == self.author and self.status in [KnowledgeStatus.DRAFT, KnowledgeStatus.REVIEW]:
            return True
        return False

class KnowledgeComment(db.Model):
    """Comments on knowledge articles"""
    __tablename__ = 'knowledge_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('knowledge_articles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)  # Internal comments for reviewers
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref='knowledge_comments')
    
    def __repr__(self):
        return f'<KnowledgeComment {self.id}>'

class KnowledgeRating(db.Model):
    """User ratings for knowledge articles"""
    __tablename__ = 'knowledge_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('knowledge_articles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 scale
    feedback = db.Column(db.Text)
    is_helpful = db.Column(db.Boolean)  # True for helpful, False for not helpful
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref='knowledge_ratings')
    
    __table_args__ = (db.UniqueConstraint('article_id', 'user_id', name='unique_user_article_rating'),)
    
    def __repr__(self):
        return f'<KnowledgeRating {self.rating}/5>'

class KnowledgeView(db.Model):
    """Track article views for analytics"""
    __tablename__ = 'knowledge_views'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('knowledge_articles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    viewed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref='knowledge_views')
    
    def __repr__(self):
        return f'<KnowledgeView {self.article_id}>'

class KnowledgeAttachment(db.Model):
    """File attachments for knowledge articles"""
    __tablename__ = 'knowledge_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('knowledge_articles.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger)
    mime_type = db.Column(db.String(100))
    description = db.Column(db.String(500))
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    uploaded_by = db.relationship('User', backref='uploaded_knowledge_attachments')
    
    def __repr__(self):
        return f'<KnowledgeAttachment {self.original_filename}>'

class KnowledgeSubscription(db.Model):
    """User subscriptions to knowledge categories or articles"""
    __tablename__ = 'knowledge_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subscription_type = db.Column(db.String(20), nullable=False)  # 'category' or 'article'
    subscription_id = db.Column(db.Integer, nullable=False)  # category_id or article_id
    notify_new = db.Column(db.Boolean, default=True)
    notify_updates = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref='knowledge_subscriptions')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'subscription_type', 'subscription_id', 
                          name='unique_user_subscription'),
    )
    
    def __repr__(self):
        return f'<KnowledgeSubscription {self.subscription_type}:{self.subscription_id}>'

class KnowledgeWorkflow(db.Model):
    """Workflow tracking for article approval process"""
    __tablename__ = 'knowledge_workflows'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('knowledge_articles.id'), nullable=False)
    from_status = db.Column(db.Enum(KnowledgeStatus))
    to_status = db.Column(db.Enum(KnowledgeStatus), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    article = db.relationship('KnowledgeArticle', backref='workflow_history')
    user = db.relationship('User', backref='knowledge_workflow_actions')
    
    def __repr__(self):
        return f'<KnowledgeWorkflow {self.from_status} -> {self.to_status}>'

# Event listeners for automatic KB ID generation
@event.listens_for(KnowledgeArticle, 'before_insert')
def generate_kb_id(mapper, connection, target):
    """Generate unique KB ID in format KB-YYYY-NNNN"""
    if not target.kb_id:
        year = datetime.now().year
        # Get the next sequence number for this year
        result = connection.execute(
            db.text("SELECT COUNT(*) FROM knowledge_articles WHERE kb_id LIKE :pattern"),
            {"pattern": f"KB-{year}-%"}
        ).scalar()
        
        sequence = (result or 0) + 1
        target.kb_id = f"KB-{year}-{sequence:04d}"

# Event listeners for updating metrics
@event.listens_for(KnowledgeRating, 'after_insert')
@event.listens_for(KnowledgeRating, 'after_update')
def update_article_rating(mapper, connection, target):
    """Update article average rating when rating changes"""
    # This will be handled in the application layer to avoid circular imports
    pass
