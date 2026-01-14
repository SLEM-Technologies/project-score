# .NET Core 10 Solution Scaffold
## Initial Project Structure for VetSuccess Migration

This document outlines the initial .NET Core 10 solution structure to be created as the foundation for the Django-to-.NET migration.

---

## Solution Structure

```
VetSuccess/
├── VetSuccess.sln
├── README.md
├── .gitignore
├── .editorconfig
├── Directory.Build.props
│
├── src/
│   ├── VetSuccess.API/
│   ├── VetSuccess.Core/
│   ├── VetSuccess.Infrastructure/
│   └── VetSuccess.Jobs/
│
├── tests/
│   ├── VetSuccess.UnitTests/
│   ├── VetSuccess.IntegrationTests/
│   └── VetSuccess.ApiTests/
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── docs/
    ├── api/
    └── architecture/
```

---

## Project Details

### 1. VetSuccess.API (ASP.NET Core Web API)

**Purpose**: REST API layer, controllers, middleware

**Key Files:**
```
VetSuccess.API/
├── Controllers/
│   ├── V1/
│   │   ├── AuthController.cs
│   │   ├── CallCenterController.cs
│   │   ├── ClientController.cs
│   │   ├── OutcomeController.cs
│   │   ├── PracticeController.cs
│   │   └── SmsController.cs
│   └── HealthController.cs
│
├── Middleware/
│   ├── ErrorHandlingMiddleware.cs
│   ├── RequestLoggingMiddleware.cs
│   └── PerformanceMonitoringMiddleware.cs
│
├── Filters/
│   ├── ValidateModelStateAttribute.cs
│   └── ApiExceptionFilterAttribute.cs
│
├── Extensions/
│   ├── ServiceCollectionExtensions.cs
│   └── ApplicationBuilderExtensions.cs
│
├── Program.cs
├── appsettings.json
├── appsettings.Development.json
├── appsettings.Production.json
└── VetSuccess.API.csproj
```

**VetSuccess.API.csproj:**
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <DockerDefaultTargetOS>Linux</DockerDefaultTargetOS>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="10.0.0" />
    <PackageReference Include="Microsoft.AspNetCore.Mvc.Versioning" Version="5.1.0" />
    <PackageReference Include="Swashbuckle.AspNetCore" Version="7.0.0" />
    <PackageReference Include="Serilog.AspNetCore" Version="9.0.0" />
    <PackageReference Include="Serilog.Sinks.Console" Version="6.0.0" />
    <PackageReference Include="Serilog.Sinks.File" Version="6.0.0" />
    <PackageReference Include="AspNetCoreRateLimit" Version="5.0.0" />
    <PackageReference Include="Hangfire.AspNetCore" Version="1.8.0" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\VetSuccess.Core\VetSuccess.Core.csproj" />
    <ProjectReference Include="..\VetSuccess.Infrastructure\VetSuccess.Infrastructure.csproj" />
    <ProjectReference Include="..\VetSuccess.Jobs\VetSuccess.Jobs.csproj" />
  </ItemGroup>

