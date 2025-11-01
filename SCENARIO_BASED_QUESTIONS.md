# Scenario-Based DevOps Interview Questions - 7+ Years Experience

## Production Incident Scenarios

### Scenario 1: High Traffic Spike Causing Service Degradation
**Situation:** Your e-commerce application is experiencing a 10x traffic spike during Black Friday. Response times have increased from 200ms to 5 seconds, and some users are getting 503 errors.

**Expected Response:**
```
Immediate Actions (0-15 minutes):
1. Check monitoring dashboards (Grafana/DataDog)
2. Verify auto-scaling is functioning
3. Check database connection pools and query performance
4. Enable circuit breakers if not already active
5. Scale up critical services manually if needed

Investigation (15-30 minutes):
1. Analyze application logs for error patterns
2. Check database slow query logs
3. Monitor memory and CPU usage across services
4. Verify CDN cache hit rates
5. Check load balancer health checks

Resolution Strategy:
1. Horizontal scaling of web servers
2. Database read replica scaling
3. Cache warming for frequently accessed data
4. Rate limiting for non-critical endpoints
5. Feature flags to disable non-essential features

Long-term Improvements:
1. Implement predictive auto-scaling
2. Load testing with realistic traffic patterns
3. Database query optimization
4. Implement proper caching strategies
5. Chaos engineering to test resilience
```

### Scenario 2: Database Corruption in Production
**Situation:** Your primary PostgreSQL database has corruption in a critical table. The application is throwing errors, and you need to restore service quickly while preserving data integrity.

**Expected Response:**
```
Immediate Assessment (0-10 minutes):
1. Stop writes to the corrupted table
2. Activate read-only mode for the application
3. Check backup integrity and availability
4. Assess the scope of corruption
5. Notify stakeholders about the incident

Recovery Strategy:
1. Promote read replica to primary (if available)
2. Point application to new primary
3. Restore corrupted table from latest backup
4. Implement data validation checks
5. Gradually restore write operations

Data Integrity Verification:
1. Compare record counts between backup and current
2. Run data consistency checks
3. Validate critical business data
4. Test application functionality thoroughly
5. Monitor for any data anomalies

Prevention Measures:
1. Implement continuous backup validation
2. Set up automated corruption detection
3. Regular disaster recovery testing
4. Database health monitoring
5. Point-in-time recovery capabilities
```

### Scenario 3: Security Breach Detection
**Situation:** Your security monitoring has detected unusual API calls from an unknown IP address. The calls are accessing sensitive customer data endpoints with valid authentication tokens.

**Expected Response:**
```
Immediate Response (0-30 minutes):
1. Block suspicious IP addresses at firewall/WAF level
2. Revoke potentially compromised authentication tokens
3. Enable additional logging and monitoring
4. Preserve evidence for forensic analysis
5. Notify security team and management

Investigation Phase:
1. Analyze access logs for attack patterns
2. Check for privilege escalation attempts
3. Review recent code deployments
4. Audit user account activities
5. Scan for malware or backdoors

Containment Strategy:
1. Implement additional authentication factors
2. Rotate all API keys and secrets
3. Review and tighten access controls
4. Implement rate limiting on sensitive endpoints
5. Enable real-time security monitoring

Recovery and Hardening:
1. Patch any identified vulnerabilities
2. Implement zero-trust security model
3. Enhanced monitoring and alerting
4. Security awareness training
5. Regular penetration testing
```

## Architecture Design Scenarios

### Scenario 4: Microservices Migration Strategy
**Situation:** Your company wants to migrate a monolithic application to microservices. The application handles 100,000 daily active users and processes financial transactions.

**Expected Response:**
```
Assessment Phase:
1. Analyze current application architecture
2. Identify service boundaries using Domain-Driven Design
3. Map data dependencies and transaction flows
4. Assess team structure and capabilities
5. Define success metrics and timeline

Migration Strategy (Strangler Fig Pattern):
1. Start with least coupled components
2. Implement API gateway for routing
3. Extract services incrementally
4. Maintain data consistency during transition
5. Implement comprehensive monitoring

Technical Implementation:
1. Containerize services with Docker
2. Orchestrate with Kubernetes
3. Implement service mesh (Istio) for communication
4. Set up distributed tracing (Jaeger)
5. Implement circuit breakers and retry logic

Data Management:
1. Database per service pattern
2. Event-driven architecture for data synchronization
3. Implement saga pattern for distributed transactions
4. Data migration strategies
5. Eventual consistency handling

Operational Considerations:
1. CI/CD pipeline per service
2. Independent deployment strategies
3. Service-level monitoring and alerting
4. Distributed logging aggregation
5. Security and compliance per service
```

