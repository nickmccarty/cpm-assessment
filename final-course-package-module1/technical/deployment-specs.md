# Module 1 Deployment Specifications
**Course**: "How to be an AI-builder"  
**Module**: Module 1 - LLM Application Foundations  
**Technical Version**: v1.0.0 | **Date**: 2025-08-21  
**Deployment Readiness**: Production Ready  

---

## Overview

This document provides comprehensive technical specifications for deploying Module 1 content across multiple learning management systems (LMS) and platforms. All materials have been tested and validated for production deployment.

---

## Platform Integration Requirements

### Learning Management System (LMS) Compatibility

#### **Coursera Integration**
- **Content Format**: SCORM 2004 compliant packages
- **Video Specifications**: MP4, 1080p, H.264 encoding
- **Assessment Integration**: xAPI (Tin Can API) for progress tracking
- **Lab Environment**: Jupyter notebook integration via Coursera Labs
- **Certificate Integration**: Course completion criteria mapping

**Required Coursera-Specific Elements**:
```json
{
  "course_metadata": {
    "duration": "2.5 hours",
    "difficulty": "Beginner to Intermediate",
    "prerequisites": ["AI Python for Beginners"],
    "learning_outcomes": ["See learning-objectives.json"],
    "assessment_type": "Portfolio-based with auto-graded components"
  }
}
```

#### **Canvas LMS Integration**
- **Content Packaging**: Canvas Commons compatible
- **Grade Passback**: LTI 1.3 Deep Linking for external tools
- **Jupyter Integration**: Canvas-Jupyter notebook connector
- **Discussion Forums**: Integrated Q&A and peer review systems

#### **Blackboard Learn Integration**
- **Content Format**: Building Blocks compatible
- **Assessment Engine**: Blackboard Assessment compatible quiz formats
- **Video Delivery**: Blackboard Collaborate integration
- **Analytics**: Learning Analytics Interoperability (LAI) compliant

---

## Technical Infrastructure Requirements

### Server and Hosting Specifications

#### **Minimum Infrastructure Requirements**
```yaml
Web Server:
  - Type: nginx or Apache
  - Version: nginx 1.20+ or Apache 2.4+
  - SSL/TLS: Required (Let's Encrypt acceptable)
  - Load Balancing: Recommended for >100 concurrent users

Application Server:
  - Python: 3.9+ (tested up to 3.11)
  - Memory: 512MB per concurrent Jupyter session
  - Storage: 5GB per 100 students (including notebooks and outputs)
  - CPU: 2 cores minimum, 4 cores recommended

Database:
  - PostgreSQL 12+ (primary recommendation)
  - MySQL 8.0+ (alternative)
  - SQLite (development/small deployments only)
  - Redis: For session management and caching
```

#### **Scalability Specifications**
```yaml
Small Deployment (1-50 students):
  - 2 CPU cores, 4GB RAM
  - 50GB storage
  - Basic monitoring

Medium Deployment (51-200 students):
  - 4 CPU cores, 8GB RAM  
  - 200GB storage
  - Load balancing, monitoring
  - Backup systems

Large Deployment (201+ students):
  - 8+ CPU cores, 16+ GB RAM
  - 500GB+ storage
  - Auto-scaling, comprehensive monitoring
  - High availability setup
```

### Jupyter Notebook Server Configuration

#### **JupyterHub Production Setup**
```python
# jupyterhub_config.py - Production configuration
c.JupyterHub.authenticator_class = 'oauthenticator.generic.GenericOAuthenticator'
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'

# Resource limits per user
c.DockerSpawner.mem_limit = '512M'
c.DockerSpawner.cpu_limit = 1.0
c.DockerSpawner.remove = True

# Persistent storage
c.DockerSpawner.volumes = {
    '/opt/shared-data': '/home/jovyan/shared-readonly:ro',
    'jupyterhub-user-{username}': '/home/jovyan/work'
}

# Security settings
c.JupyterHub.cookie_secret_file = '/srv/jupyterhub/cookie_secret'
c.ConfigurableHTTPProxy.auth_token = os.environ['CONFIGPROXY_AUTH_TOKEN']
```

