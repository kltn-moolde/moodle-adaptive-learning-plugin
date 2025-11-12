# Hướng dẫn Mở rộng Question Service

## Cấu trúc hiện tại

```
questionservice/
├── app.py                      # Main Flask application
├── config.py                   # Configuration
├── database.py                 # MongoDB connection
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── README.md                  # Full documentation
├── QUICKSTART.md              # Quick start guide
├── ARCHITECTURE.md            # This file
│
├── models/                    # Data models
│   ├── __init__.py
│   └── question.py           # Question and Answer models
│
├── routes/                    # API endpoints
│   ├── __init__.py
│   └── question_routes.py    # Question API routes
│
├── services/                  # Business logic
│   ├── __init__.py
│   ├── question_generator.py # Question CRUD operations
│   └── xml_converter.py      # JSON to XML conversion
│
├── utils/                     # Utilities
│   ├── __init__.py
│   ├── logger.py             # Logging setup
│   ├── exceptions.py         # Custom exceptions
│   └── validators.py         # Data validation
│
└── examples/                  # Examples and scripts
    ├── sample_questions.json  # Sample question data
    └── convert_json_to_xml.py # Standalone converter script
```

## Design Principles

### 1. Separation of Concerns
- **Models**: Chỉ chứa data structures và validation cơ bản
- **Services**: Chứa business logic và database operations
- **Routes**: Chỉ xử lý HTTP requests/responses
- **Utils**: Các tiện ích dùng chung

### 2. Dependency Injection
- Database connection được inject qua `database.py`
- Logger được setup và reuse
- Configuration được tập trung tại `config.py`

### 3. Error Handling
- Custom exceptions cho từng loại lỗi
- Global error handlers trong `app.py`
- Consistent error response format

### 4. Validation
- Input validation tại routes layer
- Business logic validation tại models
- Validators tái sử dụng được

## Phase 2: Thêm loại câu hỏi mới

### Bước 1: Thêm model
```python
# models/question.py

@dataclass
class EssayQuestion(Question):
    """Essay question type"""
    response_format: str = "editor"  # editor, plain, monospaced
    required_length: Optional[int] = None
    max_length: Optional[int] = None
```

### Bước 2: Update XML Converter
```python
# services/xml_converter.py

def _convert_essay_question(self, question_elem, question):
    """Convert essay question to XML"""
    ET.SubElement(question_elem, "responseformat").text = question.response_format
    if question.required_length:
        ET.SubElement(question_elem, "minwordlimit").text = str(question.required_length)
```

### Bước 3: Thêm validation
```python
# utils/validators.py

def validate_essay_question(data: Dict) -> Tuple[bool, Optional[str]]:
    """Validate essay question data"""
    if data.get('response_format') not in ['editor', 'plain', 'monospaced']:
        return False, "Invalid response format"
    return True, None
```

## Phase 3: AI-Powered Question Generation

### Bước 1: Tạo AI Service
```python
# services/ai_generator.py

from google.generativeai import GenerativeModel

class AIQuestionGenerator:
    """Generate questions using AI"""
    
    def __init__(self, api_key: str):
        self.model = GenerativeModel('gemini-pro')
        
    def generate_from_text(self, content: str, num_questions: int = 5):
        """Generate questions from text content"""
        prompt = f"""
        Tạo {num_questions} câu hỏi trắc nghiệm từ nội dung sau:
        
        {content}
        
        Format JSON như sau:
        {{
            "questions": [
                {{
                    "name": "...",
                    "question_text": "...",
                    "difficulty": "easy|medium|hard",
                    "answers": [...]
                }}
            ]
        }}
        """
        response = self.model.generate_content(prompt)
        return self._parse_response(response)
```

### Bước 2: Thêm API endpoint
```python
# routes/ai_routes.py

@ai_bp.route('/generate', methods=['POST'])
def generate_questions_ai():
    """Generate questions using AI"""
    data = request.get_json()
    content = data.get('content')
    num_questions = data.get('num_questions', 5)
    
    generator = AIQuestionGenerator(Config.GEMINI_API_KEY)
    questions = generator.generate_from_text(content, num_questions)
    
    return jsonify({'questions': questions}), 200
```

### Bước 3: Register blueprint
```python
# app.py

from routes.ai_routes import ai_bp
app.register_blueprint(ai_bp, url_prefix='/api/ai')
```

## Phase 4: Document Upload

