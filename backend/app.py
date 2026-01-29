#!/usr/bin/env python3
"""
Flask web application for AlongGPX.
Provides REST API endpoints for GPX processing.
"""

import os
import sys
import logging
import tempfile
import threading
import uuid
import re
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room

from cli.main import run_pipeline
from core.config import load_yaml_config, load_env_config, merge_env_into_config
from core.presets import load_presets
from core.gpx_processing import load_gpx_track

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app initialization
# Note: This module is now under backend/ instead of docker/
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['JSON_SORT_KEYS'] = False

# Initialize SocketIO (optional, graceful fallback to polling)
try:
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode="threading",
        ping_timeout=60,
        ping_interval=25,
        engineio_logger=False,
        logger=False,
        transports=['polling']  # Force polling only, disable WebSocket
    )
    SOCKETIO_ENABLED = True
    logger.info("SocketIO initialized for real-time updates (polling mode)")
except Exception as e:
    logger.warning(f"SocketIO initialization failed: {e}. Falling back to polling.")
    socketio = None
    SOCKETIO_ENABLED = False

ALLOWED_EXTENSIONS = {'gpx'}

# Job tracking system (thread-safe dict)
job_registry = {}
job_registry_lock = threading.Lock()

# Load cleanup settings from config.yaml (environment variables can override)
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
_cleanup_cfg = load_yaml_config(config_path).get('cleanup', {})
CLEANUP_INTERVAL_SECONDS = int(os.getenv('ALONGGPX_CLEANUP_INTERVAL_SECONDS', _cleanup_cfg.get('interval_seconds', 600)))
JOB_TTL_SECONDS = int(os.getenv('ALONGGPX_JOB_TTL_SECONDS', _cleanup_cfg.get('job_ttl_seconds', 3600)))
TEMP_FILE_MAX_AGE_SECONDS = int(os.getenv('ALONGGPX_TEMP_FILE_MAX_AGE_SECONDS', _cleanup_cfg.get('temp_file_max_age_seconds', 3600)))
OUTPUT_RETENTION_DAYS = int(os.getenv('ALONGGPX_OUTPUT_RETENTION_DAYS', _cleanup_cfg.get('output_retention_days', 30)))

UUID_GPX_RE = re.compile(r'^[0-9a-fA-F-]{36}\.gpx$')
UUID_OUTPUT_RE = re.compile(r'^[0-9a-fA-F-]{36}\.(xlsx|html)$')


def create_job(project_name: str):
    """Create a new job tracking entry."""
    job_id = str(uuid.uuid4())
    with job_registry_lock:
        job_registry[job_id] = {
            'id': job_id,
            'state': 'queued',  # queued, processing, completed, failed
            'percent': 0,
            'message': 'Queued for processing',
            'project_name': project_name,
            'created_at': datetime.now().isoformat(),
            'excel_file': None,
            'html_file': None,
            'temp_gpx_path': None,
            'rows_count': None,
            'track_length_km': None,
            'error': None,
            'geojson': None,
        }
    return job_id


def update_job(job_id: str, **kwargs):
    """Update job status."""
    with job_registry_lock:
        if job_id in job_registry:
            job_registry[job_id].update(kwargs)
            # Emit via SocketIO if available
            if SOCKETIO_ENABLED and socketio:
                try:
                    socketio.emit('job_progress', job_registry[job_id], to=job_id, skip_sid=True)
                except Exception as e:
                    logger.debug(f"SocketIO emit failed: {e}")  # Non-blocking


def get_job(job_id: str):
    """Get job status."""
    with job_registry_lock:
        return job_registry.get(job_id, None)


def _safe_remove(path: str):
    try:
        os.remove(path)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        logger.debug(f"Failed to remove file {path}: {e}")
        return False


def _cleanup_job_registry(now_ts: float):
    expired_ids = []
    with job_registry_lock:
        for job_id, job in job_registry.items():
            created_at = job.get('created_at')
            state = job.get('state')
            if not created_at or state not in ('completed', 'failed'):
                continue
            try:
                created_ts = datetime.fromisoformat(created_at).timestamp()
            except Exception:
                continue
            if now_ts - created_ts > JOB_TTL_SECONDS:
                expired_ids.append(job_id)

        for job_id in expired_ids:
            job_registry.pop(job_id, None)


def _cleanup_temp_uploads(now_ts: float):
    temp_dir = app.config.get('UPLOAD_FOLDER', tempfile.gettempdir())
    try:
        for name in os.listdir(temp_dir):
            if not UUID_GPX_RE.match(name):
                continue
            path = os.path.join(temp_dir, name)
            try:
                mtime = os.path.getmtime(path)
            except FileNotFoundError:
                continue
            if now_ts - mtime > TEMP_FILE_MAX_AGE_SECONDS:
                _safe_remove(path)
    except Exception as e:
        logger.debug(f"Temp cleanup failed: {e}")


