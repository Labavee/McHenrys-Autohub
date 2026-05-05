"""
CHANGE 5: Performance Monitoring Routes
Comprehensive API performance and system health monitoring
Features: Metrics tracking, alerts, analytics dashboard
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app import db
from app.models import PerformanceMetric, SystemMetric, MonitoringAlert, User
from app.utils import success_response, error_response
from datetime import datetime, timedelta
from sqlalchemy import func
import json

bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')


# ============================================================================
# PERFORMANCE METRICS ENDPOINTS
# ============================================================================

@bp.route('/performance/summary', methods=['GET'])
def get_performance_summary():
    """
    Get performance metrics summary for the last 24 hours
    Query params: hours (default: 24), endpoint_filter
    """
    try:
        hours = request.args.get('hours', 24, type=int)
        endpoint_filter = request.args.get('endpoint', None)
        
        # Calculate time range
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Build query
        query = PerformanceMetric.query.filter(PerformanceMetric.timestamp >= since)
        if endpoint_filter:
            query = query.filter(PerformanceMetric.endpoint.ilike(f'%{endpoint_filter}%'))
        
        metrics = query.all()
        
        if not metrics:
            return success_response({
                'summary': 'No metrics available',
                'total_requests': 0
            })
        
        # Calculate statistics
        response_times = [m.response_time_ms for m in metrics]
        status_codes = {}
        endpoints = {}
        
        for metric in metrics:
            # Group by status code
            status = metric.status_code
            status_codes[status] = status_codes.get(status, 0) + 1
            
            # Group by endpoint
            endpoint = metric.endpoint
            if endpoint not in endpoints:
                endpoints[endpoint] = {'count': 0, 'avg_time': 0, 'errors': 0}
            endpoints[endpoint]['count'] += 1
            if status >= 400:
                endpoints[endpoint]['errors'] += 1
        
        # Calculate averages
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        error_rate = sum(1 for m in metrics if m.status_code >= 400) / len(metrics) * 100
        
        # Calculate endpoint averages
        for endpoint_name in endpoints:
            endpoint_metrics = [m.response_time_ms for m in metrics if m.endpoint == endpoint_name]
            endpoints[endpoint_name]['avg_time'] = sum(endpoint_metrics) / len(endpoint_metrics)
        
        return success_response({
            'period_hours': hours,
            'total_requests': len(metrics),
            'avg_response_time_ms': round(avg_response_time, 2),
            'min_response_time_ms': min_response_time,
            'max_response_time_ms': max_response_time,
            'error_rate_percent': round(error_rate, 2),
            'status_codes': status_codes,
            'endpoints': endpoints
        })
    except Exception as e:
        return error_response(str(e), 500)


@bp.route('/performance/endpoint/<path:endpoint>', methods=['GET'])
def get_endpoint_performance(endpoint):
    """Get detailed performance metrics for a specific endpoint"""
    try:
        hours = request.args.get('hours', 24, type=int)
        since = datetime.utcnow() - timedelta(hours=hours)
        
        metrics = PerformanceMetric.query.filter(
            PerformanceMetric.endpoint == endpoint,
            PerformanceMetric.timestamp >= since
        ).all()
        
        if not metrics:
            return error_response('No metrics found for this endpoint', 404)
        
        response_times = [m.response_time_ms for m in metrics]
        
        return success_response({
            'endpoint': endpoint,
            'period_hours': hours,
            'total_calls': len(metrics),
            'avg_response_time_ms': round(sum(response_times) / len(response_times), 2),
            'min_response_time_ms': min(response_times),
            'max_response_time_ms': max(response_times),
            'p95_response_time_ms': sorted(response_times)[int(len(response_times) * 0.95)],
            'error_count': sum(1 for m in metrics if m.status_code >= 400),
            'success_count': sum(1 for m in metrics if m.status_code < 400)
        })
    except Exception as e:
        return error_response(str(e), 500)


@bp.route('/performance/slowest', methods=['GET'])
def get_slowest_requests():
    """Get the slowest API requests"""
    try:
        limit = request.args.get('limit', 20, type=int)
        hours = request.args.get('hours', 24, type=int)
        since = datetime.utcnow() - timedelta(hours=hours)
        
        slowest = PerformanceMetric.query.filter(
            PerformanceMetric.timestamp >= since
        ).order_by(
            PerformanceMetric.response_time_ms.desc()
        ).limit(limit).all()
        
        return success_response({
            'slowest_requests': [
                {
                    'endpoint': m.endpoint,
                    'method': m.method,
                    'response_time_ms': m.response_time_ms,
                    'status_code': m.status_code,
                    'timestamp': m.timestamp.isoformat()
                }
                for m in slowest
            ]
        })
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================================
# SYSTEM METRICS ENDPOINTS
# ============================================================================

@bp.route('/system/health', methods=['GET'])
def get_system_health():
    """Get current system health status"""
    try:
        # Get latest metrics for each type
        metrics = {}
        for metric_type in ['cpu', 'memory', 'disk', 'db_connections', 'error_rate']:
            latest = SystemMetric.query.filter_by(
                metric_type=metric_type
            ).order_by(SystemMetric.timestamp.desc()).first()
            
            if latest:
                metrics[metric_type] = {
                    'value': latest.value,
                    'unit': latest.unit,
                    'status': latest.status,
                    'timestamp': latest.timestamp.isoformat()
                }
        
        # Determine overall health
        critical_count = sum(1 for m in metrics.values() if m.get('status') == 'critical')
        warning_count = sum(1 for m in metrics.values() if m.get('status') == 'warning')
        
        overall_status = 'critical' if critical_count > 0 else ('warning' if warning_count > 0 else 'normal')
        
        return success_response({
            'overall_status': overall_status,
            'metrics': metrics
        })
    except Exception as e:
        return error_response(str(e), 500)


@bp.route('/system/history', methods=['GET'])
def get_system_metrics_history():
    """Get system metrics history"""
    try:
        metric_type = request.args.get('type', 'all')  # cpu, memory, disk, all
        hours = request.args.get('hours', 24, type=int)
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = SystemMetric.query.filter(SystemMetric.timestamp >= since)
        if metric_type != 'all':
            query = query.filter_by(metric_type=metric_type)
        
        metrics = query.order_by(SystemMetric.timestamp).all()
        
        # Group by type
        history = {}
        for metric in metrics:
            if metric.metric_type not in history:
                history[metric.metric_type] = []
            history[metric.metric_type].append({
                'value': metric.value,
                'status': metric.status,
                'timestamp': metric.timestamp.isoformat()
            })
        
        return success_response({
            'period_hours': hours,
            'metric_type': metric_type,
            'history': history
        })
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================================
# ALERTS ENDPOINTS
# ============================================================================

@bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get active and recent alerts"""
    try:
        days = request.args.get('days', 7, type=int)
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        since = datetime.utcnow() - timedelta(days=days)
        
        query = MonitoringAlert.query.filter(MonitoringAlert.created_at >= since)
        if active_only:
            query = query.filter_by(is_active=True)
        
        alerts = query.order_by(MonitoringAlert.created_at.desc()).all()
        
        return success_response({
            'total_alerts': len(alerts),
            'active_alerts': sum(1 for a in alerts if a.is_active),
            'alerts': [
                {
                    'id': a.id,
                    'alert_type': a.alert_type,
                    'severity': a.severity,
                    'message': a.message,
                    'metric_name': a.metric_name,
                    'metric_value': a.metric_value,
                    'is_active': a.is_active,
                    'created_at': a.created_at.isoformat(),
                    'resolved_at': a.resolved_at.isoformat() if a.resolved_at else None
                }
                for a in alerts
            ]
        })
    except Exception as e:
        return error_response(str(e), 500)


