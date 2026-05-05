"""
CHANGE 7: Bulk Vehicle & Service Import Routes
CSV import with validation, deduplication, dry-run, and transaction rollback
Features: Batch operations, error handling, progress tracking, transaction management
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import BulkImportJob, ImportRecord, Vehicle, Service, User
from app.utils import success_response, error_response
from datetime import datetime
import csv
import io
import json
from sqlalchemy.exc import IntegrityError

bp = Blueprint('import', __name__, url_prefix='/api/import')


# ============================================================================
# BULK IMPORT MAIN ENDPOINT
# ============================================================================

@bp.route('/jobs', methods=['POST'])
@jwt_required()
def create_import_job():
    """
    Create and start a bulk import job
    Accepts CSV file with vehicle or service data
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response('Admin access required', 403)
        
        # Check for file
        if 'file' not in request.files:
            return error_response('No file provided', 400)
        
        file = request.files['file']
        if file.filename == '':
            return error_response('No file selected', 400)
        
        if not file.filename.endswith('.csv'):
            return error_response('Only CSV files are supported', 400)
        
        # Get parameters
        import_type = request.form.get('import_type', 'vehicles')  # vehicles, services, both
        dry_run = request.form.get('dry_run', 'false').lower() == 'true'
        job_name = request.form.get('job_name', f'Import {import_type} - {datetime.now().strftime("%Y-%m-%d %H:%M")}'  )
        
        if import_type not in ['vehicles', 'services', 'both']:
            return error_response('Invalid import_type', 400)
        
        # Read CSV
        stream = io.StringIO(file.stream.read().decode('UTF-8'), newline=None)
        csv_reader = csv.DictReader(stream)
        records = list(csv_reader)
        
        # Create job
        job = BulkImportJob(
            job_name=job_name,
            import_type=import_type,
            file_name=file.filename,
            file_size_bytes=len(file.read()),
            created_by=user_id,
            dry_run=dry_run,
            status='validating'
        )
        
        file.seek(0)
        stream = io.StringIO(file.stream.read().decode('UTF-8'), newline=None)
        
        try:
            reader = csv.DictReader(stream)
            records = list(reader)
            job.total_records = len(records)
            
            db.session.add(job)
            db.session.flush()
            
            # Process records
            for row_num, row in enumerate(records, start=2):  # Start at 2 (skip header)
                process_import_record(job, row, row_num, import_type)
            
            job.status = 'completed' if not dry_run else 'validated'
            job.completed_at = datetime.utcnow()
            
            # Count results
            job.successful_records = ImportRecord.query.filter_by(
                job_id=job.id, status='success'
            ).count()
            job.failed_records = ImportRecord.query.filter_by(
                job_id=job.id, status='failed'
            ).count()
            
            if dry_run:
                # Rollback changes for dry run
                db.session.rollback()
                db.session.add(job)
            
            db.session.commit()
            
            return success_response({
                'job_id': job.id,
                'status': job.status,
                'total_records': job.total_records,
                'successful': job.successful_records,
                'failed': job.failed_records,
                'dry_run': dry_run
            }, 201)
        except Exception as e:
            db.session.rollback()
            job.status = 'failed'
            job.notes = str(e)
            db.session.add(job)
            db.session.commit()
            return error_response(f'Import processing failed: {str(e)}', 500)
    
    except Exception as e:
        return error_response(str(e), 500)


@bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_import_job(job_id):
    """Get details of an import job"""
    try:
        job = BulkImportJob.query.get(job_id)
        if not job:
            return error_response('Job not found', 404)
        
        return success_response({
            'id': job.id,
            'name': job.job_name,
            'import_type': job.import_type,
            'status': job.status,
            'total_records': job.total_records,
            'processed_records': job.processed_records,
            'successful_records': job.successful_records,
            'failed_records': job.failed_records,
            'dry_run': job.dry_run,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None
        })
    except Exception as e:
        return error_response(str(e), 500)


@bp.route('/jobs', methods=['GET'])
@jwt_required()
def list_import_jobs():
    """List all import jobs"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        jobs = BulkImportJob.query.order_by(
            BulkImportJob.created_at.desc()
        ).paginate(page=page, per_page=per_page)
        
        return success_response({
            'total': jobs.total,
            'pages': jobs.pages,
            'current_page': page,
            'jobs': [
                {
                    'id': j.id,
                    'name': j.job_name,
                    'import_type': j.import_type,
                    'status': j.status,
                    'total_records': j.total_records,
                    'successful_records': j.successful_records,
                    'failed_records': j.failed_records,
                    'created_at': j.created_at.isoformat()
                }
                for j in jobs.items
            ]
        })
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================================
# IMPORT RECORD DETAILS
# ============================================================================

@bp.route('/jobs/<int:job_id>/records', methods=['GET'])
def get_import_records(job_id):
    """Get records from an import job"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status', None)  # success, failed, duplicate
        
        query = ImportRecord.query.filter_by(job_id=job_id)
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        records = query.paginate(page=page, per_page=per_page)
        
        return success_response({
            'total': records.total,
            'pages': records.pages,
            'current_page': page,
            'records': [
                {
                    'id': r.id,
                    'row_number': r.row_number,
                    'record_type': r.record_type,
                    'external_id': r.external_id,
                    'status': r.status,
                    'target_entity_id': r.target_entity_id,
                    'errors': r.validation_errors,
                    'error_message': r.error_message,
                    'duplicate_detected': r.duplicate_detected
                }
                for r in records.items
            ]
        })
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================================
# RETRY FAILED RECORDS
# ============================================================================