</Project>
```

---

### 2. VetSuccess.Core (Domain/Business Logic)

**Purpose**: Domain entities, business logic, interfaces

**Key Files:**
```
VetSuccess.Core/
├── Entities/
│   ├── BaseEntity.cs
│   ├── User.cs
│   ├── Practice.cs
│   ├── PracticeSettings.cs
│   ├── Client.cs
│   ├── Patient.cs
│   ├── Appointment.cs
│   ├── Phone.cs
│   ├── Email.cs
│   ├── Reminder.cs
│   ├── Question.cs
│   ├── Answer.cs
│   ├── Outcome.cs
│   ├── SMSEvent.cs
│   ├── SMSHistory.cs
│   ├── SMSTemplate.cs
│   └── UpdatesEmailEvent.cs
│
├── Interfaces/
│   ├── Repositories/
│   │   ├── IRepository.cs
│   │   ├── IClientRepository.cs
│   │   ├── IPracticeRepository.cs
│   │   └── ISmsRepository.cs
│   ├── Services/
│   │   ├── IAuthService.cs
│   │   ├── ICallCenterService.cs
│   │   ├── ISmsService.cs
│   │   ├── IEmailService.cs
│   │   └── ICacheService.cs
│   └── External/
│       ├── IDialpadService.cs
│       ├── ISendGridService.cs
│       └── IAzureBlobService.cs
│
├── Services/
│   ├── AuthService.cs
│   ├── CallCenterService.cs
│   ├── SmsService.cs
│   ├── EmailService.cs
│   └── CacheService.cs
│
├── DTOs/
│   ├── Auth/
│   │   ├── LoginRequest.cs
│   │   ├── TokenResponse.cs
│   │   └── RefreshTokenRequest.cs
│   ├── CallCenter/
│   │   ├── ClientDto.cs
│   │   ├── PracticeDto.cs
│   │   ├── AppointmentDto.cs
│   │   └── FAQDto.cs
│   └── Sms/
│       ├── SMSHistoryDto.cs
│       └── SMSTemplateDto.cs
│
├── Enums/
│   ├── ReminderStatus.cs
│   ├── SMSHistoryStatus.cs
│   └── UserRole.cs
│
├── Exceptions/
│   ├── VetSuccessException.cs
│   ├── NotFoundException.cs
│   ├── ValidationException.cs
│   └── UnauthorizedException.cs
│
├── Constants/
│   ├── ErrorMessages.cs
│   ├── CacheKeys.cs
│   └── SMSVariables.cs
│
└── VetSuccess.Core.csproj
```

**VetSuccess.Core.csproj:**
```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="AutoMapper" Version="13.0.0" />
    <PackageReference Include="FluentValidation" Version="11.10.0" />
  </ItemGroup>

</Project>
```

---

### 3. VetSuccess.Infrastructure (Data Access & External Services)

**Purpose**: Database access, external integrations, caching

**Key Files:**
```
VetSuccess.Infrastructure/
├── Data/
│   ├── VetSuccessDbContext.cs
│   ├── Configurations/
│   │   ├── UserConfiguration.cs
│   │   ├── PracticeConfiguration.cs
│   │   ├── ClientConfiguration.cs
│   │   ├── PatientConfiguration.cs
│   │   └── SMSHistoryConfiguration.cs
│   └── Migrations/
│       └── (EF Core migrations)
│
├── Repositories/
│   ├── Repository.cs
│   ├── ClientRepository.cs
│   ├── PracticeRepository.cs
│   └── SmsRepository.cs
│
├── ExternalServices/
│   ├── Dialpad/
│   │   ├── DialpadService.cs
│   │   └── DialpadClient.cs
│   ├── SendGrid/
│   │   ├── SendGridEmailService.cs
│   │   └── EmailTemplates/
│   └── Azure/
│       └── AzureBlobStorageService.cs
│
├── Caching/
│   ├── RedisCacheService.cs
│   └── CacheKeyGenerator.cs
│
├── Identity/
│   ├── JwtTokenGenerator.cs
│   └── PasswordHasher.cs
│
└── VetSuccess.Infrastructure.csproj
```

**VetSuccess.Infrastructure.csproj:**
```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="9.0.0" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.Design" Version="9.0.0" />
    <PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="9.0.0" />
    <PackageReference Include="Microsoft.Extensions.Caching.StackExchangeRedis" Version="10.0.0" />
    <PackageReference Include="Azure.Storage.Blobs" Version="12.20.0" />
    <PackageReference Include="SendGrid" Version="9.29.0" />
    <PackageReference Include="Sentry.AspNetCore" Version="4.0.0" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\VetSuccess.Core\VetSuccess.Core.csproj" />
  </ItemGroup>

</Project>
```

---

### 4. VetSuccess.Jobs (Background Jobs)

**Purpose**: Hangfire background jobs, scheduled tasks

**Key Files:**
```
VetSuccess.Jobs/
├── Jobs/
│   ├── SmsEventCreationJob.cs
│   ├── DailyEmailUpdatesJob.cs
│   └── DataCleanupJob.cs
│
├── Configuration/
│   ├── HangfireConfiguration.cs
│   └── JobScheduler.cs
│
└── VetSuccess.Jobs.csproj
```

**VetSuccess.Jobs.csproj:**
```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Hangfire.Core" Version="1.8.0" />
    <PackageReference Include="Hangfire.PostgreSql" Version="1.20.0" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\VetSuccess.Core\VetSuccess.Core.csproj" />
    <ProjectReference Include="..\VetSuccess.Infrastructure\VetSuccess.Infrastructure.csproj" />
  </ItemGroup>

