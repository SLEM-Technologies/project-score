# VetSuccess Platform Migration to .NET Core 10
## Comprehensive Project Brief & Migration Strategy

---

## Executive Summary

This document outlines the complete strategy for migrating the VetSuccess veterinary practice management platform from Django (Python) to .NET Core 10 (C#). The project involves converting a multi-tenant SaaS application with SMS/email automation, call center features, and practice management capabilities.

**Current Stack:**
- Backend: Django 4.2.8 (Python)
- Database: PostgreSQL 16
- Cache/Message Broker: Redis 7
- Task Queue: Celery
- API: Django REST Framework
- Container: Docker

**Target Stack:**
- Backend: .NET Core 10 (ASP.NET Core)
- Database: PostgreSQL 16 (unchanged)
- Cache/Message Broker: Redis 7 (unchanged)
- Task Queue: Hangfire or Azure Functions
- API: ASP.NET Core Web API
- Container: Docker

---

## Table of Contents

1. [Project Scope](#project-scope)
2. [Application Architecture](#application-architecture)
3. [Technical Requirements](#technical-requirements)
4. [Migration Strategy](#migration-strategy)
5. [Risk Assessment](#risk-assessment)
6. [Timeline & Phases](#timeline--phases)
7. [Team Requirements](#team-requirements)
8. [Cost Estimation](#cost-estimation)
9. [Success Criteria](#success-criteria)
10. [Appendices](#appendices)

---

## 1. Project Scope

### 1.1 In Scope

#### Backend Migration
- Convert all Django applications to ASP.NET Core modules
- Migrate 40+ database models to Entity Framework Core entities
- Convert REST API endpoints (authentication, call center, SMS, email)
- Migrate background tasks from Celery to Hangfire/.NET alternatives
- Implement JWT authentication with ASP.NET Core Identity
- Migrate custom admin panel to Blazor/Razor Pages or third-party admin framework
- Convert middleware and request/response pipeline
- Migrate integration services (Dialpad SMS, SendGrid, Azure Blob Storage)

#### Data Layer
- Convert Django ORM queries to Entity Framework Core
- Migrate all database migrations to EF Core migrations
- Preserve existing PostgreSQL database schema
- Migrate custom database indexes and constraints
- Convert raw SQL queries and stored procedures (if any)

#### Task Processing
- Convert Celery tasks to Hangfire background jobs
- Migrate periodic tasks (Celery Beat) to Hangfire recurring jobs or .NET Timer-based services
- Implement task queues (low, email, sms) in Hangfire

#### External Integrations
- Dialpad SMS API integration
- SendGrid email integration
- Azure Blob Storage integration
- Sentry error tracking (migrate to .NET SDK)

#### DevOps & Infrastructure
- Convert Dockerfile to multi-stage .NET Core build
- Update docker-compose.yml for .NET services
- Migrate Azure DevOps pipelines for .NET build/deploy
- Environment configuration migration (.env to appsettings.json/User Secrets)

### 1.2 Out of Scope (Requires Separate Assessment)

- Frontend application migration (needs separate discovery)
- Database schema changes or optimizations
- Cloud infrastructure migration (Azure/AWS)
- New feature development during migration
- Performance optimization (post-migration phase)

### 1.3 Key Constraints

- **Zero downtime requirement**: Migration must support parallel running systems
- **Data integrity**: No data loss during migration
- **API compatibility**: Existing API contracts must be maintained
- **Security compliance**: Maintain HIPAA/healthcare data security standards
- **Budget**: TBD based on team size and timeline

---

## 2. Application Architecture

### 2.1 Current Django Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│              (Frontend - Technology Unknown)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ REST API (JWT Auth)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Django Backend (Port 8000)                 │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Call       │  │     SMS      │  │    Email     │      │
│  │   Center     │  │  Management  │  │  Management  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Users     │  │  Admin Panel │  │ Data         │      │
│  │    & Auth    │  │  (Custom)    │  │ Migration    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────────┐
        │             │             │                 │
        ▼             ▼             ▼                 ▼
┌──────────────┐ ┌─────────┐ ┌─────────┐   ┌──────────────────┐
│  PostgreSQL  │ │  Redis  │ │  Celery │   │   External APIs  │
│   Database   │ │  Cache  │ │ Workers │   │                  │
│              │ │         │ │  & Beat │   │ - Dialpad SMS    │
└──────────────┘ └─────────┘ └─────────┘   │ - SendGrid Email │
                                            │ - Azure Storage  │
                                            │ - Sentry         │
                                            └──────────────────┘
```

### 2.2 Target .NET Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│         (Frontend - To Be Assessed Separately)               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ REST API (JWT Auth)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              ASP.NET Core Web API (Port 8000)                │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Controllers & Minimal APIs                  │   │
│  │  - CallCenterController  - AuthController            │   │
│  │  - SmsController         - AdminController           │   │
│  │  - EmailController       - HealthCheckController     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Application Services Layer               │   │
│  │  - CallCenterService    - SmsService                 │   │
│  │  - EmailService         - UserService                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Data Access Layer                    │   │
│  │  - VetSuccessDbContext (EF Core)                     │   │
│  │  - Repository Pattern (Optional)                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                Background Jobs (Hangfire)             │   │
│  │  - SmsEventCreationJob    - DailyEmailUpdatesJob     │   │
│  │  - PeriodicCleanupJob     - ReminderProcessingJob    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────────┐
        │             │             │                 │
        ▼             ▼             ▼                 ▼
┌──────────────┐ ┌─────────┐ ┌──────────┐  ┌──────────────────┐
│  PostgreSQL  │ │  Redis  │ │ Hangfire │  │   External APIs  │
│   Database   │ │  Cache  │ │ Dashboard│  │                  │
│  (EF Core)   │ │         │ │  & Jobs  │  │ - Dialpad SDK    │
└──────────────┘ └─────────┘ └──────────┘  │ - SendGrid SDK   │
                                            │ - Azure SDK      │
                                            │ - Sentry SDK     │
                                            └──────────────────┘
```

### 2.3 Core Application Modules

Based on the Django app structure, the following modules need migration:

| Django App | .NET Core Module | Primary Responsibility |
|------------|------------------|------------------------|
| `apps.users` | `VetSuccess.Users` | User authentication, authorization, custom user model |
| `apps.call_center` | `VetSuccess.CallCenter` | Client/patient management, appointments, practice data |
| `apps.sms` | `VetSuccess.Sms` | SMS template management, SMS history, event tracking |
| `apps.email` | `VetSuccess.Email` | Email event management, daily update emails |
| `apps.admin` | `VetSuccess.Admin` | Custom admin interface for practice management |
| `apps.base` | `VetSuccess.Core` | Shared models, enums, exceptions, constants |
| `apps.data_migration` | `VetSuccess.DataMigration` | One-time data migration scripts |

---

## 3. Technical Requirements

### 3.1 Technology Stack Mapping

| Component | Current (Django) | Target (.NET Core 10) | Migration Complexity |
|-----------|------------------|----------------------|---------------------|
| Web Framework | Django 4.2.8 | ASP.NET Core 10 | High |
| ORM | Django ORM | Entity Framework Core 9+ | High |
| API Framework | Django REST Framework | ASP.NET Core Web API | Medium |
| Authentication | SimpleJWT | ASP.NET Core Identity + JWT Bearer | Medium |
| Task Queue | Celery 5.3.6 | Hangfire 1.8+ | High |
| Database | PostgreSQL 16 | PostgreSQL 16 (Npgsql) | Low |
| Caching | django-redis | StackExchange.Redis | Low |
| Email | django-anymail (SendGrid) | SendGrid.NET SDK | Low |
| File Storage | Azure Storage Blob | Azure.Storage.Blobs | Low |
| Error Tracking | sentry-sdk[django] | Sentry.AspNetCore | Low |
| API Documentation | drf-spectacular | Swashbuckle (Swagger) | Low |
| Admin Interface | Django Admin (custom) | Blazor Server/AdminLTE/.NET Admin | High |
| Dependency Injection | Django apps | Microsoft.Extensions.DependencyInjection | Medium |
| Configuration | python-decouple (.env) | appsettings.json + User Secrets | Low |
| Static Files | Whitenoise | ASP.NET Core Static Files | Low |
| Validation | Django Forms/Serializers | FluentValidation / Data Annotations | Medium |
| Date/Time | Arrow, python-dateutil | NodaTime / DateTimeOffset | Low |

### 3.2 Database Model Migration

**Total Models to Migrate: ~40+**

Key models identified:
- **User Management**: User (custom), UserManager
- **Call Center**: Practice, PracticeSettings, Client, Patient, Appointment, Phone, Email, Reminder, Answer, Question, Outcome
- **SMS**: SMSEvent, SMSHistory, SMSTemplate
- **Email**: UpdatesEmailEvent

**Migration Approach:**
1. Generate EF Core models from existing PostgreSQL schema (reverse engineering)
2. Manually adjust for naming conventions (.NET PascalCase vs Python snake_case)
3. Add data annotations and fluent API configurations
4. Preserve all indexes, constraints, and relationships
5. Test migrations in isolated environment

### 3.3 API Endpoints Inventory

**Authentication Endpoints** (`api/v1/auth/`)
- `POST /api/v1/auth/token/` - Obtain JWT token
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token

**Call Center Endpoints** (`api/v1/call-center/`)
- `GET /api/v1/call-center/clients/` - List clients with search/filter
- `GET /api/v1/call-center/clients/{odu_id}` - Client detail
- `PUT/PATCH /api/v1/call-center/clients/{odu_id}` - Update client
- `GET /api/v1/call-center/clients/contacted/` - Contacted clients list
- `GET /api/v1/call-center/practices/` - List practices
- `GET /api/v1/call-center/outcomes/` - List outcomes (cached)
- `GET /api/v1/call-center/faq/{odu_id}` - Practice FAQ
- `PATCH /api/v1/call-center/sms/{uuid}/switch/` - Update SMS status

**Utility Endpoints**
- `GET /api/` - API info
- `GET /api/health-check/` - Health check
- `GET /api/db-health-check/` - Database health check
- `GET /api/docs/schema/` - OpenAPI schema (debug only)
- `GET /api/sms-event-creation/{odu_id}` - Trigger SMS event (admin only)
- `GET /api/daily-email-updates` - Trigger email updates (admin only)

**Total: ~15-20 endpoints** (excluding admin endpoints)

### 3.4 Background Tasks Inventory

**Periodic Tasks (Celery Beat → Hangfire Recurring Jobs)**
- SMS Event Creation (periodic launcher)
- Daily Email Updates Generation
- Data cleanup/maintenance tasks

**Async Tasks (Celery Workers → Hangfire Background Jobs)**
- `SMSEventCreationTask` - Process SMS events per practice
- `CreateDailyUpdatesEmailEventsPeriodicTask` - Generate daily email events
- Email sending tasks
- SMS sending tasks via Dialpad

**Task Queues:**
- `low` - Low priority tasks
- `email` - Email processing
- `sms` - SMS processing

### 3.5 External Integrations

| Integration | Current Library | .NET Library | API Documentation |
|-------------|----------------|--------------|-------------------|
| Dialpad SMS | python-dialpad 2.2.2 | Custom HttpClient / SDK | dialpad.com/developers |
| SendGrid Email | django-anymail[sendgrid] | SendGrid 9.x.x | sendgrid.com/docs |
| Azure Blob Storage | azure-storage-blob 12.19.0 | Azure.Storage.Blobs 12.x | learn.microsoft.com/azure |
| Sentry Error Tracking | sentry-sdk[django] 1.42.0 | Sentry.AspNetCore 4.x | docs.sentry.io |

### 3.6 Performance & Optimization Features

Current Django optimizations that need preservation:
- Database connection pooling (`CONN_MAX_AGE=600`)
- Redis caching for static data (1-hour TTL for outcomes)
- Query optimization with `select_related()`, `prefetch_related()`, `only()` → EF Core `Include()`, `ThenInclude()`
- Custom database indexes for search operations

---

## 4. Migration Strategy

### 4.1 Recommended Approach: **Incremental Migration with Strangler Fig Pattern**

This approach minimizes risk by running Django and .NET services in parallel, gradually migrating modules.

#### Phase 1: Foundation & Infrastructure (Weeks 1-4)
**Goal:** Set up .NET Core project structure and shared infrastructure

**Tasks:**
1. **Project Setup**
   - Create ASP.NET Core 10 solution structure
   - Set up projects: API, Core, Infrastructure, Tests
   - Configure dependency injection and middleware pipeline
   - Set up logging, health checks, error handling

2. **Database Layer**
   - Reverse engineer PostgreSQL schema to EF Core models
   - Create `VetSuccessDbContext`
   - Configure entity relationships and indexes
   - Set up migration system
   - Validate against existing Django migrations

3. **Configuration & Environment**
   - Migrate environment variables to `appsettings.json`
   - Set up User Secrets for local development
   - Configure Azure KeyVault for production secrets
   - Set up connection strings and service configurations

4. **Infrastructure Services**
   - Implement Redis caching service
   - Set up Sentry integration
   - Configure logging (Serilog recommended)
   - Implement health check endpoints

5. **DevOps Foundation**
   - Create Dockerfile for .NET Core
   - Update docker-compose.yml to include both Django and .NET services
   - Set up initial CI/CD pipeline for .NET builds

**Deliverables:**
- Working .NET Core skeleton with database connectivity
- Health check endpoints operational
- Docker containers running side-by-side with Django
- Initial CI/CD pipeline

#### Phase 2: Authentication & Core API (Weeks 5-8)
**Goal:** Migrate authentication and establish API foundation

**Tasks:**
1. **Authentication Migration**
   - Implement ASP.NET Core Identity with custom User model
   - Configure JWT Bearer authentication
   - Migrate token generation/refresh endpoints
   - Ensure JWT tokens are compatible with Django tokens (transition period)

2. **Core Models & Repositories**
   - Implement base models and entities
   - Create repository pattern (if chosen)
   - Migrate enums, constants, exceptions
   - Set up shared DTOs and validation models

3. **API Infrastructure**
   - Configure Swagger/OpenAPI documentation
   - Implement API versioning
   - Set up CORS policies
   - Create custom middleware (error handling, logging)
   - Implement request/response filters

4. **Testing Framework**
   - Set up xUnit/NUnit test projects
   - Create integration test infrastructure
   - Implement test database seeding
   - Write tests for authentication flow

**Deliverables:**
- Working authentication endpoints in .NET
- Core domain models and database context
- API documentation (Swagger)
- Test coverage for auth module

#### Phase 3: Call Center Module Migration (Weeks 9-14)
**Goal:** Migrate primary business logic module

**Tasks:**
1. **Model Migration**
   - Migrate Practice, Client, Patient, Appointment entities
   - Implement related entities (Phone, Email, Reminder, etc.)
   - Configure EF Core relationships and indexes
   - Add validation attributes and business rules

2. **Service Layer**
   - Implement `CallCenterService`
   - Migrate business logic from Django views/services
   - Implement search and filtering logic
   - Add caching layer for frequently accessed data

3. **API Endpoints**
   - Implement all Call Center controllers
   - Migrate query parameter handling
   - Implement pagination, filtering, sorting
   - Add DTOs and AutoMapper profiles

4. **Testing & Validation**
   - Write unit tests for services
   - Write integration tests for API endpoints
   - Perform side-by-side comparison with Django endpoints
   - Load testing and performance validation

**Deliverables:**
- Complete Call Center API in .NET
- Unit and integration tests
- Performance benchmarks
- API documentation

#### Phase 4: SMS & Email Modules (Weeks 15-18)
**Goal:** Migrate notification/communication systems

**Tasks:**
1. **SMS Module**
   - Migrate SMSEvent, SMSHistory, SMSTemplate models
   - Implement SMS service layer
   - Integrate Dialpad API (custom HttpClient or SDK)
   - Migrate template variable replacement logic
   - Implement SMS endpoints

2. **Email Module**
   - Migrate UpdatesEmailEvent model
   - Implement email service layer
   - Integrate SendGrid SDK
   - Migrate email templates
   - Implement Azure Blob Storage integration for attachments

3. **Testing**
   - Unit tests for SMS/email services
   - Integration tests with external APIs (mocked)
   - End-to-end tests for notification flows

**Deliverables:**
- SMS and Email modules fully operational
- External integrations working
- Test coverage for notification systems

#### Phase 5: Background Jobs Migration (Weeks 19-22)
**Goal:** Migrate Celery tasks to Hangfire

**Tasks:**
1. **Hangfire Setup**
   - Install and configure Hangfire
   - Set up Hangfire dashboard (with authentication)
   - Configure PostgreSQL storage for Hangfire
   - Set up job queues (low, email, sms)

2. **Task Migration**
   - Convert `SMSEventCreationTask` to Hangfire background job
   - Convert `CreateDailyUpdatesEmailEventsPeriodicTask`
   - Migrate periodic tasks to recurring jobs
   - Implement job monitoring and error handling

3. **Job Scheduling**
   - Configure Hangfire recurring jobs with cron expressions
   - Implement job retry policies
   - Set up job logging and alerting
   - Migrate Celery Beat schedules

4. **Testing & Monitoring**
   - Test job execution and scheduling
   - Validate queue processing
   - Set up monitoring and alerting
   - Performance testing under load

**Deliverables:**
- All background jobs migrated to Hangfire
- Hangfire dashboard operational
- Job monitoring in place
- Celery workers can be decommissioned

#### Phase 6: Admin Panel Migration (Weeks 23-26)
**Goal:** Migrate custom Django admin to .NET solution

**Options:**
- **Option A:** Blazor Server admin panel (full .NET stack)
- **Option B:** Razor Pages with AdminLTE template
- **Option C:** Third-party admin framework (e.g., RADzen, Syncfusion)
- **Option D:** Keep Django admin running separately (not recommended)

**Tasks:**
1. **Admin Framework Selection**
   - Evaluate options based on requirements
   - Set up chosen framework
   - Design admin UI/UX

2. **Admin Features Migration**
   - User management interface
   - Practice management
   - SMS template management
   - FAQ/Q&A management
   - Outcome management
   - Practice settings

3. **Authorization**
   - Implement role-based access control
   - Restrict admin access to authorized users
   - Audit logging for admin actions

**Deliverables:**
- Functional admin panel in .NET
- All admin features migrated
- Authorization and security implemented

#### Phase 7: Data Migration & Validation (Weeks 27-28)
**Goal:** Ensure data integrity and perform final validation

**Tasks:**
1. **Data Validation**
   - Run data integrity checks
   - Compare Django vs .NET database queries
   - Validate all relationships and constraints
   - Check for data corruption or loss

2. **Migration Scripts**
   - Create any necessary data transformation scripts
   - Document data migration procedures
   - Prepare rollback procedures

3. **End-to-End Testing**
   - Full system integration tests
   - User acceptance testing (UAT)
   - Load and stress testing
   - Security penetration testing

**Deliverables:**
- Data validation report
- Migration documentation
- UAT sign-off
- Performance test results

#### Phase 8: Cutover & Deployment (Weeks 29-30)
**Goal:** Switch production traffic to .NET application

**Tasks:**
1. **Pre-Cutover**
   - Final deployment to staging environment
   - Smoke testing in staging
   - Prepare deployment runbook
   - Schedule maintenance window

2. **Cutover Execution**
   - Deploy .NET application to production
   - Switch load balancer/reverse proxy to .NET
   - Monitor logs and metrics
   - Keep Django running as fallback (blue-green deployment)

3. **Post-Cutover**
   - 24-hour monitoring period
   - Bug fixes and hotfixes as needed
   - Gradual traffic increase
   - Decommission Django application after stability confirmed

**Deliverables:**
- Production .NET application
- Deployment documentation
- Monitoring dashboards
- Django decommissioned

### 4.2 Alternative Approach: Big Bang Migration

**Not Recommended** due to high risk, but included for completeness.

Migrate entire application at once during maintenance window. Suitable only if:
- Application is small
- Downtime is acceptable
- Risk tolerance is high
- Team is highly experienced

**Timeline:** 16-20 weeks (more compressed, higher risk)

---

## 5. Risk Assessment

### 5.1 Technical Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Data Loss during Migration** | Medium | Critical | - Incremental migration<br>- Comprehensive backups<br>- Parallel running systems<br>- Validation scripts |
| **API Breaking Changes** | High | High | - Contract testing<br>- API versioning<br>- Backward compatibility layer<br>- Thorough testing |
| **Performance Degradation** | Medium | High | - Performance benchmarking<br>- Load testing<br>- Query optimization<br>- Caching strategy |
| **Integration Failures** | Medium | High | - Early integration testing<br>- Mock services for testing<br>- Vendor SDK validation |
| **Background Job Failures** | Medium | High | - Hangfire monitoring<br>- Job retry mechanisms<br>- Alerting system<br>- Gradual cutover |
| **Security Vulnerabilities** | Low | Critical | - Security audit<br>- Penetration testing<br>- Code reviews<br>- OWASP compliance |
| **Database Migration Issues** | Medium | Critical | - Schema validation<br>- Migration testing<br>- Rollback procedures<br>- Read replicas for testing |
| **Skill Gap in Team** | High | Medium | - Training program<br>- Bring in .NET consultants<br>- Pair programming<br>- Code reviews |

### 5.2 Business Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Extended Downtime** | Low | Critical | - Blue-green deployment<br>- Rollback plan<br>- Incremental cutover |
| **Cost Overruns** | High | High | - Detailed project planning<br>- Regular budget reviews<br>- Contingency budget (20-30%) |
| **Timeline Delays** | High | High | - Agile methodology<br>- Regular sprint reviews<br>- Buffer time built in |
| **User Disruption** | Medium | High | - User communication plan<br>- Training sessions<br>- Comprehensive documentation |
| **Regulatory Compliance** | Low | Critical | - HIPAA compliance review<br>- Security audit<br>- Legal consultation |

### 5.3 Organizational Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Key Personnel Turnover** | Medium | High | - Knowledge documentation<br>- Cross-training<br>- Retention bonuses |
| **Lack of Stakeholder Buy-in** | Low | Medium | - Regular demos<br>- Clear communication<br>- Show incremental value |
| **Resource Constraints** | High | High | - Prioritization<br>- Outsourcing options<br>- Hire contractors |

---

## 6. Timeline & Phases

### 6.1 Detailed Timeline (30 Weeks)

```
┌──────────────────────────────────────────────────────────────────┐
│                     30-Week Migration Timeline                    │
└──────────────────────────────────────────────────────────────────┘

Weeks 1-4:    ████████ Foundation & Infrastructure
Weeks 5-8:    ████████ Authentication & Core API
Weeks 9-14:   ████████████████ Call Center Module
Weeks 15-18:  ████████████ SMS & Email Modules
Weeks 19-22:  ████████████ Background Jobs (Hangfire)
Weeks 23-26:  ████████████ Admin Panel Migration
Weeks 27-28:  ████ Data Migration & Validation
Weeks 29-30:  ████ Cutover & Deployment
```

### 6.2 Milestone Schedule

| Week | Milestone | Description |
|------|-----------|-------------|
| 4 | Foundation Complete | .NET Core skeleton, Docker, DB connectivity |
| 8 | Auth & Core API | JWT auth working, API foundation |
| 14 | Call Center Module | Primary business logic migrated |
| 18 | SMS/Email Modules | Notification systems operational |
| 22 | Background Jobs | All Celery tasks migrated to Hangfire |
| 26 | Admin Panel | Admin interface functional |
| 28 | Validation Complete | UAT sign-off, data validated |
| 30 | Production Cutover | Django decommissioned |

### 6.3 Critical Path

The following tasks are on the critical path and cannot be delayed:
1. Database schema migration (Weeks 1-2)
2. EF Core configuration and validation (Weeks 2-3)
3. Authentication implementation (Weeks 5-6)
4. Call Center API migration (Weeks 9-13)
5. Background job migration (Weeks 19-21)
6. UAT and validation (Weeks 27-28)
7. Production cutover (Weeks 29-30)

---

## 7. Team Requirements

### 7.1 Recommended Team Structure

**Core Team (Full-time)**

| Role | Quantity | Responsibilities | Skills Required |
|------|----------|------------------|----------------|
| **Technical Lead / Architect** | 1 | - Overall architecture<br>- Technical decisions<br>- Code reviews<br>- Risk management | - 7+ years .NET Core<br>- Django experience<br>- Cloud architecture<br>- Team leadership |
| **Senior .NET Developer** | 2-3 | - Backend development<br>- API implementation<br>- Database layer<br>- Code reviews | - 5+ years .NET Core<br>- EF Core expert<br>- RESTful API design<br>- PostgreSQL |
| **Mid-level .NET Developer** | 2-3 | - Feature implementation<br>- Unit testing<br>- Bug fixes<br>- Documentation | - 2-4 years .NET Core<br>- ASP.NET Core Web API<br>- Testing frameworks<br>- Git |
| **DevOps Engineer** | 1 | - CI/CD pipelines<br>- Docker/containers<br>- Azure infrastructure<br>- Monitoring | - Azure DevOps<br>- Docker/Kubernetes<br>- Infrastructure as Code<br>- Monitoring tools |
| **QA Engineer / SDET** | 1-2 | - Test planning<br>- Test automation<br>- Integration testing<br>- UAT coordination | - .NET testing frameworks<br>- API testing (Postman)<br>- Selenium/Playwright<br>- SQL |
| **Database Administrator** | 0.5 (part-time) | - Schema migration<br>- Performance tuning<br>- Backup/recovery<br>- Index optimization | - PostgreSQL expert<br>- Migration experience<br>- Performance tuning<br>- EF Core |

**Total Core Team: 7.5-10.5 FTEs**

**Supporting Roles (Part-time or As-Needed)**

| Role | Quantity | Time Commitment | Responsibilities |
|------|----------|-----------------|------------------|
| **Product Owner** | 1 | 25-50% | Requirements, prioritization, UAT sign-off |
| **Frontend Developer** | 1-2 | 25-50% (if frontend migration) | Frontend app migration assessment and implementation |
| **Security Specialist** | 1 | 10-20% | Security audit, penetration testing, compliance |
| **Technical Writer** | 1 | 25% | Documentation, runbooks, API docs |
| **Business Analyst** | 1 | 10-20% | Requirements gathering, stakeholder communication |

### 7.2 Skill Requirements

**Must-Have Skills:**
- ASP.NET Core 6.0+ (preferably 8.0 or 10.0)
- Entity Framework Core 7.0+
- C# 10.0+
- PostgreSQL and SQL proficiency
- RESTful API design and implementation
- JWT authentication
- Docker and containerization
- Git version control
- Unit testing (xUnit/NUnit)

**Highly Desirable:**
- Django and Python (for understanding existing codebase)
- Hangfire or similar background job frameworks
- Redis caching
- Azure services (Blob Storage, Key Vault)
- SendGrid, Dialpad, or similar integrations
- Blazor (if chosen for admin panel)
- Azure DevOps or GitHub Actions
- Healthcare/HIPAA compliance knowledge

### 7.3 Training Plan

**Week 1-2: Onboarding & Orientation**
- Current Django application walkthrough
- Business domain training (veterinary practice management)
- Architecture review
- Development environment setup

**Week 3-4: Technical Deep Dive**
- Django codebase deep dive sessions
- Database schema review
- API contract analysis
- Integration points documentation

**Ongoing:**
- Weekly knowledge sharing sessions
- Code review best practices
- Pair programming for complex modules
- .NET best practices workshops (if team is transitioning from Django)

---

## 8. Cost Estimation

### 8.1 Labor Costs (30 Weeks)

**Assumptions:**
- Average rates based on US market (adjust for geography)
- Full-time = 40 hours/week

| Role | Quantity | Hourly Rate | Hours | Total Cost |
|------|----------|-------------|-------|------------|
| Technical Lead | 1 | $150/hr | 1,200 hrs | $180,000 |
| Senior .NET Developer | 2.5 | $120/hr | 3,000 hrs | $360,000 |
| Mid-level .NET Developer | 2.5 | $85/hr | 3,000 hrs | $255,000 |
| DevOps Engineer | 1 | $110/hr | 1,200 hrs | $132,000 |
| QA Engineer | 1.5 | $90/hr | 1,800 hrs | $162,000 |
| Database Administrator | 0.5 | $130/hr | 600 hrs | $78,000 |
| **Subtotal Core Team** | **9 FTEs** | - | **10,800 hrs** | **$1,167,000** |
| Product Owner | 1 @ 50% | $100/hr | 600 hrs | $60,000 |
| Frontend Developer | 1 @ 50% | $95/hr | 600 hrs | $57,000 |
| Security Specialist | 1 @ 20% | $140/hr | 240 hrs | $33,600 |
| Technical Writer | 1 @ 25% | $75/hr | 300 hrs | $22,500 |
| **Subtotal Supporting** | - | - | **1,740 hrs** | **$173,100** |
| **TOTAL LABOR** | - | - | **12,540 hrs** | **$1,340,100** |

### 8.2 Infrastructure & Tools Costs

| Item | Monthly Cost | Duration | Total Cost |
|------|--------------|----------|------------|
| Development Azure Environment | $1,500 | 7 months | $10,500 |
| Staging Azure Environment | $2,000 | 7 months | $14,000 |
| Additional Development Tools (IDEs, licenses) | $500 | 7 months | $3,500 |
| Third-party Libraries/SDKs | $200 | 7 months | $1,400 |
| Monitoring & Logging (extended) | $300 | 7 months | $2,100 |
| **TOTAL INFRASTRUCTURE** | - | - | **$31,500** |

### 8.3 Other Costs

| Item | Cost |
|------|------|
| Training & Workshops | $15,000 |
| External Consultants (as needed) | $25,000 |
| Security Audit & Penetration Testing | $20,000 |
| Contingency (20% of labor) | $268,020 |
| **TOTAL OTHER** | **$328,020** |

### 8.4 Total Project Cost Estimate

| Category | Cost |
|----------|------|
| Labor | $1,340,100 |
| Infrastructure & Tools | $31,500 |
| Other (Training, Audit, Contingency) | $328,020 |
| **GRAND TOTAL** | **$1,699,620** |

**Cost Range:** $1.5M - $2.0M (depending on team composition, rates, and geography)

**Note:** This assumes:
- US-based team (costs can be reduced 40-60% with offshore team)
- 30-week timeline
- No major scope creep
- Frontend migration assessed separately

---

## 9. Success Criteria

### 9.1 Technical Success Criteria

- [ ] **Functional Parity**: All Django features replicated in .NET
- [ ] **API Compatibility**: 100% of API endpoints migrated with same contracts
- [ ] **Performance**: .NET application meets or exceeds Django performance benchmarks
  - API response times ≤ Django baseline
  - Background job processing times ≤ Celery baseline
  - Database query performance ≤ Django ORM baseline
- [ ] **Data Integrity**: Zero data loss or corruption during migration
- [ ] **Test Coverage**: Minimum 80% code coverage with unit and integration tests
- [ ] **Security**: Pass security audit and penetration testing
- [ ] **Reliability**: 99.9% uptime during first 30 days post-cutover
- [ ] **Scalability**: Handle 2x current load without degradation

### 9.2 Business Success Criteria

- [ ] **Zero Unplanned Downtime**: No outages during migration
- [ ] **User Satisfaction**: No increase in support tickets post-cutover
- [ ] **Timeline**: Project completed within 10% of estimated timeline
- [ ] **Budget**: Project completed within 15% of budget
- [ ] **Compliance**: Maintain HIPAA compliance throughout migration

### 9.3 Key Performance Indicators (KPIs)

| KPI | Target | Measurement |
|-----|--------|-------------|
| API Response Time (p95) | < 500ms | Application Insights |
| Background Job Success Rate | > 99% | Hangfire Dashboard |
| Database Connection Pool Efficiency | > 90% | EF Core Metrics |
| Cache Hit Rate | > 85% | Redis Metrics |
| Error Rate | < 0.1% | Sentry |
| Unit Test Coverage | > 80% | Code Coverage Tools |
| Integration Test Pass Rate | 100% | CI/CD Pipeline |

---

## 10. Appendices

### Appendix A: Django Dependencies → .NET Packages Mapping

| Django Package | .NET NuGet Package | Notes |
|----------------|-------------------|-------|
| django==4.2.8 | ASP.NET Core 10.0 | Core framework |
| djangorestframework==3.14.0 | ASP.NET Core Web API | Built-in |
| psycopg==3.1.14 | Npgsql.EntityFrameworkCore.PostgreSQL | PostgreSQL provider |
| djangorestframework-simplejwt==5.3.0 | Microsoft.AspNetCore.Authentication.JwtBearer | JWT auth |
| celery==5.3.6 | Hangfire 1.8+ | Background jobs |
| django-celery-results==2.5.1 | Hangfire.PostgreSql | Job storage |
| django-redis==5.2.0 | StackExchange.Redis | Redis client |
| python-dialpad==2.2.2 | Custom HttpClient | Dialpad SDK |
| azure-storage-blob==12.19.0 | Azure.Storage.Blobs | Azure SDK |
| django-anymail[sendgrid]==10.2 | SendGrid 9.x | Email service |
| sentry-sdk[django]==1.42.0 | Sentry.AspNetCore | Error tracking |
| drf-spectacular==0.26.5 | Swashbuckle.AspNetCore | OpenAPI/Swagger |
| django-filter==23.4 | Custom implementation | Filtering |
| whitenoise==6.6.0 | Microsoft.AspNetCore.StaticFiles | Static files |
| arrow==1.3.0 | NodaTime (optional) | Date/time |
| python-decouple==3.8 | Microsoft.Extensions.Configuration | Config |
| gunicorn==21.2.0 | Kestrel (built-in) | Web server |
| django-jsonform==2.22.0 | Custom/Blazor | Admin forms |

### Appendix B: Database Schema Considerations

**Naming Convention Mapping:**
- Django: `snake_case` (e.g., `first_name`)
- .NET: `PascalCase` (e.g., `FirstName`)

**Options:**
1. **Keep PostgreSQL as snake_case** (recommended for backward compatibility)
   - Use `[Column("snake_case_name")]` attributes in C#
   - EF Core fluent API to map column names
   
2. **Migrate to PascalCase**
   - Requires database schema changes
   - Not recommended (high risk, breaks Django compatibility)

**Indexes to Preserve:**
```sql
-- Django auto-created indexes
apps_client_upper_first_name_idx
apps_client_upper_last_name_idx
apps_smshistory_practice_id_idx
-- Custom indexes from migrations
-- Full list needs inventory from Django migrations
```

### Appendix C: Environment Variables Migration

**Django (.env) → .NET (appsettings.json)**

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=vetsuccess_db;Username=developer;Password=***"
  },
  "Redis": {
    "ConnectionString": "localhost:6379,defaultDatabase=1"
  },
  "Jwt": {
    "SecretKey": "***",
    "Issuer": "VetSuccess",
    "Audience": "VetSuccess",
    "AccessTokenLifetimeMinutes": 720,
    "RefreshTokenLifetimeMinutes": 1500
  },
  "Dialpad": {
    "ApiToken": "***",
    "SendSms": false
  },
  "Azure": {
    "StorageAccountName": "***",
    "StorageAccountSasToken": "***",
    "ContainerName": "***",
    "UpdatesPathPrefix": "daily_notification"
  },
  "SendGrid": {
    "ApiKey": "***",
    "FromEmail": "***",
    "UseDebugEmail": true,
    "DebugRecipient": "***",
    "DebugCcRecipient": "***"
  },
  "Sentry": {
    "Dsn": "***",
    "Enabled": false
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning"
    }
  }
}
```

### Appendix D: Frontend Migration Considerations

**Frontend Stack Discovery Needed:**

The current Django backend serves a frontend application, but the frontend technology stack is not identified in the provided files. Before frontend migration:

1. **Identify Frontend Technology**
   - React, Vue.js, Angular?
   - Server-side rendered (Django templates)?
   - Separate SPA?

2. **Assessment Required**
   - Frontend codebase inventory
   - API consumption patterns
   - State management approach
   - Build and deployment process

3. **Migration Options**
   - **Option A**: Keep frontend as-is, only update API endpoints
   - **Option B**: Migrate to Blazor WebAssembly
   - **Option C**: Migrate to modern React/Next.js
   - **Option D**: Migrate to Angular

**Recommendation:** Assess frontend separately and potentially migrate in a later phase.

### Appendix E: Testing Strategy

**Test Pyramid:**
```
               /\
              /  \
             / E2E \         ← 10% (End-to-End Tests)
            /------\
           /        \
          / Integr-  \       ← 30% (Integration Tests)
         /  ation     \
        /--------------\
       /                \
      /   Unit Tests     \   ← 60% (Unit Tests)
     /____________________\
```

**Testing Approach:**

1. **Unit Tests (60% of tests)**
   - Services, repositories, validators
   - Business logic
   - Utilities and helpers
   - Framework: xUnit or NUnit
   - Mocking: Moq or NSubstitute

2. **Integration Tests (30%)**
   - API endpoints
   - Database operations (EF Core)
   - External service integrations (mocked)
   - Framework: xUnit with WebApplicationFactory

3. **End-to-End Tests (10%)**
   - Critical user flows
   - Multi-module scenarios
   - Framework: Selenium or Playwright

4. **Performance Tests**
   - Load testing with k6 or JMeter
   - Benchmark against Django baseline
   - Database query performance

5. **Security Tests**
   - OWASP ZAP automated scans
   - Manual penetration testing
   - Dependency vulnerability scanning

### Appendix F: Deployment Architecture

**Blue-Green Deployment Strategy:**

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    │   / API Gateway │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
         ┌──────────▼───────┐   ┌────▼────────────┐
         │   BLUE (Django)  │   │ GREEN (.NET)    │
         │   Current Prod   │   │  New Version    │
         └──────────┬───────┘   └────┬────────────┘
                    │                 │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   PostgreSQL    │
                    │   (Shared DB)   │
                    └─────────────────┘
```

**Cutover Steps:**
1. Deploy .NET (GREEN) alongside Django (BLUE)
2. Route 10% traffic to .NET
3. Monitor metrics and errors
4. Gradually increase to 50%, then 100%
5. Keep Django running for 48 hours as fallback
6. Decommission Django if stable

### Appendix G: Rollback Plan

**Triggers for Rollback:**
- Error rate > 1%
- Response time > 2x baseline
- Critical functionality broken
- Data integrity issues detected

**Rollback Procedure:**
1. Switch load balancer back to Django (BLUE)
2. Drain .NET connections gracefully
3. Investigate root cause
4. Fix issues in .NET
5. Redeploy and retry cutover

**Rollback SLA:** < 15 minutes to revert to Django

### Appendix H: Documentation Deliverables

**Required Documentation:**

1. **Architecture Documentation**
   - System architecture diagrams
   - Component interaction diagrams
   - Database schema documentation
   - API documentation (Swagger/OpenAPI)

2. **Developer Documentation**
   - Setup and development environment guide
   - Coding standards and conventions
   - Testing guidelines
   - Contribution guide

3. **Operations Documentation**
   - Deployment runbook
   - Monitoring and alerting setup
   - Troubleshooting guide
   - Disaster recovery procedures

4. **User Documentation**
   - API changelog
   - Migration guide for API consumers
   - Admin panel user guide

5. **Project Documentation**
   - Migration project plan
   - Risk register
   - Decision log
   - Lessons learned

---

## Summary & Next Steps

### Recommended Action Plan

1. **Executive Approval** (Week 0)
   - Review this project brief with stakeholders
   - Secure budget approval
   - Get executive sponsor commitment

2. **Team Assembly** (Weeks 1-2)
   - Recruit or assign team members
   - Onboard team to Django codebase
   - Set up development environments

3. **Phase 1 Kickoff** (Week 3)
   - Begin Foundation & Infrastructure phase
   - Establish sprint cadence (2-week sprints)
   - Set up project tracking (Jira/Azure DevOps)

4. **Frontend Assessment** (Parallel, Weeks 1-4)
   - Identify frontend technology stack
   - Create separate frontend migration brief
   - Decide: migrate now or later

### Key Questions for Stakeholders

1. **Timeline**: Is 30 weeks acceptable, or do you need faster delivery?
2. **Budget**: Is $1.5-2M budget approved?
3. **Downtime**: Zero downtime confirmed as requirement?
4. **Frontend**: Should frontend be migrated simultaneously or separately?
5. **Team**: Internal team, contractors, or hybrid approach?
6. **Go-Live**: Any specific date constraints (e.g., end of fiscal year)?

### Risk Acceptance

**Stakeholders must acknowledge:**
- Migrations of this scale carry inherent risk
- Incremental approach minimizes but doesn't eliminate risk
- Adequate budget, time, and resources are critical
- Strong executive sponsorship is required
- Change management and communication plan needed

---

**Document Version:** 1.0  
**Date:** January 2026  
**Prepared By:** Technical Consultant  
**Status:** Draft - Awaiting Stakeholder Review

**Next Review Date:** TBD  
**Approval Required From:**
- CTO/VP Engineering
- Product Owner
- Finance/Budget Owner
- Security/Compliance Officer