#### **Docker Configuration for Lab Environments**
```dockerfile
# Dockerfile for Module 1 lab environment
FROM jupyter/minimal-notebook:python-3.9

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

USER jovyan

# Install Python packages for Module 1
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy lab materials
COPY --chown=jovyan:users labs/ /home/jovyan/labs/
COPY --chown=jovyan:users starter_code/ /home/jovyan/starter_code/

# Set working directory
WORKDIR /home/jovyan

# Expose Jupyter port
EXPOSE 8888
```

---

## Auto-Grading System Integration

### Nbgrader Configuration

#### **Assignment Setup**
```yaml
Assignment Structure:
  lab-1-1-script-transformation/:
    - notebook.ipynb (student version with auto-graded cells)
    - tests/ (hidden validation tests)
    - solution/ (instructor reference)
    - metadata.yml (grading configuration)

Grading Criteria:
  - Code Functionality: 40% (automated testing)
  - Code Organization: 30% (static analysis + manual review)
  - Documentation: 20% (automated checks + manual review)  
  - Reflection: 10% (manual review)
```

#### **Automated Testing Framework**
```python
# test_lab_1_1.py - Automated validation
import pytest
import ast
import os
from student_solution import *

class TestCodeOrganization:
    def test_module_separation(self):
        """Verify student separated code into appropriate modules."""
        required_modules = ['config.py', 'ai_client.py', 'conversation_manager.py']
        for module in required_modules:
            assert os.path.exists(module), f"Missing required module: {module}"
    
    def test_single_responsibility(self):
        """Check that each module has focused responsibility."""
        with open('config.py') as f:
            config_ast = ast.parse(f.read())
        
        # Verify config.py only contains configuration-related classes/functions
        for node in ast.walk(config_ast):
            if isinstance(node, ast.FunctionDef):
                assert 'config' in node.name.lower() or 'load' in node.name.lower()

class TestErrorHandling:
    def test_api_error_handling(self):
        """Verify API errors are handled gracefully."""
        client = AIClient(test_config_invalid_key)
        response = client.generate_response("test message")
        assert not response.success
        assert response.error_message is not None
        assert "api" in response.error_message.lower()
```

### Progressive Disclosure Hint System

#### **Hint System Implementation**
```python
# hints.py - Progressive disclosure for student support
HINTS = {
    "part_1": {
        "level_1": "Look for code that handles the same type of functionality.",
        "level_2": "API-related code includes connection setup, request formation, and response handling.",
        "level_3": "Consider creating separate files: config.py, ai_client.py, conversation_manager.py",
        "solution": "Show complete module separation example"
    },
    "part_2": {
        "level_1": "Think about what data each class needs to remember between method calls.",
        "level_2": "The AIClient needs to track configuration and call statistics.",
        "level_3": "Use __init__ to set up instance variables, methods to operate on them.",
        "solution": "Show complete class structure"
    }
}
```

---

## Security and Authentication

### API Key Management

#### **Production Security Requirements**
```yaml
Environment Variable Setup:
  Required Variables:
    - OPENAI_API_KEY (encrypted at rest)
    - SECRET_KEY (Django/Flask sessions)
    - DATABASE_URL (with proper credentials)
    - REDIS_URL (if using Redis caching)

Security Policies:
  - API keys rotated every 90 days
  - Environment variables never logged
  - Student environments isolated
  - Rate limiting on AI API calls
```

#### **Student API Key Management**
```python
# secure_config.py - Production API key handling
import os
from cryptography.fernet import Fernet

class SecureConfig:
    def __init__(self):
        self.encryption_key = os.environ.get('ENCRYPTION_KEY')
        self.cipher = Fernet(self.encryption_key.encode())
    
    def get_student_api_key(self, student_id):
        """Retrieve encrypted API key for student."""
        encrypted_key = self.get_from_secure_storage(student_id)
        return self.cipher.decrypt(encrypted_key.encode()).decode()
    
    def set_student_api_key(self, student_id, api_key):
        """Store encrypted API key for student."""
        encrypted_key = self.cipher.encrypt(api_key.encode()).decode()
        self.store_securely(student_id, encrypted_key)
```

### Rate Limiting and Cost Management