def _cleanup_output_files(now_ts: float):
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
        cfg = load_yaml_config(config_path)
        env_cfg = load_env_config()
        cfg = merge_env_into_config(cfg, env_cfg)
        output_dir = os.path.abspath(cfg['project']['output_path'])
        max_age_seconds = OUTPUT_RETENTION_DAYS * 86400

        for name in os.listdir(output_dir):
            if not UUID_OUTPUT_RE.match(name):
                continue
            path = os.path.join(output_dir, name)
            try:
                mtime = os.path.getmtime(path)
            except FileNotFoundError:
                continue
            if now_ts - mtime > max_age_seconds:
                _safe_remove(path)
    except Exception as e:
        logger.debug(f"Output cleanup failed: {e}")


def _cleanup_loop():
    while True:
        time.sleep(CLEANUP_INTERVAL_SECONDS)
        now_ts = time.time()
        _cleanup_job_registry(now_ts)
        _cleanup_temp_uploads(now_ts)
        _cleanup_output_files(now_ts)


# Start background cleanup loop
cleanup_thread = threading.Thread(target=_cleanup_loop, daemon=True)
cleanup_thread.start()


def process_gpx_async(job_id: str, config: dict, temp_gpx_path: str, form_presets, form_includes, form_excludes):
    """Run pipeline in background thread."""
    def on_progress(percent: float, message: str):
        update_job(job_id, state='processing', percent=int(percent), message=message)

    try:
        # Generate UUIDs for output files (ensures unique names on disk)
        excel_uuid = f"{uuid.uuid4()}.xlsx"
        html_uuid = f"{uuid.uuid4()}.html"
        
        track_points = load_gpx_track(temp_gpx_path)
        update_job(job_id, state='processing', percent=5, message='Starting pipeline...')
        result = run_pipeline(
            config,
            cli_presets=form_presets,
            cli_include=form_includes,
            cli_exclude=form_excludes,
            progress_callback=on_progress,
            excel_filename=excel_uuid,
            html_filename=html_uuid,
        )
        geojson = build_geojson(track_points, result.get('dataframe'))
        try:
            os.remove(temp_gpx_path)
        except Exception as e:
            logger.warning(f"Could not delete temp GPX: {e}")
        update_job(
            job_id,
            state='completed',
            percent=100,
            message='Processing complete',
            excel_file=excel_uuid,
            html_file=html_uuid,
            rows_count=result['rows_count'],
            track_length_km=result['track_length_km'],
            geojson=geojson,
        )
    except Exception as e:
        logger.error(f"Processing failed for job {job_id}: {e}", exc_info=True)
        update_job(
            job_id,
            state='failed',
            percent=0,
            message='Processing failed',
            error=str(e),
        )


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def build_geojson(track_points, df):
    features = []
    if track_points:
        features.append(
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [(float(lon), float(lat)) for lon, lat in track_points],
                },
                'properties': {'featureType': 'track'},
            }
        )

    if df is not None:
        try:
            for _, row in df.iterrows():
                lon = float(row.get('lon'))
                lat = float(row.get('lat'))
                features.append(
                    {
                        'type': 'Feature',
                        'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
                        'properties': {
                            'featureType': 'poi',
                            'id': row.get('Name') or '',
                            'name': row.get('Name') or 'Unnamed',
                            'matching_filter': row.get('Matching Filter', ''),
                            'kilometers_from_start': row.get('Kilometers from start', 0),
                            'distance_km': row.get('Distance from track (km)', 0),
                            'website': row.get('Website', ''),
                            'phone': row.get('Phone', ''),
                            'opening_hours': row.get('Opening hours', ''),
                            'tags': row.get('OSM Tags', ''),
                        },
                    }
                )
        except Exception as e:
            logger.warning(f"Failed to convert dataframe to GeoJSON: {e}")

    return {'type': 'FeatureCollection', 'features': features}


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'AlongGPX'}), 200


