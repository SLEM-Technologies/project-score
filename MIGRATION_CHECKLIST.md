# Django to .NET Core 10 Migration Checklist
## Comprehensive Task List for VetSuccess Platform Migration

---

## Pre-Migration Phase

### Discovery & Planning
- [ ] Review and approve project brief
- [ ] Secure budget and executive sponsorship
- [ ] Identify and assess frontend application technology
- [ ] Document all Django application features
- [ ] Inventory all external integrations
- [ ] Review database schema and migrations
- [ ] Identify data migration requirements
- [ ] Create detailed project timeline
- [ ] Establish success criteria and KPIs

### Team Setup
- [ ] Assemble core migration team
- [ ] Hire/assign Technical Lead
- [ ] Hire/assign .NET developers (4-6)
- [ ] Hire/assign DevOps engineer
- [ ] Hire/assign QA engineers (1-2)
- [ ] Engage database administrator (part-time)
- [ ] Identify product owner
- [ ] Set up team communication channels
- [ ] Schedule kickoff meeting

### Environment Setup
- [ ] Set up development Azure/cloud environment
- [ ] Set up staging environment
- [ ] Configure development tools (VS/Rider licenses)
- [ ] Set up version control (Git repositories)
- [ ] Configure CI/CD pipelines (skeleton)
- [ ] Set up project management tools (Jira/Azure Boards)
- [ ] Configure monitoring tools (Application Insights/Datadog)
- [ ] Set up Sentry for error tracking

---

## Phase 1: Foundation & Infrastructure (Weeks 1-4)

### Project Structure
- [ ] Create .NET Core 10 solution
- [ ] Set up VetSuccess.API project
- [ ] Set up VetSuccess.Core project
- [ ] Set up VetSuccess.Infrastructure project
- [ ] Set up VetSuccess.Jobs project
- [ ] Set up test projects (Unit, Integration, API)
- [ ] Configure project dependencies
- [ ] Install initial NuGet packages
- [ ] Set up EditorConfig and code style
- [ ] Configure Directory.Build.props

### Database Setup
- [ ] Install Npgsql.EntityFrameworkCore.PostgreSQL
- [ ] Reverse engineer PostgreSQL schema to EF Core models
- [ ] Create VetSuccessDbContext
- [ ] Configure entity relationships with Fluent API
- [ ] Create entity configurations for all models
- [ ] Preserve all database indexes
- [ ] Test database connectivity
- [ ] Validate schema mapping
- [ ] Set up connection pooling
- [ ] Configure retry policies

### Configuration Management
- [ ] Create appsettings.json structure
- [ ] Migrate environment variables to appsettings
- [ ] Set up User Secrets for local development
- [ ] Configure Azure Key Vault for production
- [ ] Set up environment-specific configs
- [ ] Document configuration structure
- [ ] Test configuration loading

### Infrastructure Services
- [ ] Set up Serilog logging
- [ ] Configure console and file sinks
- [ ] Implement structured logging
- [ ] Set up Redis caching service
- [ ] Test Redis connectivity
- [ ] Configure Sentry integration
- [ ] Implement health check endpoints
- [ ] Create database health check
- [ ] Create Redis health check

### DevOps Foundation
- [ ] Create Dockerfile for .NET Core
- [ ] Update docker-compose.yml
- [ ] Test local Docker build
- [ ] Set up Azure DevOps/GitHub Actions pipeline
- [ ] Configure build pipeline
- [ ] Configure test pipeline
- [ ] Set up Docker registry
- [ ] Document deployment process

### Testing Infrastructure
- [ ] Set up xUnit test framework
- [ ] Configure test database (Testcontainers)
- [ ] Set up Moq for mocking
- [ ] Configure code coverage tools
- [ ] Create base test classes
- [ ] Write sample unit test
- [ ] Write sample integration test

---

## Phase 2: Authentication & Core API (Weeks 5-8)

### Authentication Implementation
- [ ] Install Microsoft.AspNetCore.Identity
- [ ] Install Microsoft.AspNetCore.Authentication.JwtBearer
- [ ] Create custom User entity (match Django model)
- [ ] Implement UserManager and SignInManager
- [ ] Create JWT token generator service
- [ ] Implement token validation
- [ ] Create refresh token mechanism
- [ ] Test JWT token generation
- [ ] Test token validation

### Auth API Endpoints
- [ ] Create AuthController
- [ ] Implement POST /api/v1/auth/token (login)
- [ ] Implement POST /api/v1/auth/token/refresh
- [ ] Add request/response DTOs
- [ ] Add validation (FluentValidation)
- [ ] Test auth endpoints manually
- [ ] Write unit tests for auth service
- [ ] Write integration tests for auth endpoints

