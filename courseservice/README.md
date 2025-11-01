# Course Service

Microservice để quản lý và chuyển đổi cấu trúc khóa học từ Moodle.

## 🎯 Features

- ✅ **Moodle Integration**: Kết nối với Moodle API
- ✅ **Hierarchy Converter**: Chuyển đổi structure phẳng → deep hierarchy
- ✅ **MongoDB Storage**: Lưu trữ course data
- ✅ **Structured Logging**: Logs với colors + file rotation
- ✅ **Error Handling**: Custom exceptions và consistent responses
- ✅ **Production Ready**: Docker, health checks

## 📁 Structure

```
courseservice/
├── app.py              # Flask application
├── config.py           # Configuration
├── database.py         # MongoDB connection
│
├── routes/            # API endpoints
│   ├── course_routes.py
│   └── learning_path_routes.py
│
├── services/          # Business logic
│   ├── moodle_client.py
│   └── gemini_service.py
│
└── utils/             # Utilities
    ├── logger.py
    ├── exceptions.py
    └── moodle_converter.py
```

## 🚀 Quick Start

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. Configure

Create `.env`:

```env
MONGO_URI=mongodb://localhost:27017/courseservice
MOODLE_API_BASE=http://localhost:8100/webservice/rest/server.php
ADDRESS_MOODLE=localhost:8100
MOODLE_TOKEN=your_token
GEMINI_API_KEY=your_key  # optional
```

### 3. Run

```bash
python app.py
```

Service starts on `http://localhost:5001`

## 📊 API Endpoints

### Health Check
```bash
GET /api/health
```

### Moodle Courses
```bash
# Get all courses
GET /api/moodle/courses

# Get course detail
GET /api/moodle/courses/<course_id>

# Get course hierarchy (NEW)
GET /api/moodle/courses/<course_id>/hierarchy

# Get enrolled users
GET /api/moodle/courses/<course_id>/users
```

### MongoDB CRUD
```bash
GET    /api/courses         # List all
POST   /api/courses         # Create
GET    /api/courses/<id>    # Get one
PUT    /api/courses/<id>    # Update
DELETE /api/courses/<id>    # Delete
```

## 🔧 Usage Examples

### Get Course Hierarchy

```bash
curl http://localhost:5001/api/moodle/courses/2/hierarchy
```

Response:
```json
{
  "course_name": "Tin 12 - AI",
  "analysis": {
    "total_nodes": 85,
    "max_depth": 3,
    "node_type_counts": {
      "course": 1,
      "section": 10,
      "activity": 45,
      "resource": 29
    }
  },
  "hierarchy": {
    "id": 0,
    "name": "Tin 12 - AI",
    "type": "course",
    "children": [...]
  }
}
```

### Use Converter in Code

```python
from utils.moodle_converter import MoodleStructureConverter
from services.moodle_client import get_moodle_client

# Get course data
client = get_moodle_client()
contents = client.get_course_contents(course_id=2)

# Convert to hierarchy
converter = MoodleStructureConverter(course_name="My Course")
converter.convert(contents)

# Get results
hierarchy = converter.to_dict()
analysis = converter.analyze_structure()

print(f"Max depth: {analysis['max_depth']}")
print(f"Total nodes: {analysis['total_nodes']}")
```

## 🧪 Testing

```bash
# Run examples
python examples.py

# Health check
curl http://localhost:5001/api/health
```

## 📝 Logging

Logs saved in `logs/` directory:

- `courseservice.log` - All logs
- `courseservice_error.log` - Errors only

```bash
# Watch logs
tail -f logs/courseservice.log

# Watch errors only
tail -f logs/courseservice_error.log
```

## 🐳 Docker

```bash
# Build
docker build -t courseservice .

# Run
docker run -d -p 5001:5001 \
  -e MONGO_URI=mongodb://mongo:27017/courseservice \
  -e MOODLE_TOKEN=your_token \
  courseservice
```

## 🔧 Extend for New Modules

```python
from utils.moodle_converter import MoodleStructureConverter, NodeType

class CustomConverter(MoodleStructureConverter):
    MODULE_TYPE_MAPPING = {
        **MoodleStructureConverter.MODULE_TYPE_MAPPING,
        'workspace': NodeType.MODULE,      # Add new type
        'discussion': NodeType.ACTIVITY,
    }

# Use normally
converter = CustomConverter()
converter.convert(moodle_data)
```

## 📚 Documentation

- `QUICKSTART.md` - 5-minute quick start
- `CHANGELOG.md` - Version history
- `examples.py` - Working examples

## 🛠️ Tech Stack

- **Python 3.x**
- **Flask** - Web framework
- **MongoDB** - Database
- **Moodle API** - Data source
- **Google Gemini** - AI integration (optional)

## 📞 Support

Check logs for errors:
```bash
tail -f logs/courseservice_error.log
```

Test health:
```bash
curl http://localhost:5001/api/health
```

---

**Version**: 2.0  
**Status**: ✅ Production Ready