### Scenario 5: Multi-Cloud Disaster Recovery
**Situation:** Design a disaster recovery solution for a critical application that must have 99.99% uptime and RTO of 4 hours, RPO of 1 hour, spanning AWS and Azure.

**Expected Response:**
```
Architecture Design:
Primary Site (AWS):
- Multi-AZ deployment with auto-scaling
- RDS Multi-AZ with read replicas
- S3 with cross-region replication
- CloudFront for global distribution
- Route 53 for DNS with health checks

Secondary Site (Azure):
- Standby infrastructure (warm standby)
- Azure SQL Database with geo-replication
- Blob Storage with replication
- Azure CDN for content delivery
- Traffic Manager for failover

Data Replication Strategy:
1. Database: Continuous replication with 15-minute lag
2. File Storage: Real-time synchronization
3. Application State: Stateless design with external state store
4. Configuration: Infrastructure as Code deployment
5. Secrets: Cross-cloud secret synchronization

Failover Process:
1. Automated health monitoring across both clouds
2. DNS-based failover with 60-second TTL
3. Database promotion procedures
4. Application deployment automation
5. Traffic routing validation

Testing and Validation:
1. Monthly disaster recovery drills
2. Automated failover testing
3. Data integrity validation
4. Performance benchmarking
5. Compliance verification
```

## Performance Optimization Scenarios

### Scenario 6: Application Performance Degradation
**Situation:** Your web application's response time has gradually increased from 200ms to 2 seconds over the past month. CPU and memory usage appear normal.

**Expected Response:**
```
Performance Analysis Approach:
1. Application Performance Monitoring (APM) analysis
2. Database query performance review
3. Network latency investigation
4. Cache hit rate analysis
5. Third-party service dependency check

Investigation Tools and Techniques:
1. Distributed tracing to identify bottlenecks
2. Database slow query log analysis
3. Memory profiling for memory leaks
4. Network packet analysis
5. Load testing with realistic scenarios

Common Root Causes to Check:
1. Database query optimization needs
2. Memory leaks causing garbage collection pressure
3. Inefficient caching strategies
4. Network connectivity issues
5. Third-party API performance degradation

Optimization Strategy:
1. Database index optimization
2. Query result caching implementation
3. Connection pooling optimization
4. CDN configuration for static assets
5. Asynchronous processing for heavy operations

Monitoring and Prevention:
1. Implement performance budgets
2. Automated performance regression testing
3. Real-time performance alerting
4. Regular performance reviews
5. Capacity planning based on growth trends
```

### Scenario 7: Database Scaling Challenge
**Situation:** Your PostgreSQL database is hitting CPU limits during peak hours. Read queries are slow, and write operations are backing up. The database size is 2TB with 10,000 concurrent connections.

**Expected Response:**
```
Immediate Scaling Solutions:
1. Implement read replicas for read traffic distribution
2. Connection pooling (PgBouncer) to manage connections
3. Query optimization for expensive operations
4. Implement caching layer (Redis) for frequent queries
5. Vertical scaling as temporary measure

Long-term Architecture:
1. Database sharding strategy implementation
2. CQRS (Command Query Responsibility Segregation)
3. Event sourcing for write-heavy operations
4. Microservices with database per service
5. Polyglot persistence for different data types

Performance Optimization:
1. Index optimization and maintenance
2. Query plan analysis and optimization
3. Partitioning for large tables
4. Archive old data to reduce database size
5. Implement proper monitoring and alerting

Operational Improvements:
1. Automated backup and recovery procedures
2. Database health monitoring
3. Capacity planning and forecasting
4. Regular maintenance windows
5. Disaster recovery testing
```

## DevOps Process Scenarios

### Scenario 8: CI/CD Pipeline Failure Investigation
**Situation:** Your CI/CD pipeline has a 30% failure rate. Deployments are taking 2 hours instead of the expected 30 minutes, and developers are losing confidence in the system.