### Core Models & Repositories
- [ ] Migrate BaseEntity model
- [ ] Create repository interfaces
- [ ] Implement generic repository
- [ ] Set up AutoMapper profiles
- [ ] Create core enums (ReminderStatus, SMSHistoryStatus, etc.)
- [ ] Migrate constants classes
- [ ] Create custom exceptions
- [ ] Implement exception middleware

### API Infrastructure
- [ ] Configure Swagger/OpenAPI
- [ ] Set up API versioning
- [ ] Configure CORS policies
- [ ] Implement error handling middleware
- [ ] Implement request logging middleware
- [ ] Create custom filters (validation, exception)
- [ ] Set up model validation
- [ ] Configure JSON serialization settings
- [ ] Test API documentation (Swagger UI)

### Security
- [ ] Configure HTTPS/TLS
- [ ] Implement rate limiting
- [ ] Configure CSRF protection
- [ ] Set up security headers
- [ ] Implement authorization policies
- [ ] Test security configuration

---

## Phase 3: Call Center Module (Weeks 9-14)

### Model Migration
- [ ] Migrate Practice entity
- [ ] Migrate PracticeSettings entity
- [ ] Migrate Client entity
- [ ] Migrate Patient entity
- [ ] Migrate Appointment entity
- [ ] Migrate Phone entity
- [ ] Migrate Email entity
- [ ] Migrate Reminder entity
- [ ] Migrate Question entity
- [ ] Migrate Answer entity
- [ ] Migrate Outcome entity
- [ ] Configure all entity relationships
- [ ] Create database indexes
- [ ] Test model relationships

### Repository Implementation
- [ ] Create IPracticeRepository
- [ ] Implement PracticeRepository
- [ ] Create IClientRepository
- [ ] Implement ClientRepository
- [ ] Create IPatientRepository
- [ ] Implement PatientRepository
- [ ] Add complex query methods
- [ ] Test repository queries

### Service Layer
- [ ] Create ICallCenterService interface
- [ ] Implement CallCenterService
- [ ] Migrate client search logic
- [ ] Migrate client detail logic
- [ ] Implement practice listing logic
- [ ] Implement FAQ retrieval logic
- [ ] Implement outcome caching logic
- [ ] Add business validation rules
- [ ] Write unit tests for services

### API Endpoints - Clients
- [ ] Implement GET /api/v1/call-center/clients
- [ ] Add search/filter functionality
- [ ] Add pagination support
- [ ] Implement GET /api/v1/call-center/clients/{odu_id}
- [ ] Implement PUT/PATCH /api/v1/call-center/clients/{odu_id}
- [ ] Create request/response DTOs
- [ ] Add validation
- [ ] Write integration tests

### API Endpoints - Other
- [ ] Implement GET /api/v1/call-center/practices
- [ ] Add scheduler mapping logic
- [ ] Implement GET /api/v1/call-center/outcomes (with caching)
- [ ] Implement GET /api/v1/call-center/faq/{odu_id}
- [ ] Implement GET /api/v1/call-center/clients/contacted
- [ ] Add filtering and pagination
- [ ] Write integration tests

### Performance Optimization
- [ ] Optimize database queries (Include/ThenInclude)
- [ ] Implement query result caching
- [ ] Add database query logging (dev only)
- [ ] Load test call center endpoints
- [ ] Compare performance with Django
- [ ] Optimize slow queries

---

## Phase 4: SMS & Email Modules (Weeks 15-18)

### SMS Model Migration
- [ ] Migrate SMSEvent entity
- [ ] Migrate SMSHistory entity
- [ ] Migrate SMSTemplate entity
- [ ] Configure entity relationships
- [ ] Create SMS indexes
- [ ] Test SMS models

### SMS Service Implementation
- [ ] Create ISmsService interface
- [ ] Implement SmsService
- [ ] Migrate SMS template variable replacement logic
- [ ] Implement SMS history tracking
- [ ] Add SMS validation logic
- [ ] Write unit tests

### Dialpad Integration
- [ ] Create IDialpadService interface
- [ ] Implement DialpadService (HttpClient)
- [ ] Configure Dialpad API credentials
- [ ] Implement SMS sending method
- [ ] Add error handling and retries
- [ ] Test Dialpad integration (sandbox)
- [ ] Write integration tests (mocked)

### SMS API Endpoints
- [ ] Implement PATCH /api/v1/call-center/sms/{uuid}/switch
- [ ] Add SMS-related DTOs
- [ ] Add validation
- [ ] Write integration tests

### Email Model Migration
- [ ] Migrate UpdatesEmailEvent entity
- [ ] Configure entity relationships
- [ ] Test email models

### Email Service Implementation
- [ ] Create IEmailService interface
- [ ] Implement EmailService
- [ ] Migrate email template logic
- [ ] Implement email event tracking
- [ ] Write unit tests