</Project>
```

---

### 5. Test Projects

**VetSuccess.UnitTests.csproj:**
```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.10.0" />
    <PackageReference Include="xUnit" Version="2.9.0" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.0" />
    <PackageReference Include="Moq" Version="4.20.0" />
    <PackageReference Include="FluentAssertions" Version="7.0.0" />
    <PackageReference Include="coverlet.collector" Version="6.0.0" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\..\src\VetSuccess.Core\VetSuccess.Core.csproj" />
    <ProjectReference Include="..\..\src\VetSuccess.Infrastructure\VetSuccess.Infrastructure.csproj" />
  </ItemGroup>

</Project>
```

**VetSuccess.IntegrationTests.csproj:**
```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.10.0" />
    <PackageReference Include="xUnit" Version="2.9.0" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.0" />
    <PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="10.0.0" />
    <PackageReference Include="Testcontainers.PostgreSql" Version="3.10.0" />
    <PackageReference Include="Respawn" Version="6.2.0" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\..\src\VetSuccess.API\VetSuccess.API.csproj" />
  </ItemGroup>

</Project>
```

---

## Docker Configuration

**Dockerfile:**
```dockerfile
# Build stage
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# Copy solution and project files
COPY VetSuccess.sln .
COPY src/VetSuccess.API/VetSuccess.API.csproj src/VetSuccess.API/
COPY src/VetSuccess.Core/VetSuccess.Core.csproj src/VetSuccess.Core/
COPY src/VetSuccess.Infrastructure/VetSuccess.Infrastructure.csproj src/VetSuccess.Infrastructure/
COPY src/VetSuccess.Jobs/VetSuccess.Jobs.csproj src/VetSuccess.Jobs/

# Restore dependencies
RUN dotnet restore

# Copy everything else
COPY . .

# Build
WORKDIR /src/src/VetSuccess.API
RUN dotnet build -c Release -o /app/build

# Publish
FROM build AS publish
RUN dotnet publish -c Release -o /app/publish /p:UseAppHost=false

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final
WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

COPY --from=publish /app/publish .

EXPOSE 8000
ENV ASPNETCORE_URLS=http://+:8000

ENTRYPOINT ["dotnet", "VetSuccess.API.dll"]
```

**docker-compose.yml (updated for both Django and .NET):**
```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    hostname: vetsuccess-db
    container_name: heartland-db
    environment:
      POSTGRES_DB: vetsuccess_db
      POSTGRES_USER: developer
      POSTGRES_PASSWORD: local
    ports:
      - "6011:5432"
    volumes:
      - pg-data:/var/lib/postgresql/data

  redis:
    container_name: heartland-redis
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  # Django backend (existing - to be deprecated)
  backend-django:
    image: heartland-backend
    container_name: heartland-backend-django
    build: services/backend/
    env_file:
      - ./.env
    ports:
      - "5011:8000"
    volumes:
      - ./services/backend/service:/home/appuser/project/service
    depends_on:
      - db
      - redis
    command: /bin/bash -c '
      chmod +x ../wait-for.sh &&
      ../wait-for.sh vetsuccess-db:5432 &&
      python manage.py migrate &&
      python manage.py collectstatic --no-input &&
      python manage.py runserver 0.0.0.0:8000'

  # .NET backend (new)
  backend-dotnet:
    image: vetsuccess-dotnet
    container_name: heartland-backend-dotnet
    build:
      context: ./VetSuccess
      dockerfile: docker/Dockerfile
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__VetSuccessDb=Host=vetsuccess-db;Port=5432;Database=vetsuccess_db;Username=developer;Password=local
      - Redis__Configuration=heartland-redis:6379,defaultDatabase=1
    ports:
      - "5012:8000"
    depends_on:
      - db
      - redis

  # Celery worker (Django - to be deprecated)
  worker:
    image: heartland-backend
    container_name: heartland-worker
    env_file:
      - ./.env
    depends_on:
      - redis
      - db
    working_dir: /home/appuser/project/service
    entrypoint: ['celery']
    command: ['-A', 'libs.celery.celery', 'worker', '-Q', 'low,email,sms', '--loglevel=DEBUG']

  # Celery beat (Django - to be deprecated)
  beat:
    image: heartland-backend
    container_name: heartland-beat
    env_file:
      - ./.env
    depends_on:
      - redis
      - db
    working_dir: /home/appuser/project/service
    entrypoint: ['celery']
    command: ['-A', 'libs.celery.celery', 'beat', '--loglevel=DEBUG']