@bp.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@jwt_required()
def acknowledge_alert(alert_id):
    """Acknowledge an alert (mark as seen)"""
    try:
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        
        alert = MonitoringAlert.query.get(alert_id)
        if not alert:
            return error_response('Alert not found', 404)
        
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = user_id
        db.session.commit()
        
        return success_response({'message': 'Alert acknowledged'})
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_alert(alert_id):
    """Resolve an alert (mark as resolved)"""
    try:
        alert = MonitoringAlert.query.get(alert_id)
        if not alert:
            return error_response('Alert not found', 404)
        
        alert.is_active = False
        alert.resolved_at = datetime.utcnow()
        db.session.commit()
        
        return success_response({'message': 'Alert resolved'})
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


# ============================================================================
# ANALYTICS DASHBOARD ENDPOINTS
# ============================================================================

@bp.route('/dashboard/overview', methods=['GET'])
def get_dashboard_overview():
    """Get comprehensive monitoring dashboard data"""
    try:
        hours = request.args.get('hours', 24, type=int)
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Performance metrics
        perf_metrics = PerformanceMetric.query.filter(
            PerformanceMetric.timestamp >= since
        ).all()
        
        perf_data = {}
        if perf_metrics:
            response_times = [m.response_time_ms for m in perf_metrics]
            perf_data = {
                'total_requests': len(perf_metrics),
                'avg_response_time_ms': round(sum(response_times) / len(response_times), 2),
                'error_rate_percent': round(sum(1 for m in perf_metrics if m.status_code >= 400) / len(perf_metrics) * 100, 2)
            }
        
        # System health
        health_data = {}
        for metric_type in ['cpu', 'memory', 'disk']:
            latest = SystemMetric.query.filter_by(
                metric_type=metric_type
            ).order_by(SystemMetric.timestamp.desc()).first()
            if latest:
                health_data[metric_type] = {
                    'value': latest.value,
                    'status': latest.status
                }
        
        # Alerts
        active_alerts = MonitoringAlert.query.filter_by(is_active=True).count()
        
        return success_response({
            'timestamp': datetime.utcnow().isoformat(),
            'period_hours': hours,
            'performance': perf_data,
            'system_health': health_data,
            'active_alerts': active_alerts
        })
    except Exception as e:
        return error_response(str(e), 500)
