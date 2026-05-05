from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import Invoice, InvoiceItem, Customer, User

bp = Blueprint('invoices', __name__, url_prefix='/api/invoices')

@bp.route('', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get invoices (customer sees own, admin sees all)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role == 'admin':
        invoices = Invoice.query.all()
    else:
        customer = Customer.query.filter_by(user_id=user_id).first()
        invoices = Invoice.query.filter_by(customer_id=customer.id).all() if customer else []
    
    return jsonify([{
        'id': i.id,
        'invoice_number': i.invoice_number,
        'customer_id': i.customer_id,
        'invoice_date': i.invoice_date.isoformat(),
        'due_date': i.due_date.isoformat() if i.due_date else None,
        'subtotal': i.subtotal,
        'tax': i.tax,
        'total': i.total,
        'status': i.status
    } for i in invoices]), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_invoice():
    """Create a new invoice (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if not data.get('customer_id') or not data.get('invoice_number'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404
    
    invoice = Invoice(
        customer_id=data['customer_id'],
        invoice_number=data['invoice_number'],
        invoice_date=datetime.fromisoformat(data.get('invoice_date', datetime.utcnow().isoformat())),
        due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
        subtotal=data.get('subtotal', 0),
        tax=data.get('tax', 0),
        total=data.get('total', 0),
        status=data.get('status', 'pending')
    )
    
    db.session.add(invoice)
    db.session.commit()
    
    return jsonify({'message': 'Invoice created successfully', 'id': invoice.id}), 201

@bp.route('/<int:invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    """Get invoice details"""
    invoice = Invoice.query.get(invoice_id)
    
    if not invoice:
        return jsonify({'message': 'Invoice not found'}), 404
    
    return jsonify({
        'id': invoice.id,
        'invoice_number': invoice.invoice_number,
        'customer_id': invoice.customer_id,
        'invoice_date': invoice.invoice_date.isoformat(),
        'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
        'subtotal': invoice.subtotal,
        'tax': invoice.tax,
        'total': invoice.total,
        'status': invoice.status,
        'items': [
            {
                'id': item.id,
                'description': item.description,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_price': item.total_price
            } for item in invoice.items
        ]
    }), 200

@bp.route('/<int:invoice_id>/items', methods=['POST'])
@jwt_required()
def add_invoice_item(invoice_id):
    """Add item to invoice"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return jsonify({'message': 'Invoice not found'}), 404
    
    data = request.get_json()
    required_fields = ['description', 'quantity', 'unit_price']
    
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    item = InvoiceItem(
        invoice_id=invoice_id,
        description=data['description'],
        quantity=data['quantity'],
        unit_price=data['unit_price'],
        total_price=data['quantity'] * data['unit_price']
    )
    
    db.session.add(item)
    db.session.commit()
    
    # Update invoice totals
    invoice.subtotal = sum(item.total_price for item in invoice.items)
    invoice.total = invoice.subtotal + invoice.tax
    db.session.commit()
    
    return jsonify({'message': 'Item added successfully', 'id': item.id}), 201

@bp.route('/<int:invoice_id>', methods=['PUT'])
@jwt_required()
def update_invoice(invoice_id):
    """Update invoice status (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return jsonify({'message': 'Invoice not found'}), 404
    
    data = request.get_json()
    invoice.status = data.get('status', invoice.status)
    
    db.session.commit()
    return jsonify({'message': 'Invoice updated successfully'}), 200