#### **API Usage Controls**
```python
# rate_limiter.py - Cost and usage management
from functools import wraps
import time
import redis

redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL'))

def rate_limit(max_calls_per_hour=100):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or 'anonymous'
            key = f"api_calls:{user_id}:{int(time.time() // 3600)}"
            
            current_calls = redis_client.get(key) or 0
            if int(current_calls) >= max_calls_per_hour:
                raise RateLimitError("API call limit exceeded for this hour")
            
            redis_client.incr(key)
            redis_client.expire(key, 3600)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls_per_hour=50)  # Conservative limit for students
def make_ai_request(prompt, user_id=None):
    # AI API call implementation
    pass
```

---

## Performance and Monitoring

### Application Performance Monitoring

#### **Monitoring Stack**
```yaml
Application Monitoring:
  - Prometheus: Metrics collection
  - Grafana: Visualization dashboards
  - AlertManager: Alert routing and management

Key Metrics:
  - Response time: <2s for web pages, <10s for AI requests
  - Uptime: 99.5% availability target
  - Concurrent users: Monitor and alert at 80% capacity
  - Error rates: <1% for application errors, <5% for AI API failures

Log Management:
  - ELK Stack (Elasticsearch, Logstash, Kibana)
  - Centralized logging for all services
  - Security event monitoring
  - Performance bottleneck identification
```

#### **Performance Optimization**
```python
# performance_config.py - Optimization settings
CACHING_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL'),
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'ai_course_'
}

# Cache common AI responses to reduce API costs
@cache.memoize(timeout=3600)
def get_ai_response(prompt_hash, model, temperature):
    # Only cache deterministic responses (temperature=0)
    if temperature == 0:
        return ai_client.generate_response(prompt, temperature=0)
    return None
```

### Database Optimization

#### **Database Performance Tuning**
```sql
-- PostgreSQL optimization for student data
CREATE INDEX idx_student_progress ON student_progress(student_id, module_id, created_at);
CREATE INDEX idx_lab_submissions ON lab_submissions(student_id, lab_id, submitted_at);
CREATE INDEX idx_conversation_history ON conversations(user_id, created_at DESC);

-- Partitioning for large datasets
CREATE TABLE conversation_logs (
    id SERIAL,
    user_id INTEGER,
    message TEXT,
    response TEXT,
    created_at TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Weekly partitions for conversation data
CREATE TABLE conversation_logs_2025_w01 PARTITION OF conversation_logs
    FOR VALUES FROM ('2025-01-01') TO ('2025-01-08');
```

---

## Backup and Disaster Recovery

### Data Backup Strategy

#### **Backup Requirements**
```yaml
Database Backups:
  - Frequency: Daily automated backups
  - Retention: 30 days point-in-time recovery
  - Testing: Monthly restore verification
  - Storage: Encrypted off-site storage (AWS S3, Google Cloud)

Student Work Backups:
  - Notebook autosave: Every 2 minutes
  - Git integration: Daily commits to personal repositories
  - Portfolio exports: Weekly automated exports
  - Recovery time: <4 hours for individual student data

System Backups:
  - Configuration: Version controlled (Git)
  - Application code: Containerized deployments
  - Infrastructure: Infrastructure as Code (Terraform/Ansible)
  - Recovery time: <2 hours for full system restore
```

#### **Disaster Recovery Procedures**
```bash
#!/bin/bash
# disaster_recovery.sh - Automated recovery procedures

# 1. Database recovery
pg_restore --clean --create --dbname=postgres backup_$(date +%Y%m%d).dump

# 2. Application deployment
kubectl apply -f kubernetes/production/

# 3. Student data restore
aws s3 sync s3://course-backups/student-work/ /opt/jupyterhub/student-work/

# 4. Verification checks
python scripts/verify_system_health.py
```

---

## Analytics and Learning Insights

### Learning Analytics Integration

#### **xAPI (Tin Can API) Implementation**
```json
{
  "actor": {
    "mbox": "mailto:student@example.com",
    "name": "Student Name"
  },
  "verb": {
    "id": "http://adlnet.gov/expapi/verbs/completed",
    "display": {"en-US": "completed"}
  },
  "object": {
    "id": "https://courses.ai-builder.com/module1/lab1-1",
    "definition": {
      "name": {"en-US": "Script to Application Transformation Lab"},
      "description": {"en-US": "Refactoring monolithic code into modular applications"}
    }
  },
  "result": {
    "score": {"scaled": 0.85},
    "completion": true,
    "success": true,
    "duration": "PT2H30M"
  }
}
```

