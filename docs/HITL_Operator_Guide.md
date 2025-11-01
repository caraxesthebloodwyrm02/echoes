# HITL Operator Quick-Start Guide

## 🎯 Overview
This guide helps Human-in-the-Loop (HITL) operators effectively use the GPT-OSS:120B middleware component for real-time diagnostics and corrective actions.

## 🔍 What to Look For

### Common Failure Patterns
- **API Rate Limits**: "Rate limit exceeded" - Check usage patterns, implement backoff
- **Missing Dependencies**: "Module not found" - Verify package versions, environment consistency
- **Constraint Violations**: "Validation failed" - Review business rules, data constraints
- **Resource Exhaustion**: "Out of memory" - Scale resources, optimize queries
- **Network Timeouts**: "Connection failed" - Check connectivity, implement retries

### System Health Indicators
- **Error Rate Spikes**: >5% increase from baseline
- **Latency Degradation**: >2x normal response time
- **Resource Utilization**: >90% CPU/Memory
- **Queue Backlogs**: >100 pending requests
- **Failed Transactions**: Any non-zero failure count

## 🛠️ How to Use Glimpse

### Quick Commands
```bash
# Get contextual snippets for current failure
glimpse search "error: rate limit exceeded in payment processing"

# Get recent similar incidents
glimpse history --similar "API timeout" --last 24h

# Surface relevant documentation
glimpse docs "constraint validation patterns"
```

### Glimpse Integration Tips
- **Real-time Context**: Always include current error messages and stack traces
- **Temporal Scope**: Focus on last 30 minutes for acute issues
- **Cross-System**: Include related service statuses and dependencies
- **Pattern Matching**: Look for recurring error signatures

## ⚡ When to Trigger Offline Knowledge

### Immediate Action Triggers
- **Novel Failures**: Errors not seen in training data
- **Complex Constraints**: Multi-variable business rules
- **Regulatory Issues**: Compliance-related failures
- **Security Events**: Potential breaches or vulnerabilities

### Knowledge Sources
1. **Pre-trained Models**: GPT-OSS:120B for constraint inference
2. **Cached Solutions**: Historical successful fixes
3. **Documentation**: Internal runbooks and procedures
4. **Expert Patterns**: Common fixes from experienced operators

## 🔄 HITL Workflow Steps

### 1. Observe & Assess (0-30 seconds)
- Review error logs and system metrics
- Identify failure pattern and scope
- Check recent changes/deployments

### 2. Gather Context (30-60 seconds)
```bash
# Use Glimpse for rapid context
glimpse search "[error message]"
glimpse history --service [affected_service]
```

### 3. Infer Constraints (1-2 minutes)
- Use GPT-OSS:120B to analyze failure root cause
- Cross-reference with offline knowledge base
- Identify violated constraints or missing dependencies

### 4. Generate Solutions (2-3 minutes)
- Propose corrective actions
- Validate against business rules
- Check resource requirements

### 5. Validate & Deploy (3-5 minutes)
- Test fix in Realtime Preview canvas
- Monitor I/O ratios and performance metrics
- Deploy if validation passes

### 6. Monitor & Learn (Ongoing)
- Track fix effectiveness
- Update knowledge base with successful patterns
- Refine future detection rules

## 📊 Realtime Preview Usage

### Key Metrics to Monitor
- **I/O Ratio**: Input operations vs output results
- **Latency**: Response time before/after fix
- **Error Rate**: Failure percentage trend
- **Throughput**: Operations per second

### Validation Checklist
- [ ] Fix reduces error rate by >50%
- [ ] Latency improves or stays neutral
- [ ] No new errors introduced
- [ ] Resource usage within bounds
- [ ] Business rules still enforced

## 🚨 Emergency Procedures

### When HITL Operator is Unavailable
1. **Shadow Mode Activation**: System logs anomalies automatically
2. **Safe State Transition**: Roll back to last known good state
3. **Alert Escalation**: Notify on-call team with full context
4. **Automated Mitigations**: Apply predefined safety measures

### Critical System Protection
- **Circuit Breakers**: Automatic failover for failing services
- **Rate Limiting**: Prevent cascade failures
- **Graceful Degradation**: Maintain core functionality
- **Audit Logging**: Full trace of automated actions

## 📈 Performance Targets

### Response Time Goals
- **Detection**: <30 seconds from failure occurrence
- **Diagnosis**: <2 minutes to root cause identification
- **Resolution**: <5 minutes to validated fix deployment
- **Validation**: <1 minute via Realtime Preview

### Quality Metrics
- **Accuracy**: >95% correct constraint identification
- **Completeness**: >90% of failure modes covered
- **Efficiency**: >80% reduction in mean time to recovery (MTTR)

## 🔧 Tools & Resources

### Primary Tools
- **GPT-OSS:120B**: Main HITL inference Glimpse
- **Glimpse**: Real-time contextual search
- **Realtime Preview**: Interactive validation canvas
- **Grafana Dashboard**: System monitoring and KPIs

### Support Resources
- **Knowledge Base**: Historical fixes and patterns
- **Runbooks**: Service-specific troubleshooting guides
- **Expert Directory**: Contact information for specialists
- **Training Materials**: Onboarding and advanced techniques

## 📝 Logging & Auditing

### Required Log Entries
- Timestamp and operator identification
- Original error description and context
- Constraint inference reasoning
- Proposed and implemented solutions
- Validation results and metrics
- Lessons learned and knowledge base updates

### Compliance Requirements
- **Audit Trail**: Complete history of all HITL interventions
- **Data Privacy**: No sensitive information in logs
- **Regulatory Compliance**: Adherence to relevant standards
- **Retention Policy**: Logs retained for 7 years minimum

## 🎯 Success Metrics

### Daily KPIs
- Number of incidents resolved
- Average resolution time
- Error rate reduction percentage
- User satisfaction scores

### Weekly Reports
- Most common failure patterns
- Knowledge base utilization
- Tool effectiveness ratings
- Process improvement opportunities

Remember: The goal is rapid, accurate intervention that prevents issues from escalating while continuously learning from each interaction.