### SendGrid Integration
- [ ] Install SendGrid NuGet package
- [ ] Configure SendGrid API key
- [ ] Implement email sending method
- [ ] Create email templates
- [ ] Add error handling
- [ ] Test SendGrid integration
- [ ] Write integration tests (mocked)

### Azure Blob Storage Integration
- [ ] Install Azure.Storage.Blobs
- [ ] Configure Azure Storage connection
- [ ] Implement blob upload/download methods
- [ ] Test blob operations
- [ ] Add error handling

---

## Phase 5: Background Jobs (Weeks 19-22)

### Hangfire Setup
- [ ] Install Hangfire NuGet packages
- [ ] Install Hangfire.PostgreSql
- [ ] Configure Hangfire in Program.cs
- [ ] Set up Hangfire dashboard
- [ ] Configure dashboard authentication
- [ ] Test Hangfire dashboard access

### Job Infrastructure
- [ ] Create background job base classes
- [ ] Set up job logging
- [ ] Configure job retry policies
- [ ] Set up job queues (low, email, sms)
- [ ] Configure queue priorities
- [ ] Test basic job execution

### SMS Jobs
- [ ] Create SmsEventCreationJob
- [ ] Migrate SMS event creation logic
- [ ] Create SMS periodic launcher job
- [ ] Set up recurring job schedule
- [ ] Test job execution
- [ ] Add job monitoring

### Email Jobs
- [ ] Create DailyEmailUpdatesJob
- [ ] Migrate daily email logic
- [ ] Set up recurring job schedule
- [ ] Test job execution
- [ ] Add job monitoring

### Job Monitoring
- [ ] Set up Hangfire metrics
- [ ] Configure job failure alerts
- [ ] Implement job logging to Sentry
- [ ] Create job monitoring dashboard
- [ ] Test job retry behavior
- [ ] Document job configuration

### Celery Decommissioning Plan
- [ ] Document all Celery tasks
- [ ] Validate all tasks migrated
- [ ] Create cutover plan
- [ ] Test Hangfire under load
- [ ] Prepare rollback procedure

---

## Phase 6: Admin Panel (Weeks 23-26)

### Framework Selection
- [ ] Evaluate admin panel options (Blazor/Razor/3rd party)
- [ ] Get stakeholder approval for chosen framework
- [ ] Set up admin panel project
- [ ] Configure authentication for admin
- [ ] Create admin layout/navigation

### User Management
- [ ] Create user list view
- [ ] Create user detail/edit view
- [ ] Implement user creation
- [ ] Implement user deletion
- [ ] Add role management
- [ ] Test user management features

### Practice Management
- [ ] Create practice list view
- [ ] Create practice detail/edit view
- [ ] Implement practice creation
- [ ] Implement practice settings management
- [ ] Add practice archiving
- [ ] Test practice management

### SMS Template Management
- [ ] Create template list view
- [ ] Create template detail/edit view
- [ ] Implement template creation
- [ ] Add template validation
- [ ] Test template variable replacement
- [ ] Test template management

### FAQ Management
- [ ] Create question/answer list view
- [ ] Create Q&A edit view
- [ ] Implement Q&A creation
- [ ] Implement Q&A deletion
- [ ] Test FAQ management

### Outcome Management
- [ ] Create outcome list view
- [ ] Create outcome edit view
- [ ] Implement outcome creation
- [ ] Test outcome management

### Authorization & Audit
- [ ] Implement role-based access control
- [ ] Restrict admin to authorized users
- [ ] Implement audit logging
- [ ] Test authorization rules

---

## Phase 7: Data Migration & Validation (Weeks 27-28)

### Data Validation
- [ ] Run data integrity checks
- [ ] Compare Django vs .NET query results
- [ ] Validate all entity relationships
- [ ] Check for missing data
- [ ] Validate data types and formats
- [ ] Check constraint enforcement
- [ ] Test cascade deletes

### Migration Scripts
- [ ] Create any necessary data transformation scripts
- [ ] Document migration procedures
- [ ] Create rollback procedures
- [ ] Test migration scripts in staging

### End-to-End Testing
- [ ] Create E2E test scenarios
- [ ] Test complete user workflows
- [ ] Test all API endpoints
- [ ] Test background jobs end-to-end
- [ ] Test admin panel workflows
- [ ] Test error scenarios

### Performance Testing
- [ ] Set up load testing environment
- [ ] Create load test scripts (k6/JMeter)
- [ ] Run baseline Django performance tests
- [ ] Run .NET performance tests
- [ ] Compare results
- [ ] Optimize bottlenecks
- [ ] Document performance benchmarks

