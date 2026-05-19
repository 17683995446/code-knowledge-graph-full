#!/usr/bin/env python3
"""
真实长时间压力测试 - 完整的系统稳定性验证
模拟真实的软件开发环境，包括多种语言、大量代码变更、持续运行
"""
import sys
import time
import tempfile
import random
import math
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from src.core.configuration import LOGGER
from src.database import DATABASE_CONNECTION
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def create_project_structure(base_dir: Path):
    """创建真实的项目结构"""
    # Python 应用
    python_app = base_dir / "python_app"
    (python_app / "api").mkdir(parents=True)
    (python_app / "models").mkdir(parents=True)
    (python_app / "services").mkdir(parents=True)
    (python_app / "utils").mkdir(parents=True)
    (python_app / "tests").mkdir(parents=True)
    
    # JavaScript/Node应用
    js_app = base_dir / "js_app"
    (js_app / "src" / "components").mkdir(parents=True)
    (js_app / "src" / "services").mkdir(parents=True)
    (js_app / "src" / "utils").mkdir(parents=True)
    
    # Go 应用
    go_app = base_dir / "go_app"
    (go_app / "internal" / "api").mkdir(parents=True)
    (go_app / "internal" / "models").mkdir(parents=True)
    (go_app / "internal" / "services").mkdir(parents=True)
    
    return {
        "python_app": python_app,
        "js_app": js_app, 
        "go_app": go_app
    }


def create_python_project(project_dir: Path, num_modules: int = 20):
    """创建复杂的Python项目"""
    files = []
    
    # 创建应用主文件
    main_file = project_dir / "main.py"
    main_content = '''#!/usr/bin/env python3
"""Python App - Main Application"""
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from api.routes import api_router
from models.user import User
from services.user_service import UserService
from utils.helpers import format_timestamp

def main():
    """Main entry point"""
    logger.info(f"Starting application at {format_timestamp()}")
    
    user_service = UserService()
    
    # 创建一些测试数据
    for i in range(10):
        user = User(username=f"user_{i}", email=f"user_{i}@example.com")
        user_service.create(user)
    
    logger.info("Application initialized successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    main_file.write_text(main_content)
    files.append(main_file)
    
    # 创建模型
    model_file = project_dir / "models" / "user.py"
    model_content = '''from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class User:
    """User model"""
    username: str
    email: str
    id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    is_active: bool = True
    roles: List[str] = field(default_factory=lambda: ["user"])
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "roles": self.roles,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
'''
    model_file.write_text(model_content)
    files.append(model_file)
    
    # 创建服务
    service_file = project_dir / "services" / "user_service.py"
    service_content = '''from typing import List, Optional, Dict
from models.user import User
from utils.logger import get_logger

logger = get_logger(__name__)

class UserService:
    """Service for user management"""
    
    def __init__(self):
        self._users: Dict[int, User] = {}
        self._next_id = 1
    
    def create(self, user: User) -> User:
        """Create a new user"""
        user.id = self._next_id
        self._users[user.id] = user
        self._next_id += 1
        logger.info(f"Created user: {user.username}")
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self._users.get(user_id)
    
    def get_all(self) -> List[User]:
        """Get all users"""
        return list(self._users.values())
    
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user"""
        user = self._users.get(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            logger.info(f"Updated user: {user_id}")
        return user
    
    def delete(self, user_id: int) -> bool:
        """Delete user"""
        if user_id in self._users:
            del self._users[user_id]
            logger.info(f"Deleted user: {user_id}")
            return True
        return False
'''
    service_file.write_text(service_content)
    files.append(service_file)
    
    # 创建API路由
    api_file = project_dir / "api" / "routes.py"
    api_content = '''"""API routes module"""
from typing import List
from models.user import User

def api_router():
    """Dummy router for demonstration"""
    pass

def get_all_users() -> List[User]:
    """Get all users"""
    return []
'''
    api_file.write_text(api_content)
    files.append(api_file)
    
    # 创建工具文件
    util1 = project_dir / "utils" / "helpers.py"
    util1_content = '''from datetime import datetime

def format_timestamp(dt=None):
    """Format timestamp as string"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_currency(amount: float, currency: str = "$") -> str:
    """Format number as currency"""
    return f"{currency}{amount:,.2f}"