**Expected Response:**
```
Root Cause Analysis:
1. Pipeline stage failure analysis
2. Test flakiness investigation
3. Infrastructure resource constraints
4. Dependency management issues
5. Environment configuration drift

Pipeline Optimization Strategy:
1. Parallel execution of independent stages
2. Test optimization and flaky test elimination
3. Artifact caching and reuse
4. Infrastructure scaling for build agents
5. Pipeline as code implementation

Quality Improvements:
1. Implement proper test categorization (unit, integration, e2e)
2. Static code analysis integration
3. Security scanning automation
4. Performance testing integration
5. Deployment smoke tests

Monitoring and Metrics:
1. Pipeline success rate tracking
2. Build time monitoring and alerting
3. Test execution time analysis
4. Deployment frequency metrics
5. Mean time to recovery (MTTR) tracking

Developer Experience:
1. Fast feedback loops implementation
2. Clear error messaging and debugging info
3. Self-service deployment capabilities
4. Branch-based environment provisioning
5. Rollback automation
```

### Scenario 9: Infrastructure Cost Optimization
**Situation:** Your AWS bill has increased by 200% over 6 months. Management wants a 30% cost reduction without impacting performance or reliability.

**Expected Response:**
```
Cost Analysis Approach:
1. AWS Cost Explorer analysis by service and tag
2. Resource utilization monitoring
3. Reserved Instance vs On-Demand analysis
4. Data transfer cost investigation
5. Third-party cost monitoring tools

Immediate Cost Reduction Opportunities:
1. Right-sizing over-provisioned instances
2. Implementing auto-scaling policies
3. Reserved Instance purchases for predictable workloads
4. Spot Instance usage for fault-tolerant workloads
5. Unused resource identification and cleanup

Storage Optimization:
1. S3 Intelligent Tiering implementation
2. EBS volume optimization and cleanup
3. Snapshot lifecycle management
4. Data archival strategies
5. CloudFront caching optimization

Long-term Cost Management:
1. FinOps culture implementation
2. Cost allocation and chargeback systems
3. Budget alerts and governance policies
4. Regular cost optimization reviews
5. Cloud cost optimization automation

Monitoring and Governance:
1. Real-time cost monitoring dashboards
2. Cost anomaly detection and alerting
3. Resource tagging strategies
4. Cost optimization KPIs
5. Regular cost review meetings
```

## Team Leadership Scenarios

### Scenario 10: Leading a Major Infrastructure Migration
**Situation:** You're leading a team of 8 engineers to migrate from on-premises infrastructure to AWS. The migration must be completed in 6 months with zero downtime for critical services.

**Expected Response:**
```
Project Planning and Strategy:
1. Comprehensive current state assessment
2. Future state architecture design
3. Risk assessment and mitigation strategies
4. Detailed migration timeline and milestones
5. Success criteria and rollback plans

Team Organization:
1. Cross-functional team structure
2. Clear roles and responsibilities
3. Communication protocols and cadence
4. Knowledge sharing and documentation
5. Training and skill development plans

Technical Approach:
1. Hybrid cloud setup for gradual migration
2. Application dependency mapping
3. Data migration strategies
4. Network connectivity planning
5. Security and compliance requirements

Risk Management:
1. Pilot migrations for non-critical systems
2. Comprehensive testing strategies
3. Rollback procedures for each phase
4. Business continuity planning
5. Stakeholder communication plans

Change Management:
1. Staff training on new technologies
2. Process documentation updates
3. Operational runbook creation
4. Monitoring and alerting setup
5. Post-migration optimization planning
```

## Key Interview Success Factors

### Technical Depth
- Demonstrate understanding of underlying technologies
- Explain trade-offs and alternative approaches
- Show experience with real-world challenges
- Discuss scalability and performance implications

### Problem-Solving Approach
- Structured thinking and systematic analysis
- Risk assessment and mitigation strategies
- Consideration of business impact
- Long-term vs short-term solutions

### Leadership and Communication
- Clear explanation of complex technical concepts
- Stakeholder management and communication
- Team coordination and collaboration
- Decision-making under pressure

### Operational Excellence
- Monitoring and observability focus
- Automation and efficiency improvements
- Security and compliance considerations
- Continuous improvement mindset