### Security Testing
- [ ] Run OWASP ZAP automated scans
- [ ] Perform manual penetration testing
- [ ] Test authentication/authorization
- [ ] Test input validation
- [ ] Test for SQL injection
- [ ] Test for XSS vulnerabilities
- [ ] Review dependency vulnerabilities
- [ ] Address security findings

### User Acceptance Testing
- [ ] Create UAT test plan
- [ ] Recruit UAT testers
- [ ] Conduct UAT sessions
- [ ] Document UAT feedback
- [ ] Fix UAT-identified bugs
- [ ] Obtain UAT sign-off

---

## Phase 8: Cutover & Deployment (Weeks 29-30)

### Pre-Deployment
- [ ] Final code review
- [ ] Final security review
- [ ] Update all documentation
- [ ] Create deployment runbook
- [ ] Create rollback plan
- [ ] Schedule maintenance window
- [ ] Notify stakeholders
- [ ] Brief support team

### Staging Deployment
- [ ] Deploy to staging environment
- [ ] Run smoke tests in staging
- [ ] Test all integrations in staging
- [ ] Run load tests in staging
- [ ] Fix any staging issues
- [ ] Get staging sign-off

### Production Deployment (Blue-Green)
- [ ] Deploy .NET application (GREEN)
- [ ] Verify .NET health checks
- [ ] Route 10% traffic to .NET
- [ ] Monitor metrics and errors
- [ ] Increase to 25% traffic
- [ ] Monitor for 1 hour
- [ ] Increase to 50% traffic
- [ ] Monitor for 2 hours
- [ ] Increase to 100% traffic
- [ ] Monitor for 24 hours

### Post-Deployment Monitoring
- [ ] Monitor application logs
- [ ] Monitor error rates (Sentry)
- [ ] Monitor performance metrics
- [ ] Monitor database performance
- [ ] Monitor Redis cache hit rates
- [ ] Monitor Hangfire jobs
- [ ] Monitor external API calls
- [ ] Check support ticket volume

### Django Decommissioning
- [ ] Verify .NET stability (48+ hours)
- [ ] Stop Django containers
- [ ] Archive Django code
- [ ] Archive Celery configuration
- [ ] Update DNS/load balancer permanently
- [ ] Remove Django from infrastructure
- [ ] Update documentation

### Rollback (If Needed)
- [ ] Trigger: Error rate > 1% OR critical bug
- [ ] Switch load balancer back to Django
- [ ] Drain .NET connections
- [ ] Investigate root cause
- [ ] Fix .NET issues
- [ ] Redeploy and retry

---

## Post-Migration Phase

### Documentation
- [ ] Update API documentation
- [ ] Update developer documentation
- [ ] Update operations runbooks
- [ ] Create troubleshooting guide
- [ ] Document lessons learned
- [ ] Update architecture diagrams

### Knowledge Transfer
- [ ] Conduct .NET training for ops team
- [ ] Document common issues and solutions
- [ ] Create video walkthroughs
- [ ] Hand off to support team

### Optimization
- [ ] Review performance metrics
- [ ] Optimize slow queries
- [ ] Tune cache settings
- [ ] Optimize background jobs
- [ ] Review resource utilization
- [ ] Implement improvements

### Closure
- [ ] Conduct project retrospective
- [ ] Document wins and challenges
- [ ] Celebrate team success
- [ ] Close out project budget
- [ ] Archive project artifacts
- [ ] Formal project sign-off

---

## Ongoing Maintenance

### Monitoring
- [ ] Set up monitoring dashboards
- [ ] Configure alerting rules
- [ ] Review logs weekly
- [ ] Monitor cost metrics
- [ ] Track performance trends

### Updates
- [ ] Keep NuGet packages updated
- [ ] Monitor security advisories
- [ ] Apply security patches
- [ ] Test updates in staging first

---

## Checklist Summary

| Phase | Total Tasks | Estimated Weeks |
|-------|-------------|-----------------|
| Pre-Migration | ~30 | 2 |
| Phase 1: Foundation | ~40 | 4 |
| Phase 2: Auth & Core | ~35 | 4 |
| Phase 3: Call Center | ~45 | 6 |
| Phase 4: SMS & Email | ~40 | 4 |
| Phase 5: Background Jobs | ~25 | 4 |
| Phase 6: Admin Panel | ~30 | 4 |
| Phase 7: Validation | ~30 | 2 |
| Phase 8: Cutover | ~35 | 2 |
| Post-Migration | ~20 | 2 |
| **TOTAL** | **~330 tasks** | **34 weeks** |

---

**Notes:**
- Check off tasks as they are completed
- Add notes/blockers for each task as needed
- Update estimated completion dates
- Escalate blockers to technical lead immediately
- Review checklist weekly in team meetings

**Last Updated:** January 2026  
**Project Manager:** TBD  
**Technical Lead:** TBD