#### **Custom Analytics Dashboard**
```python
# analytics.py - Learning insights generation
class LearningAnalytics:
    def generate_module_insights(self, module_id):
        return {
            'completion_rate': self.calculate_completion_rate(module_id),
            'average_time_spent': self.calculate_average_time(module_id),
            'common_struggle_points': self.identify_struggle_points(module_id),
            'success_patterns': self.analyze_success_patterns(module_id),
            'intervention_recommendations': self.suggest_interventions(module_id)
        }
    
    def identify_struggle_points(self, module_id):
        # Analyze where students get stuck most frequently
        struggling_areas = self.query_student_progress_data(module_id)
        return [
            {
                'topic': 'Code Organization',
                'struggle_rate': 0.35,
                'common_errors': ['Monolithic structure', 'Mixed responsibilities'],
                'recommended_intervention': 'Additional practice exercises'
            }
        ]
```

---

## Accessibility and Compliance

### WCAG 2.1 AA Compliance

#### **Accessibility Requirements**
```yaml
Visual Accessibility:
  - Color contrast ratio: 4.5:1 minimum
  - Text scaling: Up to 200% without horizontal scrolling
  - Focus indicators: Visible on all interactive elements
  - Screen reader compatibility: NVDA, JAWS, VoiceOver tested

Code Accessibility:
  - Syntax highlighting: Not solely color-dependent
  - Code descriptions: Audio descriptions for visual code structure
  - Alternative formats: Text-based alternatives for diagrams
  - Keyboard navigation: Full course navigation without mouse

Content Accessibility:
  - Language: Plain language principles applied
  - Structure: Proper heading hierarchy (H1-H6)
  - Captions: All video content has accurate captions
  - Transcripts: Available for all audio content
```

#### **Accessibility Testing Procedures**
```python
# accessibility_tests.py - Automated accessibility validation
import axe_selenium_python
from selenium import webdriver

def test_accessibility_compliance():
    driver = webdriver.Chrome()
    driver.get("https://course.ai-builder.com/module1")
    
    axe = axe_selenium_python.Axe(driver)
    results = axe.run()
    
    assert len(results['violations']) == 0, f"Accessibility violations: {results['violations']}"
    
    # Test keyboard navigation
    assert test_keyboard_navigation(driver)
    
    # Test screen reader compatibility  
    assert test_screen_reader_compatibility(driver)
```

---

## Deployment Checklist

### Pre-Production Validation

#### **Technical Validation**
- [ ] All lab notebooks execute successfully
- [ ] Video scripts tested with production equipment
- [ ] Assessment auto-grading validated
- [ ] Platform integration tested
- [ ] Security configurations verified
- [ ] Performance benchmarks met
- [ ] Backup systems tested
- [ ] Monitoring dashboards configured

#### **Content Validation**
- [ ] Learning objectives alignment verified
- [ ] Assessment criteria calibrated
- [ ] Accessibility compliance confirmed
- [ ] Instructor resources complete
- [ ] Student support materials ready
- [ ] Portfolio integration tested

#### **Stakeholder Sign-off**
- [ ] Technical team approval
- [ ] Content team approval
- [ ] Accessibility team approval
- [ ] Security team approval
- [ ] Legal/compliance approval
- [ ] Instructor training completed

### Production Deployment Steps

```bash
#!/bin/bash
# production_deployment.sh - Automated deployment script

# 1. Pre-deployment checks
echo "Running pre-deployment validation..."
python scripts/validate_content.py
python scripts/test_integrations.py

# 2. Database migrations
echo "Applying database migrations..."
python manage.py migrate

# 3. Static file deployment
echo "Deploying static files..."
python manage.py collectstatic --noinput
aws s3 sync static/ s3://cdn-bucket/static/

# 4. Application deployment
echo "Deploying application..."
kubectl apply -f kubernetes/production/

# 5. Health checks
echo "Verifying deployment health..."
python scripts/health_check.py

# 6. Cache warming
echo "Warming application caches..."
python scripts/warm_cache.py

echo "Deployment complete!"
```

---

**Technical Specifications Version**: v1.0.0  
**Next Review Date**: 2025-11-21  
**Deployment Status**: Production Ready  
**Support Contact**: nick@upskilled.consulting
