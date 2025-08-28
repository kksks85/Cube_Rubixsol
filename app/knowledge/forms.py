"""
Knowledge Management Forms
Flask-WTF forms for knowledge base operations
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, TextAreaField, SelectField, BooleanField, 
                    IntegerField, DateTimeField, SubmitField, HiddenField,
                    SelectMultipleField, RadioField)
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Email
from wtforms.widgets import TextArea, CheckboxInput, ListWidget
from app.knowledge.models import KnowledgeStatus, KnowledgeType, VisibilityLevel

def coerce_int_or_none(value):
    """Coerce to int or None if empty"""
    if value == '' or value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class KnowledgeArticleForm(FlaskForm):
    """Form for creating and editing knowledge articles"""
    
    # Basic Information
    title = StringField('Title', validators=[
        DataRequired(message="Title is required"),
        Length(min=10, max=200, message="Title must be between 10 and 200 characters")
    ], render_kw={"placeholder": "Enter a clear, descriptive title"})
    
    summary = TextAreaField('Summary', validators=[
        DataRequired(message="Summary is required"),
        Length(min=20, max=500, message="Summary must be between 20 and 500 characters")
    ], render_kw={
        "placeholder": "Brief summary of the issue and solution (20-500 characters)",
        "rows": 3
    })
    
    description = TextAreaField('Problem Description', validators=[
        Optional(),
        Length(max=2000, message="Description cannot exceed 2000 characters")
    ], render_kw={
        "placeholder": "Detailed description of the problem or topic",
        "rows": 5
    })
    
    # KEDB Standard Fields
    problem_statement = TextAreaField('Problem Statement', validators=[Optional()],
        render_kw={
            "placeholder": "Clear statement of the problem being addressed",
            "rows": 3
        })
    
    environment = TextAreaField('Environment', validators=[Optional()],
        render_kw={
            "placeholder": "System environment, versions, configurations affected",
            "rows": 2
        })
    
    cause = TextAreaField('Root Cause', validators=[Optional()],
        render_kw={
            "placeholder": "Underlying cause of the issue",
            "rows": 3
        })
    
    solution = TextAreaField('Solution', validators=[Optional()],
        render_kw={
            "placeholder": "Step-by-step solution or detailed information",
            "rows": 8
        })
    
    resolution_steps = TextAreaField('Resolution Steps', validators=[Optional()],
        render_kw={
            "placeholder": "Numbered steps to resolve the issue",
            "rows": 6
        })
    
    workaround = TextAreaField('Workaround', validators=[Optional()],
        render_kw={
            "placeholder": "Temporary workaround if available",
            "rows": 4
        })
    
    prevention_steps = TextAreaField('Prevention Steps', validators=[Optional()],
        render_kw={
            "placeholder": "Steps to prevent this issue from occurring",
            "rows": 4
        })
    
    related_documents = TextAreaField('Related Documents', validators=[Optional()],
        render_kw={
            "placeholder": "Links to related documentation, tickets, or articles",
            "rows": 2
        })
    
    # Classification
    article_type = SelectField('Article Type', 
        choices=[(type.value, type.value.replace('_', ' ').title()) for type in KnowledgeType],
        validators=[DataRequired(message="Article type is required")])
    
    category_id = SelectField('Category', coerce=coerce_int_or_none, validators=[Optional()])
    
    priority = SelectField('Priority', 
        choices=[
            ('LOW', 'Low'),
            ('MEDIUM', 'Medium'),
            ('HIGH', 'High'),
            ('CRITICAL', 'Critical')
        ],
        default='MEDIUM',
        validators=[DataRequired()])
    
    # Visibility and Access Control
    visibility = SelectField('Visibility Level',
        choices=[(level.value, level.value.replace('_', ' ').title()) for level in VisibilityLevel],
        default=VisibilityLevel.PUBLIC.value,
        validators=[DataRequired()])
    
    visibility_roles = MultiCheckboxField('Visible to Roles', coerce=int, validators=[Optional()])
    visibility_users = MultiCheckboxField('Visible to Specific Users', coerce=int, validators=[Optional()])
    
    # Tags and Keywords
    keywords = StringField('Keywords', validators=[Optional()],
        render_kw={
            "placeholder": "Comma-separated keywords for search optimization"
        })
    
    tags = StringField('Tags', validators=[Optional()],
        render_kw={
            "placeholder": "Comma-separated tags (e.g., windows, network, database)"
        })
    
    # Lifecycle Management
    expires_at = DateTimeField('Expiration Date', validators=[Optional()],
        render_kw={"placeholder": "YYYY-MM-DD HH:MM"})
    
    # Workflow Actions
    status = SelectField('Status',
        choices=[(status.value, status.value.title()) for status in KnowledgeStatus],
        validators=[DataRequired()])
    
    reviewer_id = SelectField('Reviewer', coerce=coerce_int_or_none, validators=[Optional()])
    
    # File Attachments
    attachments = FileField('Attachments', 
        validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'gif'],
                                          'Only documents and images are allowed')])
    
    # Workflow Comments
    workflow_comments = TextAreaField('Comments', validators=[Optional()],
        render_kw={
            "placeholder": "Comments about status change or review",
            "rows": 3
        })
    
    submit = SubmitField('Save Article')
    submit_for_review = SubmitField('Submit for Review')
    publish = SubmitField('Publish')
    reject = SubmitField('Reject')
    approve = SubmitField('Approve')

class KnowledgeCategoryForm(FlaskForm):
    """Form for managing knowledge categories"""
    
    name = StringField('Category Name', validators=[
        DataRequired(message="Category name is required"),
        Length(min=2, max=100, message="Name must be between 2 and 100 characters")
    ])
    
    description = TextAreaField('Description', validators=[Optional()],
        render_kw={"rows": 3})
    
    parent_id = SelectField('Parent Category', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    
    icon = StringField('Icon Class', validators=[Optional()],
        render_kw={"placeholder": "Font Awesome icon class (e.g., fa-folder)"})
    
    color = StringField('Color', validators=[Optional()],
        render_kw={"type": "color", "value": "#007bff"})
    
    sort_order = IntegerField('Sort Order', validators=[Optional(), NumberRange(min=0)],
        default=0)
    
    is_active = BooleanField('Active', default=True)
    
    submit = SubmitField('Save Category')

class KnowledgeSearchForm(FlaskForm):
    """Advanced search form for knowledge base"""
    
    query = StringField('Search Query',
        render_kw={"placeholder": "Search articles, solutions, and procedures..."})
    
    category_id = SelectField('Category', coerce=coerce_int_or_none, validators=[Optional()])
    
    article_type = SelectField('Type', 
        choices=[('', 'All Types')] + [(type.value, type.value.replace('_', ' ').title()) for type in KnowledgeType],
        validators=[Optional()])
    
    status = SelectField('Status',
        choices=[('', 'All Statuses')] + [(status.value, status.value.title()) for status in KnowledgeStatus],
        validators=[Optional()])
    
    priority = SelectField('Priority',
        choices=[('', 'All Priorities'), ('LOW', 'Low'), ('MEDIUM', 'Medium'), 
                ('HIGH', 'High'), ('CRITICAL', 'Critical')],
        validators=[Optional()])
    
    author_id = SelectField('Author', coerce=coerce_int_or_none, validators=[Optional()])
    
    tags = StringField('Tags',
        render_kw={"placeholder": "Comma-separated tags"})
    
    date_from = DateTimeField('Date From', validators=[Optional()])
    date_to = DateTimeField('Date To', validators=[Optional()])
    
    sort_by = SelectField('Sort By',
        choices=[
            ('updated_at', 'Last Updated'),
            ('created_at', 'Date Created'),
            ('view_count', 'Most Viewed'),
            ('helpful_count', 'Most Helpful'),
            ('title', 'Title A-Z')
        ],
        default='updated_at')
    
    sort_order = SelectField('Order',
        choices=[('desc', 'Descending'), ('asc', 'Ascending')],
        default='desc')
    
    submit = SubmitField('Search')

class KnowledgeCommentForm(FlaskForm):
    """Form for adding comments to articles"""
    
    content = TextAreaField('Comment', validators=[
        DataRequired(message="Comment content is required"),
        Length(min=10, max=1000, message="Comment must be between 10 and 1000 characters")
    ], render_kw={"rows": 4, "placeholder": "Add your comment..."})
    
    is_internal = BooleanField('Internal Comment (visible to reviewers only)')
    
    submit = SubmitField('Add Comment')

class KnowledgeRatingForm(FlaskForm):
    """Form for rating articles"""
    
    rating = RadioField('Rating', 
        choices=[(5, '★★★★★ Excellent'), (4, '★★★★☆ Good'), (3, '★★★☆☆ Average'),
                (2, '★★☆☆☆ Poor'), (1, '★☆☆☆☆ Very Poor')],
        coerce=int,
        validators=[DataRequired(message="Please select a rating")])
    
    is_helpful = BooleanField('This article was helpful')
    
    feedback = TextAreaField('Feedback (Optional)', validators=[Optional()],
        render_kw={"rows": 3, "placeholder": "Additional feedback about this article..."})
    
    submit = SubmitField('Submit Rating')

class KnowledgeFilterForm(FlaskForm):
    """Form for filtering articles in list view"""
    
    status = SelectMultipleField('Status',
        choices=[(status.value, status.value.title()) for status in KnowledgeStatus],
        validators=[Optional()])
    
    article_type = SelectMultipleField('Type',
        choices=[(type.value, type.value.replace('_', ' ').title()) for type in KnowledgeType],
        validators=[Optional()])
    
    category_id = SelectMultipleField('Categories', coerce=int, validators=[Optional()])
    
    author_id = SelectMultipleField('Authors', coerce=int, validators=[Optional()])
    
    apply_filters = SubmitField('Apply Filters')
    clear_filters = SubmitField('Clear Filters')

class IncidentToKnowledgeForm(FlaskForm):
    """Form for converting incidents to knowledge articles"""
    
    incident_id = HiddenField('Incident ID')
    
    title = StringField('Article Title', validators=[
        DataRequired(message="Title is required"),
        Length(min=10, max=200)
    ])
    
    article_type = SelectField('Article Type',
        choices=[(KnowledgeType.SOLUTION.value, 'Solution'),
                (KnowledgeType.TROUBLESHOOTING.value, 'Troubleshooting'),
                (KnowledgeType.PROCEDURE.value, 'Procedure')],
        default=KnowledgeType.SOLUTION.value,
        validators=[DataRequired()])
    
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    
    include_incident_details = BooleanField('Include incident details', default=True)
    include_resolution = BooleanField('Include resolution steps', default=True)
    include_workaround = BooleanField('Include workaround if available', default=True)
    
    additional_content = TextAreaField('Additional Content', validators=[Optional()],
        render_kw={
            "placeholder": "Add any additional information not captured in the incident",
            "rows": 5
        })
    
    visibility = SelectField('Visibility Level',
        choices=[(VisibilityLevel.PUBLIC.value, 'Public'),
                (VisibilityLevel.DEPARTMENT.value, 'Department Only'),
                (VisibilityLevel.ROLE_BASED.value, 'Role Based')],
        default=VisibilityLevel.PUBLIC.value,
        validators=[DataRequired()])
    
    create_article = SubmitField('Create Knowledge Article')
    preview = SubmitField('Preview Article')

class KnowledgeSubscriptionForm(FlaskForm):
    """Form for managing knowledge subscriptions"""
    
    subscription_type = HiddenField('Subscription Type')
    subscription_id = HiddenField('Subscription ID')
    
    notify_new = BooleanField('Notify me of new articles', default=True)
    notify_updates = BooleanField('Notify me of updates', default=True)
    
    subscribe = SubmitField('Subscribe')
    unsubscribe = SubmitField('Unsubscribe')

class KnowledgeImportForm(FlaskForm):
    """Form for importing knowledge articles"""
    
    import_file = FileField('Import File', validators=[
        DataRequired(message="Please select a file to import"),
        FileAllowed(['csv', 'xlsx', 'json'], 'Only CSV, Excel, and JSON files are allowed')
    ])
    
    default_category_id = SelectField('Default Category', coerce=int, validators=[DataRequired()])
    default_author_id = SelectField('Default Author', coerce=int, validators=[DataRequired()])
    
    overwrite_existing = BooleanField('Overwrite existing articles with same KB ID')
    create_categories = BooleanField('Create categories if they don\'t exist', default=True)
    create_tags = BooleanField('Create tags if they don\'t exist', default=True)
    
    import_articles = SubmitField('Import Articles')

class KnowledgeExportForm(FlaskForm):
    """Form for exporting knowledge articles"""
    
    export_format = RadioField('Export Format',
        choices=[('csv', 'CSV'), ('xlsx', 'Excel'), ('json', 'JSON'), ('pdf', 'PDF')],
        default='csv',
        validators=[DataRequired()])
    
    include_fields = MultiCheckboxField('Include Fields',
        choices=[
            ('basic', 'Basic Information'),
            ('content', 'Content Fields'),
            ('metadata', 'Metadata'),
            ('metrics', 'View/Rating Metrics'),
            ('workflow', 'Workflow History')
        ],
        default=['basic', 'content'])
    
    category_filter = SelectMultipleField('Categories', coerce=int, validators=[Optional()])
    status_filter = SelectMultipleField('Status', 
        choices=[(status.value, status.value.title()) for status in KnowledgeStatus],
        validators=[Optional()])
    
    date_from = DateTimeField('From Date', validators=[Optional()])
    date_to = DateTimeField('To Date', validators=[Optional()])
    
    export_articles = SubmitField('Export Articles')

class KnowledgeAnalyticsForm(FlaskForm):
    """Form for knowledge analytics filtering"""
    
    date_range = SelectField('Date Range',
        choices=[
            ('7', 'Last 7 days'),
            ('30', 'Last 30 days'),
            ('90', 'Last 90 days'),
            ('365', 'Last year'),
            ('custom', 'Custom range')
        ],
        default='30')
    
    date_from = DateTimeField('From Date', validators=[Optional()])
    date_to = DateTimeField('To Date', validators=[Optional()])
    
    category_filter = SelectMultipleField('Categories', coerce=int, validators=[Optional()])
    author_filter = SelectMultipleField('Authors', coerce=int, validators=[Optional()])
    
    generate_report = SubmitField('Generate Report')