### Bước 1: File Upload Handler
```python
# services/document_parser.py

class DocumentParser:
    """Parse documents to extract text"""
    
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Parse PDF file"""
        import PyPDF2
        # Implementation
        
    @staticmethod
    def parse_docx(file_path: str) -> str:
        """Parse DOCX file"""
        import docx
        # Implementation
```

### Bước 2: Upload endpoint
```python
# routes/upload_routes.py

@upload_bp.route('/document', methods=['POST'])
def upload_document():
    """Upload document and generate questions"""
    file = request.files['file']
    
    # Save file
    filepath = save_upload(file)
    
    # Parse document
    content = DocumentParser.parse(filepath)
    
    # Generate questions
    generator = AIQuestionGenerator(Config.GEMINI_API_KEY)
    questions = generator.generate_from_text(content)
    
    return jsonify({'questions': questions}), 200
```

### Bước 3: Update dependencies
```
# requirements.txt
PyPDF2==3.0.1
python-docx==1.1.0
```

## Phase 5: Question Templates

### Template System
```python
# models/template.py

@dataclass
class QuestionTemplate:
    """Template for question generation"""
    template_id: str
    name: str
    question_type: str
    template_text: str
    variables: List[str]
    
    def generate_question(self, values: Dict) -> Question:
        """Generate question from template"""
        question_text = self.template_text
        for var, val in values.items():
            question_text = question_text.replace(f"{{{var}}}", val)
        # Create Question object
```

### Template API
```python
# routes/template_routes.py

@template_bp.route('/apply', methods=['POST'])
def apply_template():
    """Apply template to generate questions"""
    data = request.get_json()
    template_id = data['template_id']
    values = data['values']
    
    template = TemplateService.get_template(template_id)
    question = template.generate_question(values)
    
    return jsonify({'question': question.to_dict()}), 200
```

## Best Practices

### 1. Testing
```python
# tests/test_question_service.py

import pytest
from services.question_generator import QuestionGenerator

def test_create_question():
    question_data = {...}
    question = QuestionGenerator.create_question(question_data)
    assert question.question_id is not None
```

### 2. Logging
```python
# Always log important operations
logger.info(f"Creating question: {question.name}")
logger.error(f"Failed to create question: {str(e)}")
```

### 3. Error Handling
```python
# Use custom exceptions
try:
    question = QuestionGenerator.get_question(id)
except QuestionNotFoundError:
    return jsonify({'error': 'Question not found'}), 404
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500
```

### 4. Validation
```python
# Validate early
is_valid, error = validate_question_data(data)
if not is_valid:
    return jsonify({'error': error}), 400
```

### 5. Database Indexing
```python
# Create indexes for better performance
mongo.db.questions.create_index([('difficulty', 1)])
mongo.db.questions.create_index([('question_type', 1)])
mongo.db.questions.create_index([('created_at', -1)])
```

## Performance Optimization

### 1. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_question_cached(question_id: str):
    return QuestionGenerator.get_question(question_id)
```

### 2. Batch Operations
```python
# Use batch operations when possible
QuestionGenerator.create_questions_batch(questions_data)
```

### 3. Pagination
```python
# Always use pagination for list endpoints
questions, total = QuestionGenerator.get_questions(
    page=page, limit=limit
)
```

## Security

### 1. Input Sanitization
```python
from html import escape

def sanitize_html(text: str) -> str:
    """Sanitize HTML input"""
    return escape(text)
```

### 2. Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@limiter.limit("10 per minute")
@app.route('/api/questions/create')
def create_question():
    ...
```

### 3. Authentication (Future)
```python
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not verify_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated
```

## Deployment

### Development
```bash
# Direct Python (auto-reload enabled)
python3 app.py
```

### Production
```bash
# Gunicorn with 4 workers
gunicorn --bind 0.0.0.0:5003 \
         --workers 4 \
         --timeout 120 \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         "app:app"

# Or use the start script
./start.sh
```

### Docker
```bash
docker-compose up -d
```

### Systemd (Linux)
```bash
sudo systemctl enable questionservice
sudo systemctl start questionservice
```

See `DEPLOYMENT.md` for detailed deployment instructions.

## Monitoring

### Health Check
```bash
curl http://localhost:5003/health
```

### Statistics
```bash
curl http://localhost:5003/api/questions/statistics
```

### Logs
```bash
tail -f logs/app.log
```
