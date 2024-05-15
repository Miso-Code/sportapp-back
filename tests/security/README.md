# Security Tests

This document describes the security tests that are performed on the project. The tests involve the use of various
techniques and tools to ensure that the project is secure.

## Table of Contents

- [Static Code Analysis](#static-code-analysis)
  - [SonarCloud](#sonarcloud)
    - [Adverse Incidents](#adverse-incidents)
    - [Adverse Incidents Provider](#adverse-incidents-provider)
    - [Alerts](#alerts)
    - [Authorizer](#authorizer)
    - [Business Partners](#business-partners)
    - [Miso Stripe](#miso-stripe)
    - [Nutritional Plans](#nutritional-plans)
    - [Sport Events](#sport-events)
    - [Sport Sessions](#sport-sessions)
    - [Sports](#sports)
    - [Training Plans](#training-plans)
    - [Users](#users)
  - [Snyk](#snyk)
  - [Clair (AWS ECR)](#clair-aws-ecr)
  - [Dependabot](#dependabot)
  - [Configuration](#dependabot-configuration)
  - [GitGuardian](#gitguardian)
  - [AWS Secrets Manager](#aws-secrets-manager)
  - [OWASP ZAP](#owasp-zap)
- [Dependency Scanning](#dependency-scanning)
    - [Snyk](#snyk)
    - [Clair (AWS ECR)](#clair-aws-ecr)
- [Dependency Updates](#dependency-updates)
    - [Dependabot](#dependabot)
    - [Configuration](#dependabot-configuration)
- [Secrets Scanning](#secrets-scanning)
    - [GitGuardian](#gitguardian)
- [Secrets Management](#secrets-management)
    - [AWS Secrets Manager](#aws-secrets-manager)
- [Penetration Testing](#penetration-testing)
    - [OWASP ZAP](#owasp-zap)

## Static Code Analysis

Static code analysis is the process of analyzing the source code of a program without executing it. It checks for
potential security vulnerabilities, code smells, and bugs in the code. Static code analysis tools can help identify
security vulnerabilities in the code early in the development process, making it easier to fix them before they become
problems.

### SonarCloud

The static code analysis is performed using SonarCloud. SonarCloud is a cloud-based code analysis tool that provides
detailed reports on the quality of the code. It checks for code smells, bugs, and security vulnerabilities in the code.

We created a SonarCloud organization and connected it to the GitHub repository. The SonarCloud GitHub app is installed
on the repository, and it automatically analyzes the code on every push to the repository.

You can see next the SonarCloud badges for each project. It will show the security rating of the project (A, B, C, D, or
F). A security rating of A is the best, while a security rating of F is the worst. The security rating is calculated
based on the number of security vulnerabilities found in the code.

#### Adverse Incidents

[![Adverse Incidents](https://sonarcloud.io/api/project_badges/measure?project=misocode_sportapp-back-adverse-incidents&metric=security_rating)](https://sonarcloud.io/dashboard?id=misocode_sportapp-back-adverse-incidents)

#### Adverse Incidents Provider

[![Adverse Incidents Provider](https://sonarcloud.io/api/project_badges/measure?project=misocode_sportapp-back-adverse-incidents-provider&metric=security_rating)](https://sonarcloud.io/dashboard?id=misocode_sportapp-back-adverse-incidents-provider)

#### Alerts

[![Alerts](https://sonarcloud.io/api/project_badges/measure?project=misocode_sportapp-back-alerts&metric=security_rating)](https://sonarcloud.io/dashboard?id=misocode_sportapp-back-alerts)

#### Authorizer

[![Authorizer](https://sonarcloud.io/api/project_badges/measure?project=misocode_sportapp-back-authorizer&metric=security_rating)](https://sonarcloud.io/dashboard?id=misocode_sportapp-back-authorizer)

#### Business Partners

[![Business Partners](https://sonarcloud.io/api/project_badges/measure?project=misocode_sportapp-back-business-partners&metric=security_rating)](https://sonarcloud.io/dashboard?id=misocode_sportapp-back-business-partners)

#### Miso Stripe

[![Miso Stripe](https://sonarcloud.io/api/project_badges/measure?project=misocode_sportapp-back-miso-stripe&metric=security_rating)](https://sonarcloud.io/dashboard?id=misocode_sportapp-back-miso-stripe)

#### Nutritional Plans

[![Nutritional Plans](https://sonarcloud.io/api/project_badges/measure?project=misocode_sportapp-back-nutritional-plan&metric=security_rating)](https://sonarcloud.io/dashboard?id=misocode_sportapp-back-nutritional-plan)

#### Sport Events

[![Sport Events](https://sonarcloud.io/api/project_badges/measure?project=misocode_sportapp-back-sport-events&metric=security_rating)](https://sonarcloud.io/dashboard?id=misocode_sportapp-back-sport-events)

#### Sport Sessions

[![Sport Sessions](https://sonarcloud.io/api/project_badges/measure?project=misocode_sportapp-back-sport-sessions&metric=security_rating)](https://sonarcloud.io/dashboard?id=misocode_sportapp-back-sport-sessions)

#### Sports

[![Sports](https://sonarcloud.io/api/project_badges/measure?project=misocode_sportapp-back-sports&metric=security_rating)](https://sonarcloud.io/dashboard?id=misocode_sportapp-back-sports)

#### Training Plans

[![Training Plans](https://sonarcloud.io/api/project_badges/measure?project=misocode_sportapp-back-training-plan&metric=security_rating)](https://sonarcloud.io/dashboard?id=misocode_sportapp-back-training-plan)

#### Users

[![Users](https://sonarcloud.io/api/project_badges/measure?project=misocode_sportapp-back-users&metric=security_rating)](https://sonarcloud.io/dashboard?id=misocode_sportapp-back-users)

## Dependency Scanning

Dependency scanning is the process of analyzing the dependencies of a project to identify security vulnerabilities in
the dependencies. It checks for known security vulnerabilities in the dependencies and provides information on how to
fix them. Dependency scanning tools can help identify and fix security vulnerabilities in the dependencies early in the
development process.

It is usually used to scan Docker images, npm packages, Maven dependencies, and other types of dependencies.

### Snyk

Snyk is a dependency scanning tool that checks for known security vulnerabilities in the dependencies of a project. It
scans the dependencies of a project and provides information on the vulnerabilities found in the dependencies.

![Snyk Report](resources/snyk.png)
![AWS ECR Scan](resources/aws_ecr.png)
![Dependabot Report](resources/dependabot_report.png)
![GitGuardian Scan](resources/git_guardian.png)
![AWS Secrets Manager](resources/secrets_manager.png)
![OWASP ZAP](resources/zap.png)
![API Gateway Authorizer](resources/api_gateway_authorizer.png)

### Clair (AWS ECR)

Clair is an open-source vulnerability scanner that scans Docker images for known security vulnerabilities. It checks the
Docker images stored in the Amazon Elastic Container Registry (ECR) for known security vulnerabilities and provides
information on the vulnerabilities found in the images.

This scan is enabled by default in AWS ECR and runs automatically when a new image is pushed to the ECR.

![img.png](resources/aws_ecr.png)

## Dependency Updates

### Dependabot

![img.png](resources/dependabot_report.png)

Dependabot is a GitHub app that creates pull requests to keep your dependencies secure and up-to-date. It checks for
updates to your dependencies every day and opens individual pull requests for each update. You can configure Dependabot
to create pull requests for updates to a specific package ecosystem, directory, or package type.

### Dependabot configuration

The Dependabot configuration is stored in the `.github/dependabot.yml` file in the repository. The configuration file
specifies the package ecosystems, directories, and schedules for the dependency updates.

```yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "daily"
  - package-ecosystem: "poetry"
    directory: "/projects/adverse-incidents"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    target-branch: "develop"
  - package-ecosystem: "poetry"
    directory: "/projects/adverse-incidents-provider"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    target-branch: "develop"
  - package-ecosystem: "poetry"
    directory: "/projects/alerts"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    target-branch: "develop"
  - package-ecosystem: "poetry"
    directory: "/projects/authorizer"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    target-branch: "develop"
  - package-ecosystem: "poetry"
    directory: "/projects/business-partners"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    target-branch: "develop"
  - package-ecosystem: "npm"
    directory: "/projects/miso-stripe"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    target-branch: "develop"
  - package-ecosystem: "poetry"
    directory: "/projects/nutritional-plans"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    target-branch: "develop"
  - package-ecosystem: "poetry"
    directory: "/projects/sport-events"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    target-branch: "develop"
  - package-ecosystem: "poetry"
    directory: "/projects/sport-sessions"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    target-branch: "develop"
  - package-ecosystem: "poetry"
    directory: "/projects/sports"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    target-branch: "develop"
  - package-ecosystem: "poetry"
    directory: "/projects/training-plans"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    target-branch: "develop"
  - package-ecosystem: "poetry"
    directory: "/projects/users"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    target-branch: "develop"

```

## Secrets Scanning

Secrets scanning is the process of scanning the codebase for secrets such as API keys, passwords, and other sensitive
information. It checks for secrets in the codebase and provides information on the secrets found in the code.

### GitGuardian

GitGuardian is a secrets scanning tool that scans the codebase for secrets such as API keys, passwords, and other
sensitive information. It checks for secrets in the codebase and provides information on the secrets found in the code.

![img_2.png](resources/git_guardian.png)

## Secrets Management

Secrets management is the process of securely storing and managing secrets such as API keys, passwords, and other
sensitive information. It ensures that the secrets are stored securely and are only accessible to authorized users.

### AWS Secrets Manager

AWS Secrets Manager is a secrets management service that securely stores and manages secrets such as API keys,
passwords, and other sensitive information. It encrypts the secrets and stores them securely in the AWS cloud. The
secrets can be accessed programmatically using the AWS SDK or the AWS CLI.

![img.png](resources/secrets_manager.png)

## Penetration Testing

Penetration testing is the process of testing the security of a system by simulating an attack on the system. It checks
for security vulnerabilities in the system and provides information on how to fix them. Penetration testing tools can
help identify and fix security vulnerabilities in the system before they become problems.

### OWASP ZAP

OWASP ZAP is a penetration testing tool that checks for security vulnerabilities in web applications. It simulates an
attack on the web application and checks for security vulnerabilities such as cross-site scripting (XSS), SQL injection,
and other vulnerabilities. It provides detailed reports on the security vulnerabilities found in the web application.

![img.png](resources/zap.png)

## Permissions

All the applications have the necessary permissions to access the resources they need. The permissions are managed using
lambda Authorizers and JWT tokens. The Authorizers check the JWT tokens and verify the permissions of the applications
before allowing access to the resources.

All of this is done through the AWS API Gateway, which acts as a facade for the applications and manages the permissions
and access control.

![img.png](resources/api_gateway_authorizer.png)

Every request that does not pass the Authorizer will be rejected with a `401 Unauthorized` response with the following body:

```json
{
  "message": "Unauthorized"
}
```

## Conclusion

The security tests described in this document help ensure that the project is secure. The tests involve the use of
various techniques and tools to identify and fix security vulnerabilities in the project. By performing these tests
regularly, we can ensure that the project is secure and that the data is protected from unauthorized access.