@app.route('/api/config', methods=['GET'])
def get_config():
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
        config = load_yaml_config(config_path)
        env_cfg = load_env_config()
        config = merge_env_into_config(config, env_cfg)
        presets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'presets.yaml')
        presets = load_presets(presets_path)
        return jsonify({
            'defaults': {
                'project_name': config['project']['name'],
                'radius_km': config['search']['radius_km'],
                'step_km': config['search']['step_km'],
                'include': config['search'].get('include', []),
                'exclude': config['search'].get('exclude', []),
            },
            'presets': list(presets.keys()),
            'presets_detail': {name: p for name, p in presets.items()},
            'marker_color_palette': config.get('map', {}).get('marker_color_palette', []),
            'default_marker_color': config.get('map', {}).get('default_marker_color', 'gray'),
        }), 200
    except Exception as e:
        logger.error(f"Config fetch failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id: str):
    try:
        job = get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        return jsonify(job), 200
    except Exception as e:
        logger.error(f"Status fetch failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/process', methods=['POST'])
def process_gpx():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only .gpx files allowed'}), 400
        # Use UUID to ensure unique temp filename (avoid collisions)
        temp_filename = f"{uuid.uuid4()}.gpx"
        temp_gpx_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        file.save(temp_gpx_path)
        logger.info(f"Processing GPX: {temp_gpx_path}")
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
        config = load_yaml_config(config_path)
        env_cfg = load_env_config()
        config = merge_env_into_config(config, env_cfg)
        # Ensure optional search filters exist even if omitted in YAML
        config.setdefault('search', {})
        config['search'].setdefault('include', [])
        config['search'].setdefault('exclude', [])
        if 'project_name' in request.form:
            config['project']['name'] = request.form['project_name']
        else:
            config['project']['name'] = os.path.splitext(filename)[0]
        if 'radius_km' in request.form:
            config['search']['radius_km'] = float(request.form['radius_km'])
        if 'step_km' in request.form:
            config['search']['step_km'] = float(request.form['step_km'])
        form_presets = request.form.getlist('preset') if 'preset' in request.form else None
        form_includes = request.form.getlist('include') if 'include' in request.form else None
        form_excludes = request.form.getlist('exclude') if 'exclude' in request.form else None
        if config['search']['step_km'] is None:
            config['search']['step_km'] = config['search']['radius_km'] * 0.6
        config['input']['gpx_file'] = temp_gpx_path
        os.makedirs(config['project']['output_path'], exist_ok=True)
        job_id = create_job(config['project']['name'])
        update_job(job_id, temp_gpx_path=temp_gpx_path)
        thread = threading.Thread(
            target=process_gpx_async,
            args=(job_id, config, temp_gpx_path, form_presets, form_includes, form_excludes),
            daemon=True,
        )
        thread.start()
        return jsonify({'job_id': job_id, 'status_url': f'/api/status/{job_id}'}), 202
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/excel/<job_id>', methods=['GET'])
def download_excel(job_id):
    try:
        job = get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        excel_uuid = job.get('excel_file')
        if not excel_uuid:
            return jsonify({'error': 'Excel file not available'}), 404
        
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
        cfg = load_yaml_config(config_path)
        env_cfg = load_env_config()
        cfg = merge_env_into_config(cfg, env_cfg)
        output_dir = os.path.abspath(cfg['project']['output_path'])
        file_path = os.path.join(output_dir, secure_filename(excel_uuid))
        logger.info(f"Download Excel requested for job {job_id}: {file_path}")
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Download with clean project name
        project_name = job.get('project_name', 'download')
        clean_download_name = f"{project_name}.xlsx"
        return send_file(file_path, as_attachment=True, download_name=clean_download_name)
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/html/<job_id>', methods=['GET'])
def download_html(job_id):
    try:
        job = get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        html_uuid = job.get('html_file')
        if not html_uuid:
            return jsonify({'error': 'HTML file not available'}), 404
        
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
        cfg = load_yaml_config(config_path)
        env_cfg = load_env_config()
        cfg = merge_env_into_config(cfg, env_cfg)
        output_dir = os.path.abspath(cfg['project']['output_path'])
        file_path = os.path.join(output_dir, secure_filename(html_uuid))
        logger.info(f"Download HTML requested for job {job_id}: {file_path}")
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Download with clean project name
        project_name = job.get('project_name', 'download')
        clean_download_name = f"{project_name}.html"
        return send_file(file_path, as_attachment=False, download_name=clean_download_name)
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/job/<job_id>/geojson', methods=['GET'])
def get_geojson(job_id: str):
    job = get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    if not job.get('geojson'):
        return jsonify({'error': 'GeoJSON not available yet'}), 404
    return jsonify(job['geojson'])


if SOCKETIO_ENABLED and socketio:
    @socketio.on('connect')
    def handle_connect():
        logger.info(f"Client connected: {request.sid}")
        emit('connected', {'ok': True})

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f"Client disconnected: {request.sid}")

    @socketio.on('subscribe_job')
    def handle_subscribe(data):
        job_id = data.get('job_id') if isinstance(data, dict) else None
        if not job_id:
            emit('error', {'message': 'No job_id provided'})
            return
        try:
            join_room(job_id)
            logger.info(f"Client {request.sid} subscribed to job {job_id}")
            job = get_job(job_id)
            if job:
                emit('job_progress', job)
        except Exception as e:
            logger.error(f"Subscribe error: {e}", exc_info=True)
            emit('error', {'message': str(e)})


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large (max 50MB)'}), 413


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    logger.info(f"Starting Flask server on 0.0.0.0:{port} (debug={debug}, socketio={SOCKETIO_ENABLED})")
    try:
        if SOCKETIO_ENABLED and socketio:
            socketio.run(
                app,
                host='0.0.0.0',
                port=port,
                debug=debug,
                use_reloader=False,
                allow_unsafe_werkzeug=True
            )
        else:
            # Run without SocketIO (polling only)
            app.run(
                host='0.0.0.0',
                port=port,
                debug=debug,
                use_reloader=False
            )
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