volumes:
  pg-data:
  redis-data:
```

---

## Initial Setup Commands

```bash
# Create solution
dotnet new sln -n VetSuccess

# Create projects
dotnet new webapi -n VetSuccess.API -o src/VetSuccess.API
dotnet new classlib -n VetSuccess.Core -o src/VetSuccess.Core
dotnet new classlib -n VetSuccess.Infrastructure -o src/VetSuccess.Infrastructure
dotnet new classlib -n VetSuccess.Jobs -o src/VetSuccess.Jobs

# Create test projects
dotnet new xunit -n VetSuccess.UnitTests -o tests/VetSuccess.UnitTests
dotnet new xunit -n VetSuccess.IntegrationTests -o tests/VetSuccess.IntegrationTests
dotnet new xunit -n VetSuccess.ApiTests -o tests/VetSuccess.ApiTests

# Add projects to solution
dotnet sln add src/VetSuccess.API/VetSuccess.API.csproj
dotnet sln add src/VetSuccess.Core/VetSuccess.Core.csproj
dotnet sln add src/VetSuccess.Infrastructure/VetSuccess.Infrastructure.csproj
dotnet sln add src/VetSuccess.Jobs/VetSuccess.Jobs.csproj
dotnet sln add tests/VetSuccess.UnitTests/VetSuccess.UnitTests.csproj
dotnet sln add tests/VetSuccess.IntegrationTests/VetSuccess.IntegrationTests.csproj
dotnet sln add tests/VetSuccess.ApiTests/VetSuccess.ApiTests.csproj

# Add project references
dotnet add src/VetSuccess.API/VetSuccess.API.csproj reference src/VetSuccess.Core/VetSuccess.Core.csproj
dotnet add src/VetSuccess.API/VetSuccess.API.csproj reference src/VetSuccess.Infrastructure/VetSuccess.Infrastructure.csproj
dotnet add src/VetSuccess.API/VetSuccess.API.csproj reference src/VetSuccess.Jobs/VetSuccess.Jobs.csproj
dotnet add src/VetSuccess.Infrastructure/VetSuccess.Infrastructure.csproj reference src/VetSuccess.Core/VetSuccess.Core.csproj
dotnet add src/VetSuccess.Jobs/VetSuccess.Jobs.csproj reference src/VetSuccess.Core/VetSuccess.Core.csproj
dotnet add src/VetSuccess.Jobs/VetSuccess.Jobs.csproj reference src/VetSuccess.Infrastructure/VetSuccess.Infrastructure.csproj

# Install NuGet packages (see .csproj files above)

# Build solution
dotnet build

# Run tests
dotnet test

# Run API
dotnet run --project src/VetSuccess.API/VetSuccess.API.csproj
```

---

## Next Steps After Scaffold

1. **Set up EF Core DbContext**
   - Reverse engineer from existing PostgreSQL database
   - Create entity configurations

2. **Implement Base Services**
   - Authentication service with JWT
   - Caching service with Redis
   - Logging configuration with Serilog

3. **Create First Endpoint**
   - Health check endpoints
   - Auth endpoints (login, refresh token)

4. **Set up CI/CD**
   - Azure DevOps or GitHub Actions pipeline
   - Docker build and push

5. **Write First Tests**
   - Unit tests for services
   - Integration tests for API

---

This scaffold provides a solid foundation for the Django-to-.NET migration project.
