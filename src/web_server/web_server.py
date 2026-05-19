"""
Web Server Module
Flask-based REST API and WebSocket for real-time updates
"""

import json
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import logging

from ..core.configuration import CONFIG, LOGGER
from ..database import DATABASE_CONNECTION, FileDAO, TypeDAO, FunctionDAO, CallDAO, ReferenceDAO
from ..llm_service import get_llm_service

app = Flask(__name__, static_folder='../web/static', template_folder='../web/templates')
app.config['SECRET_KEY'] = 'code-knowledge-graph-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

WEB_INSTANCE: Optional['WebServer'] = None


class WebServer:
    """
    Web server providing REST API and WebSocket for real-time updates
    """
    
    def __init__(self):
        self.app = app
        self.socketio = socketio
        self._event_handlers: Dict[str, List[callable]] = {
            'file_created': [],
            'file_updated': [],
            'file_deleted': [],
            'sync_complete': []
        }
        
        global WEB_INSTANCE
        WEB_INSTANCE = self
        
        self._setup_routes()
        self._setup_socketio()
    
    def _setup_routes(self) -> None:
        """Setup Flask routes"""
        
        @app.route('/')
        def index():
            """Serve main dashboard"""
            return send_from_directory('../web/templates', 'index.html')
        
        @app.route('/api/stats')
        def get_stats():
            """Get knowledge graph statistics"""
            stats = DATABASE_CONNECTION.get_database_stats()
            return jsonify({
                'success': True,
                'data': stats
            })
        
        @app.route('/api/files')
        def get_files():
            """Get all files"""
            files = FileDAO.get_all()
            return jsonify({
                'success': True,
                'data': files
            })
        
        @app.route('/api/files/<int:file_id>')
        def get_file(file_id):
            """Get single file details"""
            file_info = FileDAO.get_by_id(file_id)
            if not file_info:
                return jsonify({'success': False, 'error': 'File not found'}), 404
            
            types = TypeDAO.get_by_file(file_id)
            functions = FunctionDAO.get_by_file(file_id)
            
            return jsonify({
                'success': True,
                'data': {
                    'file': file_info,
                    'types': types,
                    'functions': functions
                }
            })
        
        @app.route('/api/types')
        def get_types():
            """Get all types"""
            types = TypeDAO.get_all()
            return jsonify({
                'success': True,
                'data': types
            })
        
        @app.route('/api/types/<int:type_id>')
        def get_type(type_id):
            """Get single type details"""
            with DATABASE_CONNECTION.get_cursor() as cursor:
                cursor.execute("""
                    SELECT t.*, f.path as file_path
                    FROM types t
                    JOIN files f ON t.file_id = f.id
                    WHERE t.id = ?
                """, (type_id,))
                type_info = cursor.fetchone()
            
            if not type_info:
                return jsonify({'success': False, 'error': 'Type not found'}), 404
            
            type_dict = dict(type_info)
            references = ReferenceDAO.get_by_type(type_id)
            
            return jsonify({
                'success': True,
                'data': {
                    'type': type_dict,
                    'references': references
                }
            })
        
        @app.route('/api/functions')
        def get_functions():
            """Get all functions"""
            functions = FunctionDAO.get_all()
            return jsonify({
                'success': True,
                'data': functions
            })
        
        @app.route('/api/functions/<int:function_id>')
        def get_function(function_id):
            """Get single function details"""
            with DATABASE_CONNECTION.get_cursor() as cursor:
                cursor.execute("""
                    SELECT f.*, t.name as type_name, fi.path as file_path
                    FROM functions f
                    LEFT JOIN types t ON f.type_id = t.id
                    JOIN files fi ON f.file_id = fi.id
                    WHERE f.id = ?
                """, (function_id,))
                func_info = cursor.fetchone()
            
            if not func_info:
                return jsonify({'success': False, 'error': 'Function not found'}), 404
            
            func_dict = dict(func_info)
            callers = CallDAO.get_callers(function_id)
            callees = CallDAO.get_callees(function_id)
            
            return jsonify({
                'success': True,
                'data': {
                    'function': func_dict,
                    'callers': callers,
                    'callees': callees
                }
            })
        
        @app.route('/api/graph/full')
        def get_full_graph():
            """Get full knowledge graph for visualization"""
            files = FileDAO.get_all()
            types = TypeDAO.get_all()
            functions = FunctionDAO.get_all()
            
            nodes = []
            edges = []
            
            for f in files:
                nodes.append({
                    'id': f'id_f_{f["id"]}',
                    'label': Path(f['path']).name,
                    'type': 'file',
                    'data': f
                })
            
            type_id_map = {}
            for t in types:
                node_id = f'id_t_{t["id"]}'
                type_id_map[t['id']] = node_id
                nodes.append({
                    'id': node_id,
                    'label': t['name'],
                    'type': t['kind'],
                    'data': t
                })
                edges.append({
                    'source': node_id,
                    'target': f'id_f_{t["file_id"]}',
                    'relation': 'defined_in'
                })
            
            func_id_map = {}
            for fn in functions:
                node_id = f'id_fn_{fn["id"]}'
                func_id_map[fn['id']] = node_id
                nodes.append({
                    'id': node_id,
                    'label': fn['name'],
                    'type': 'function',
                    'data': fn
                })
                
                target = f'id_t_{fn["type_id"]}' if fn.get('type_id') else f'id_f_{fn["file_id"]}'
                edges.append({
                    'source': node_id,
                    'target': target,
                    'relation': 'defined_in'
                })
            
            with DATABASE_CONNECTION.get_cursor() as cursor:
                cursor.execute("SELECT * FROM calls")
                for row in cursor.fetchall():
                    caller = f'id_fn_{row["caller_id"]}'
                    callee = f'id_fn_{row["callee_id"]}'
                    if caller in func_id_map.values() and callee in func_id_map.values():
                        edges.append({
                            'source': caller,
                            'target': callee,
                            'relation': 'calls'
                        })
            
            return jsonify({
                'success': True,
                'data': {
                    'nodes': nodes,
                    'edges': edges
                }
            })
        
        @app.route('/api/graph/call-hierarchy/<int:function_id>')
        def get_call_hierarchy(function_id):
            """Get call hierarchy for a function"""
            visited = set()
            nodes = []
            edges = []
            
            def traverse(func_id, depth=0):
                if func_id in visited or depth > 10:
                    return
                visited.add(func_id)
                
                with DATABASE_CONNECTION.get_cursor() as cursor:
                    cursor.execute("""
                        SELECT f.*, fi.path
                        FROM functions f
                        JOIN files fi ON f.file_id = fi.id
                        WHERE f.id = ?
                    """, (func_id,))
                    func = cursor.fetchone()
                
                if func:
                    nodes.append({
                        'id': f'id_fn_{func_id}',
                        'label': dict(func)['name'],
                        'depth': depth,
                        'data': dict(func)
                    })
                    
                    callers = CallDAO.get_callers(func_id)
                    callees = CallDAO.get_callees(func_id)
                    
                    for caller in callers:
                        edges.append({
                            'source': f'id_fn_{caller["id"]}',
                            'target': f'id_fn_{func_id}',
                            'relation': 'calls'
                        })
                        traverse(caller['id'], depth - 1)
                    
                    for callee in callees:
                        edges.append({
                            'source': f'id_fn_{func_id}',
                            'target': f'id_fn_{callee["id"]}',
                            'relation': 'calls'
                        })
                        traverse(callee['id'], depth + 1)
            
            traverse(function_id)
            
            return jsonify({
                'success': True,
                'data': {
                    'nodes': nodes,
                    'edges': edges
                }
            })
        
        @app.route('/api/search')
        def search():
            """Search across all entities"""
            query = request.args.get('q', '').lower()
            if not query:
                return jsonify({'success': True, 'data': []})
            
            results = []
            
            for t in TypeDAO.get_all():
                if query in t['name'].lower():
                    results.append({
                        'type': 'type',
                        'id': t['id'],
                        'name': t['name'],
                        'kind': t['kind'],
                        'file_id': t['file_id']
                    })
            
            for f in FunctionDAO.get_all():
                if query in f['name'].lower():
                    results.append({
                        'type': 'function',
                        'id': f['id'],
                        'name': f['name'],
                        'file_id': f['file_id']
                    })
            
            for fi in FileDAO.get_all():
                if query in fi['path'].lower():
                    results.append({
                        'type': 'file',
                        'id': fi['id'],
                        'name': Path(fi['path']).name,
                        'path': fi['path']
                    })
            
            return jsonify({
                'success': True,
                'data': results[:50]
            })
        
        @app.route('/api/analyze/code', methods=['POST'])
        def analyze_code():
            """Analyze code using LLM"""
            data = request.json
            code = data.get('code', '')
            language = data.get('language', 'unknown')
            analysis_type = data.get('type', 'general')
            
            llm = get_llm_service()
            if not llm:
                return jsonify({
                    'success': False,
                    'error': 'LLM service not available'
                }), 503
            
            result = llm.analyze_code(code, language, analysis_type)
            
            if result.error:
                return jsonify({
                    'success': False,
                    'error': result.error
                }), 500
            
            return jsonify({
                'success': True,
                'data': {
                    'analysis': result.content,
                    'model': result.model
                }
            })
        
        @app.route('/api/llm/query', methods=['POST'])
        def llm_query():
            """Query knowledge graph using LLM"""
            data = request.json
            question = data.get('question', '')
            
            llm = get_llm_service()
            if not llm:
                return jsonify({
                    'success': False,
                    'error': 'LLM service not available'
                }), 503
            
            with DATABASE_CONNECTION.get_cursor() as cursor:
                cursor.execute("""
                    SELECT 'type' as entity_type, name, kind, path
                    FROM types t JOIN files f ON t.file_id = f.id
                    UNION ALL
                    SELECT 'function', fn.name, 'function', f.path
                    FROM functions fn JOIN files f ON fn.file_id = f.id
                    LIMIT 100
                """)
                context_rows = cursor.fetchall()
            
            context = "\n".join([
                f"{r['entity_type']}: {r['name']} ({r.get('kind', 'function')}) in {r['path']}"
                for r in context_rows
            ])
            
            result = llm.query_knowledge_graph(question, context)
            
            return jsonify({
                'success': True,
                'data': {
                    'answer': result.content,
                    'model': result.model
                }
            })
        
        @app.route('/api/diagrams/architecture')
        def get_architecture_diagram():
            """Get system architecture diagram data"""
            return jsonify({
                'success': True,
                'data': {
                    'title': 'Code Knowledge Graph System Architecture',
                    'type': 'architecture',
                    'nodes': [
                        {'id': 'file_monitor', 'label': 'File Monitor', 'layer': 1},
                        {'id': 'debounce_queue', 'label': 'Debounce Queue', 'layer': 2},
                        {'id': 'update_engine', 'label': 'Update Engine', 'layer': 3},
                        {'id': 'database', 'label': 'SQLite Database', 'layer': 4},
                        {'id': 'parsers', 'label': 'Parser Interface', 'layer': 3},
                        {'id': 'llm_service', 'label': 'LLM Service', 'layer': 3},
                        {'id': 'web_server', 'label': 'Web Server', 'layer': 4}
                    ],
                    'edges': [
                        {'source': 'file_monitor', 'target': 'debounce_queue'},
                        {'source': 'debounce_queue', 'target': 'update_engine'},
                        {'source': 'update_engine', 'target': 'database'},
                        {'source': 'parsers', 'target': 'update_engine'},
                        {'source': 'update_engine', 'target': 'llm_service'},
                        {'source': 'web_server', 'target': 'database'}
                    ]
                }
            })
        
        @app.route('/api/diagrams/flow')
        def get_flow_diagram():
            """Get system flow diagram data"""
            return jsonify({
                'success': True,
                'data': {
                    'title': 'Code Processing Flow',
                    'type': 'flow',
                    'nodes': [
                        {'id': 'start', 'label': 'File Change', 'type': 'start'},
                        {'id': 'detect', 'label': 'Detect Event', 'type': 'process'},
                        {'id': 'debounce', 'label': 'Debounce', 'type': 'process'},
                        {'id': 'parse', 'label': 'Parse File', 'type': 'process'},
                        {'id': 'delete', 'label': 'Delete Old', 'type': 'decision'},
                        {'id': 'insert', 'label': 'Insert New', 'type': 'process'},
                        {'id': 'notify', 'label': 'Notify Clients', 'type': 'process'},
                        {'id': 'end', 'label': 'Complete', 'type': 'end'}
                    ],
                    'edges': [
                        {'source': 'start', 'target': 'detect'},
                        {'source': 'detect', 'target': 'debounce'},
                        {'source': 'debounce', 'target': 'parse'},
                        {'source': 'parse', 'target': 'delete'},
                        {'source': 'delete', 'target': 'insert', 'label': 'Yes'},
                        {'source': 'delete', 'target': 'end', 'label': 'No'},
                        {'source': 'insert', 'target': 'notify'},
                        {'source': 'notify', 'target': 'end'}
                    ]
                }
            })
        
        @app.route('/api/diagrams/sequence')
        def get_sequence_diagram():
            """Get component interaction sequence diagram"""
            return jsonify({
                'success': True,
                'data': {
                    'title': 'File Update Sequence',
                    'type': 'sequence',
                    'actors': [
                        'FileSystem',
                        'FileMonitor',
                        'UpdateEngine',
                        'Parser',
                        'Database',
                        'WebSocket'
                    ],
                    'steps': [
                        {'from': 'FileSystem', 'to': 'FileMonitor', 'message': 'File Changed'},
                        {'from': 'FileMonitor', 'to': 'UpdateEngine', 'message': 'Event'},
                        {'from': 'UpdateEngine', 'to': 'Parser', 'message': 'Parse File'},
                        {'from': 'Parser', 'to': 'UpdateEngine', 'message': 'Parse Result'},
                        {'from': 'UpdateEngine', 'to': 'Database', 'message': 'Delete Old'},
                        {'from': 'UpdateEngine', 'to': 'Database', 'message': 'Insert New'},
                        {'from': 'UpdateEngine', 'to': 'WebSocket', 'message': 'Emit Update'},
                        {'from': 'WebSocket', 'to': 'WebSocket', 'message': 'Broadcast'}
                    ]
                }
            })
    
    def _setup_socketio(self) -> None:
        """Setup SocketIO event handlers"""
        
        @socketio.on('connect')
        def handle_connect():
            LOGGER.info('Client connected')
            emit('connected', {'status': 'connected'})
        
        @socketio.on('disconnect')
        def handle_disconnect():
            LOGGER.info('Client disconnected')
        
        @socketio.on('subscribe')
        def handle_subscribe(data):
            LOGGER.info(f'Client subscribed: {data}')
            emit('subscribed', {'status': 'subscribed'})
        
        @socketio.on('request_update')
        def handle_request_update():
            stats = DATABASE_CONNECTION.get_database_stats()
            emit('stats_update', stats)
    
    def emit_update(self, event_type: str, data: Any) -> None:
        """Emit update to all connected clients"""
        self.socketio.emit(event_type, data)
        LOGGER.debug(f"Emitted {event_type} update")
    
    def emit_stats_update(self) -> None:
        """Emit statistics update"""
        stats = DATABASE_CONNECTION.get_database_stats()
        self.emit_update('stats_update', stats)
    
    def register_event_handler(self, event_type: str, handler: callable) -> None:
        """Register event handler"""
        if event_type in self._event_handlers:
            self._event_handlers[event_type].append(handler)
    
    def run(self, host: str = CONFIG.web_server_host, port: int = CONFIG.web_server_port) -> None:
        """Run the web server"""
        LOGGER.info(f"Starting web server at http://{host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)


def create_web_server() -> WebServer:
    """Factory function to create web server"""
    return WebServer()


def get_web_server() -> Optional[WebServer]:
    """Get global web server instance"""
    return WEB_INSTANCE