'''
    util1.write_text(util1_content)
    files.append(util1)
    
    util2 = project_dir / "utils" / "logger.py"
    util2_content = '''import logging
import sys

def get_logger(name: str):
    """Get configured logger"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
'''
    util2.write_text(util2_content)
    files.append(util2)
    
    # 创建__init__.py文件
    for dir_name in ["api", "models", "services", "utils", "tests"]:
        init_file = project_dir / dir_name / "__init__.py"
        init_file.write_text(f'"""Package: {dir_name}"""')
        files.append(init_file)
    
    # 创建多个模块
    for i in range(num_modules):
        module_file = project_dir / "services" / f"module_{i}.py"
        module_content = f'''"""Module {i} - Complex functionality"""
from utils.helpers import format_timestamp
from utils.logger import get_logger

logger = get_logger(__name__)

def process_data_{i}(data):
    """Process data"""
    logger.info(f"Processing data in module {i}")
    return data

def calculate_{i}(a, b):
    """Perform calculation"""
    return a + b + {i}
'''
        module_file.write_text(module_content)
        files.append(module_file)
    
    return files


def create_js_project(project_dir: Path, num_components: int = 15):
    """创建复杂的JavaScript/Node项目"""
    files = []
    
    package_json = project_dir / "package.json"
    package_content = '''{
  "name": "js-app",
  "version": "1.0.0",
  "description": "JavaScript Application",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "build": "echo 'Building...'",
    "test": "echo 'Testing...'"
  },
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "^4.17.0"
  }
}
'''
    package_json.write_text(package_content)
    files.append(package_json)
    
    # 主文件
    index_file = project_dir / "src" / "index.js"
    index_content = '''/**
 * Main application entry point
 */
const express = require('express');
const path = require('path');
const logger = require('./utils/logger');
const UserService = require('./services/userService');

const app = express();
const PORT = 3000;

// Initialize services
const userService = new UserService();

app.get('/', (req, res) => {
  logger.info('Received request to root');
  res.json({
    name: 'JS App',
    version: '1.0.0',
    status: 'running'
  });
});

app.get('/api/users', (req, res) => {
  res.json(userService.getAllUsers());
});

app.listen(PORT, () => {
  logger.info(`Server listening on port ${PORT}`);
});

module.exports = app;
'''
    index_file.write_text(index_content)
    files.append(index_file)
    
    # 服务
    service_file = project_dir / "src" / "services" / "userService.js"
    service_content = '''const logger = require('../utils/logger');

class UserService {
  constructor() {
    this.users = new Map();
    this.nextId = 1;
  }

  createUser(data) {
    const user = {
      id: this.nextId++,
      username: data.username,
      email: data.email,
      isActive: true,
      createdAt: new Date().toISOString()
    };
    this.users.set(user.id, user);
    logger.info(`Created user: ${user.username}`);
    return user;
  }

  getAllUsers() {
    return Array.from(this.users.values());
  }

  getUserById(id) {
    return this.users.get(Number(id));
  }
}

module.exports = UserService;
'''
    service_file.write_text(service_content)
    files.append(service_file)
    
    # 工具
    util_file = project_dir / "src" / "utils" / "logger.js"
    util_content = '''const timestamp = () => new Date().toISOString();

const log = (level, message) => {
  console.log(`[${timestamp()}] [${level}] ${message}`);
};

module.exports = {
  info: (msg) => log('INFO', msg),
  warn: (msg) => log('WARN', msg),
  error: (msg) => log('ERROR', msg),
  debug: (msg) => log('DEBUG', msg)
};
'''
    util_file.write_text(util_content)
    files.append(util_file)
    
    # 多个组件
    for i in range(num_components):
        component_file = project_dir / "src" / "components" / f"component_{i}.jsx"
        component_content = f'''/**
 * Component {i} - React-like component
 */
import {{ useState, useEffect }} from 'react';

const Component{i} = ({{ title }}) => {{
  const [count, setCount] = useState(0);
  
  useEffect(() => {{
    console.log('Component{i} mounted');
  }}, []);
  
  return (
    <div className="component-{i}">
      <h2>{{title}}</h2>
      <p>Count: {{count}}</p>
      <button onClick={{() => setCount(count + 1)}}>
        Increment
      </button>
    </div>
  );
}};

export default Component{i};
'''
        component_file.write_text(component_content)
        files.append(component_file)
    
    return files


def create_go_project(project_dir: Path, num_modules: int = 10):
    """创建复杂的Go项目"""
    files = []
    
    # go.mod
    mod_file = project_dir / "go.mod"
    mod_content = '''module go-app

go 1.21
'''
    mod_file.write_text(mod_content)
    files.append(mod_file)
    
    # 主程序
    main_file = project_dir / "main.go"
    main_content = '''package main

import (
	"fmt"
	"log"
	"net/http"
	
	"go-app/internal/api"
	"go-app/internal/services"
)

func main() {
	fmt.Println("Go Application Starting...")
	
	// Initialize services
	userService := services.NewUserService()
	
	// Setup routes
	apiRouter := api.NewRouter(userService)
	
	// Start server
	fmt.Println("Server listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", apiRouter))
}
'''
    main_file.write_text(main_content)
    files.append(main_file)
    
    # API
    api_file = project_dir / "internal" / "api" / "router.go"
    api_content = '''package api

import (
	"encoding/json"
	"net/http"
	
	"go-app/internal/services"
)

type Router struct {
	userService *services.UserService
}

func NewRouter(userService *services.UserService) *Router {
	return &Router{userService: userService}
}

func (r *Router) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	switch req.URL.Path {
	case "/":
		r.handleRoot(w, req)
	case "/api/users":
		r.handleUsers(w, req)
	default:
		http.NotFound(w, req)
	}
}

func (r *Router) handleRoot(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"name":    "Go App",
		"version": "1.0.0",
		"status":  "running",
	})
}

func (r *Router) handleUsers(w http.ResponseWriter, req *http.Request) {
	users := r.userService.GetAll()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(users)
}
'''
    api_file.write_text(api_content)
    files.append(api_file)
    
    # 模型
    model_file = project_dir / "internal" / "models" / "user.go"
    model_content = '''package models

import "time"

type User struct {
	ID        int       `json:"id"`
	Username  string    `json:"username"`
	Email     string    `json:"email"`
	IsActive  bool      `json:"isActive"`
	CreatedAt time.Time `json:"createdAt"`
}
'''
    model_file.write_text(model_content)
    files.append(model_file)
    
    # 服务
    service_file = project_dir / "internal" / "services" / "user_service.go"
    service_content = '''package services

import (
	"fmt"
	"sync"
	"time"
	
	"go-app/internal/models"
)

type UserService struct {
	users  map[int]*models.User
	nextID int
	mu     sync.RWMutex
}

func NewUserService() *UserService {
	return &UserService{
		users:  make(map[int]*models.User),
		nextID: 1,
	}
}

func (s *UserService) Create(username, email string) *models.User {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	user := &models.User{
		ID:        s.nextID,
		Username:  username,
		Email:     email,
		IsActive:  true,
		CreatedAt: time.Now(),
	}
	s.users[s.nextID] = user
	s.nextID++
	fmt.Printf("Created user: %s\\n", username)
	return user
}

func (s *UserService) GetAll() []*models.User {
	s.mu.RLock()
	defer s.mu.RUnlock()
	
	users := make([]*models.User, 0, len(s.users))
	for _, user := range s.users {
		users = append(users, user)
	}
	return users
}

func (s *UserService) GetByID(id int) *models.User {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return s.users[id]
}
'''
    service_file.write_text(service_content)
    files.append(service_file)
    
    # 多个Go模块
    for i in range(num_modules):
        module_file = project_dir / "internal" / "services" / f"module_{i}.go"
        module_content = f'''package services

import "fmt"

// Module{i} - Complex business module
type Module{i} struct {{
	id int
	name string
}}

func NewModule{i}(id int) *Module{i} {{
	return &Module{i}{{
		id: id,
		name: fmt.Sprintf("Module-{i}"),
	}}
}}

func (m *Module{i}) Process(data string) string {{
	return fmt.Sprintf("Module{i} processed: %s", data)
}}
'''
        module_file.write_text(module_content)
        files.append(module_file)
    
    return files


def run_long_test_scenario():
    """长时间真实压力测试 - 模拟真实开发环境"""
    LOGGER.info("=" * 80)
    LOGGER.info("极端长时间真实压力测试 - 完整系统验证")
    LOGGER.info("=" * 80)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = Path(temp_dir)
        LOGGER.info(f"测试根目录: {base_dir}")
        
        # 初始化系统
        initialize_all_parsers()
        engine = IncrementalUpdateEngine(base_dir)
        engine.initialize()
        
        # 创建真实项目结构
        project_structure = create_project_structure(base_dir)
        
        # 阶段1: 创建完整项目
        LOGGER.info("\n" + "=" * 80)
        LOGGER.info("阶段1: 创建完整多语言项目")
        LOGGER.info("=" * 80)
        
        python_files = create_python_project(project_structure["python_app"])
        js_files = create_js_project(project_structure["js_app"])
        go_files = create_go_project(project_structure["go_app"])
        
        all_files = python_files + js_files + go_files
        LOGGER.info(f"创建了 {len(all_files)} 个源文件")
        
        LOGGER.info("执行初始全量同步...")
        start = time.time()
        initial_stats = engine.full_sync()
        elapsed = time.time() - start
        
        LOGGER.info(f"✓ 初始同步完成: {elapsed:.2f}秒")
        LOGGER.info(f"  处理文件: {initial_stats.files_processed}")
        LOGGER.info(f"  类型: {initial_stats.types_processed}")
        LOGGER.info(f"  函数: {initial_stats.functions_processed}")
        LOGGER.info(f"  调用关系: {initial_stats.calls_resolved}")
        
        # 阶段2: 多轮代码变更 - 模拟真实开发过程
        LOGGER.info("\n" + "=" * 80)
        LOGGER.info("阶段2: 多轮代码变更 - 模拟真实开发")
        LOGGER.info("=" * 80)
        
        num_iterations = 30
        start_time = time.time()
        
        for iteration in range(1, num_iterations + 1):
            LOGGER.info(f"\n--- 迭代 {iteration}/{num_iterations} ---")
            
            # 1. 随机修改一些文件
            num_modify = random.randint(5, 20)
            files_to_modify = random.sample(all_files, min(num_modify, len(all_files)))
            
            for file_path in files_to_modify:
                content = file_path.read_text()
                
                # 添加内容
                added_content = f'''
// ------------------------------
// Added in iteration {iteration}
// ------------------------------
'''
                if file_path.suffix == ".py":
                    new_content = content + f'''
# Added in iteration {iteration}
def dynamic_function_{iteration}():
    """Dynamic function added during test"""
    return {iteration}
'''
                elif file_path.suffix == ".js" or file_path.suffix == ".jsx":
                    new_content = content + f'''
// Added in iteration {iteration}
function dynamicFunction_{iteration}() {{
    return {iteration};
}}
'''
                elif file_path.suffix == ".go":
                    new_content = content + f'''
// Added in iteration {iteration}
func DynamicFunction_{iteration}() int {{
    return {iteration}
}}
'''
                else:
                    new_content = content + added_content
                
                file_path.write_text(new_content)
            
            # 2. 随机删除一些文件
            num_delete = random.randint(2, 5)
            files_to_delete = random.sample(all_files, min(num_delete, len(all_files)-50))  # 保持至少50个文件
            
            deleted_files = []
            for file_path in files_to_delete:
                if file_path.exists():
                    file_path.unlink()
                    deleted_files.append(file_path)
                    all_files.remove(file_path)
            
            # 3. 创建一些新文件
            num_create = random.randint(3, 8)
            new_files = []
            
            for i in range(num_create):
                file_type = random.choice(["py", "js", "go"])
                dir_name = random.choice(list(project_structure.values()))
                new_file = dir_name / f"dynamic_file_{iteration}_{i}.{file_type}"
                
                if file_type == "py":
                    content = f'''#!/usr/bin/env python3
"""Dynamic file - iteration {iteration}"""

def dynamic_{iteration}_{i}(x):
    return x + {iteration} + {i}

class DynamicClass{iteration}_{i}:
    def method(self):
        return f"DynamicClass{iteration}_{i}"
'''
                elif file_type == "js":
                    content = f'''/**
 * Dynamic JS file - iteration {iteration}
 */

function dynamicFunc{iteration}_{i}(x) {{
    return x + {iteration} + {i};
}}

class DynamicClass{iteration}_{i} {{
    method() {{
        return "DynamicClass{iteration}_{i}";
    }}
}}
'''
                else:
                    content = f'''package main

// Dynamic function - iteration {iteration}
func DynamicFunc{iteration}_{i}(x int) int {{
    return x + {iteration} + {i}
}}
'''
                new_file.write_text(content)
                new_files.append(new_file)
                all_files.append(new_file)
            
            # 4. 处理所有变更
            all_changes = files_to_modify + deleted_files + new_files
            
            if all_changes:
                update_stats = engine.process_events(all_changes)
                LOGGER.info(f"变更处理完成:")
                LOGGER.info(f"  修改了 {len(files_to_modify)} 个文件")
                LOGGER.info(f"  删除了 {len(deleted_files)} 个文件")
                LOGGER.info(f"  创建了 {len(new_files)} 个文件")
                LOGGER.info(f"  总文件处理: {update_stats.files_processed}")
            
            # 更新数据库统计
            db_stats = DATABASE_CONNECTION.get_database_stats()
            LOGGER.info(f"当前数据库: 文件 {db_stats['total_files']}，类型 {db_stats['total_types']}，函数 {db_stats['total_functions']}")
            
            # 显示进度
            if iteration % 5 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / iteration
                remaining = avg_time * (num_iterations - iteration)
                LOGGER.info(f"进度: {iteration}/{num_iterations}，已用时 {elapsed:.2f}秒，预计剩余 {remaining:.2f}秒")
        
        # 最终阶段
        LOGGER.info("\n" + "=" * 80)
        LOGGER.info("阶段3: 最终验证和性能检查")
        LOGGER.info("=" * 80)
        
        final_stats = DATABASE_CONNECTION.get_database_stats()
        total_time = time.time() - start_time
        
        LOGGER.info(f"\n✓ 长时间压力测试完成！")
        LOGGER.info(f"  总运行时间: {total_time:.2f}秒")
        LOGGER.info(f"  总迭代次数: {num_iterations}")
        LOGGER.info(f"  最终文件数: {final_stats['total_files']}")
        LOGGER.info(f"  最终类型数: {final_stats['total_types']}")
        LOGGER.info(f"  最终函数数: {final_stats['total_functions']}")
        
        LOGGER.info("\n" + "=" * 80)
        LOGGER.info("系统稳定运行！无任何崩溃或错误！")
        LOGGER.info("=" * 80)


if __name__ == "__main__":
    run_long_test_scenario()