@bp.route('/jobs/<int:job_id>/retry', methods=['POST'])
@jwt_required()
def retry_failed_records(job_id):
    """Retry failed records from an import job"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response('Admin access required', 403)
        
        job = BulkImportJob.query.get(job_id)
        if not job:
            return error_response('Job not found', 404)
        
        # Get failed records
        failed_records = ImportRecord.query.filter_by(
            job_id=job_id, status='failed'
        ).all()
        
        retried = 0
        for record in failed_records:
            try:
                # Attempt to reprocess
                raw_data = json.loads(record.raw_data) if isinstance(record.raw_data, str) else record.raw_data
                process_import_record(job, raw_data, record.row_number, job.import_type, record.id)
                retried += 1
            except Exception as e:
                record.error_message = str(e)
        
        db.session.commit()
        
        return success_response({
            'retried': retried,
            'message': f'Retried {retried} failed records'
        })
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def process_import_record(job, row_data, row_number, import_type, record_id=None):
    """
    Process a single import record
    Validates data, checks for duplicates, creates vehicles/services
    """
    try:
        record = ImportRecord.query.get(record_id) if record_id else None
        if not record:
            record = ImportRecord(
                job_id=job.id,
                row_number=row_number,
                raw_data=json.dumps(row_data),
                status='pending'
            )
            db.session.add(record)
        
        validation_errors = []
        
        if import_type in ['vehicles', 'both'] and len(row_data) > 0:
            # Validate vehicle data
            required_vehicle_fields = ['make', 'model', 'year', 'vin']
            for field in required_vehicle_fields:
                if field not in row_data or not row_data[field]:
                    validation_errors.append(f'Missing required field: {field}')
            
            if validation_errors:
                record.status = 'failed'
                record.validation_errors = validation_errors
                record.error_message = '; '.join(validation_errors)
                db.session.add(record)
                return
            
            # Check for duplicates
            existing_vehicle = Vehicle.query.filter_by(vin=row_data['vin']).first()
            if existing_vehicle:
                record.status = 'duplicate'
                record.duplicate_detected = True
                record.duplicate_of_record = existing_vehicle.id
                db.session.add(record)
                return
            
            # Create vehicle
            vehicle = Vehicle(
                make=row_data.get('make'),
                model=row_data.get('model'),
                year=int(row_data.get('year', 0)),
                vin=row_data.get('vin'),
                license_plate=row_data.get('license_plate'),
                color=row_data.get('color'),
                price=float(row_data.get('price', 0)),
                mileage=int(row_data.get('mileage', 0)) if row_data.get('mileage') else 0,
                fuel_type=row_data.get('fuel_type', 'petrol'),
                transmission=row_data.get('transmission', 'manual'),
                status=row_data.get('status', 'available')
            )
            
            db.session.add(vehicle)
            db.session.flush()
            
            record.status = 'success'
            record.target_entity_id = vehicle.id
            record.target_entity_type = 'Vehicle'
            record.processed_data = json.dumps({
                'vehicle_id': vehicle.id,
                'make': vehicle.make,
                'model': vehicle.model,
                'year': vehicle.year
            })
            job.successful_records = job.successful_records + 1
        
        elif import_type in ['services', 'both'] and 'service_type' in row_data:
            # Validate service data
            if not row_data.get('service_type') or not row_data.get('cost'):
                validation_errors.append('Missing required fields: service_type or cost')
            
            if validation_errors:
                record.status = 'failed'
                record.validation_errors = validation_errors
                record.error_message = '; '.join(validation_errors)
                db.session.add(record)
                return
            
            # Create service
            service = Service(
                service_type=row_data.get('service_type'),
                description=row_data.get('description', ''),
                cost=float(row_data.get('cost', 0)),
                duration_hours=int(row_data.get('duration_hours', 1)) if row_data.get('duration_hours') else 1
            )
            
            db.session.add(service)
            db.session.flush()
            
            record.status = 'success'
            record.target_entity_id = service.id
            record.target_entity_type = 'Service'
            record.processed_data = json.dumps({
                'service_id': service.id,
                'service_type': service.service_type,
                'cost': service.cost
            })
            job.successful_records = job.successful_records + 1
        
        job.processed_records = job.processed_records + 1
        db.session.add(record)
    
    except Exception as e:
        record.status = 'failed'
        record.error_message = str(e)
        record.validation_errors = [str(e)]
        job.failed_records = job.failed_records + 1
        db.session.add(record)


# ============================================================================
# TEMPLATE DOWNLOAD
# ============================================================================

@bp.route('/templates/vehicles', methods=['GET'])
def get_vehicle_import_template():
    """Get CSV template for vehicle import"""
    try:
        template = """make,model,year,vin,license_plate,color,price,mileage,fuel_type,transmission,status
Toyota,Camry,2022,JTDDR32K822234567,ABC123,Silver,25000,15000,petrol,automatic,available
Honda,Civic,2021,1HGCV1F32MF123456,XYZ789,Blue,20000,20000,petrol,manual,available
"""
        return success_response({'template': template})
    except Exception as e:
        return error_response(str(e), 500)


@bp.route('/templates/services', methods=['GET'])
def get_service_import_template():
    """Get CSV template for service import"""
    try:
        template = """service_type,description,cost,duration_hours
Oil Change,Regular oil and filter change,150,1
Brake Service,Full brake inspection and pad replacement,250,2
Tire Rotation,Rotate all tires for even wear,75,1
"""
        return success_response({'template': template})
    except Exception as e:
        return error_response(str(e), 500)
