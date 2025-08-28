"""
Inventory Management Forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DecimalField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

class InventoryCategoryForm(FlaskForm):
    """Form for creating/editing inventory categories"""
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Category')

class InventoryItemForm(FlaskForm):
    """Form for creating/editing inventory items"""
    part_number = StringField('Part Number', validators=[DataRequired(), Length(min=2, max=100)])
    name = StringField('Item Name', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    manufacturer = StringField('Manufacturer', validators=[Optional(), Length(max=100)])
    model = StringField('Model', validators=[Optional(), Length(max=100)])
    
    # Stock Information
    quantity_in_stock = IntegerField('Current Stock', validators=[DataRequired(), NumberRange(min=0)])
    minimum_stock_level = IntegerField('Minimum Stock Level', validators=[DataRequired(), NumberRange(min=0)])
    maximum_stock_level = IntegerField('Maximum Stock Level', validators=[DataRequired(), NumberRange(min=1)])
    condition = SelectField('Part Condition', 
                          choices=[('new', 'New'), ('faulty', 'Faulty')],
                          validators=[DataRequired()],
                          default='new')
    unit_cost = DecimalField('Unit Cost ($)', validators=[Optional(), NumberRange(min=0)], places=2)
    
    # Item Details
    weight = DecimalField('Weight (kg)', validators=[Optional(), NumberRange(min=0)], places=3)
    dimensions = StringField('Dimensions', validators=[Optional(), Length(max=100)])
    compatible_uav_models = TextAreaField('Compatible UAV Models', 
                                        validators=[Optional(), Length(max=500)],
                                        description="Enter compatible UAV models (one per line)")
    
    # Category
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)
    
    submit = SubmitField('Save Item')

class InventoryTransactionForm(FlaskForm):
    """Form for recording inventory transactions"""
    transaction_type = SelectField('Transaction Type', 
                                 choices=[('IN', 'Stock In'), ('OUT', 'Stock Out'), ('ADJUSTMENT', 'Adjustment')],
                                 validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    unit_cost = DecimalField('Unit Cost ($)', validators=[Optional(), NumberRange(min=0)], places=2)
    reference_type = SelectField('Reference Type',
                               choices=[('PURCHASE', 'Purchase'), ('WORKORDER', 'Work Order'), 
                                      ('ADJUSTMENT', 'Stock Adjustment'), ('RETURN', 'Return')],
                               validators=[DataRequired()])
    reference_id = StringField('Reference ID', validators=[Optional(), Length(max=50)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Record Transaction')

class WorkOrderPartRequestForm(FlaskForm):
    """Form for requesting parts for work orders"""
    inventory_item_id = SelectField('Select Part', coerce=int, validators=[DataRequired()])
    quantity_requested = IntegerField('Quantity Needed', validators=[DataRequired(), NumberRange(min=1)])
    notes = TextAreaField('Notes/Reason', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Request Part')

class StockSearchForm(FlaskForm):
    """Form for searching inventory items"""
    search_term = StringField('Search', validators=[Optional(), Length(max=100)])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    stock_status = SelectField('Stock Status',
                              choices=[('', 'All'), ('in_stock', 'In Stock'), 
                                     ('low_stock', 'Low Stock'), ('out_of_stock', 'Out of Stock')],
                              validators=[Optional()])
    submit = SubmitField('Search')
