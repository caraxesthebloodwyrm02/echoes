# Creative Corner - Security & Management System

## Overview

The Creative Corner is an enhanced educational zone with comprehensive identification, security, and equipment management features. This system ensures safe, organized, and accountable use of creative resources.

## Key Features

### 1. User Identification & Access Control
- **Multi-level Access System**: Visitor, Student, Instructor, Admin
- **Secure Token-Based Authentication**: SHA-256 hashed access tokens
- **Equipment Certifications**: Track user qualifications for specialized equipment
- **Access Restrictions**: Temporary or permanent restrictions with expiration tracking
- **Activity Logging**: Complete audit trail of all access attempts

### 2. Equipment Management
- **Comprehensive Inventory Tracking**: All equipment cataloged with unique IDs
- **Status Monitoring**: Available, In Use, Maintenance, Damaged, Missing
- **Check-out/Check-in System**: Track who has what equipment and when
- **Certification Requirements**: Restrict dangerous equipment to certified users
- **Damage Reporting**: Document equipment issues with severity levels
- **Maintenance Scheduling**: Track maintenance history and schedules
- **Usage Analytics**: Monitor equipment utilization patterns

### 3. Session Management
- **Session Tracking**: Record all Creative Corner usage sessions
- **Purpose Documentation**: Track what users are working on
- **Collaborative Sessions**: Support multiple users working together
- **Session Notes**: Add observations and progress notes
- **Duration Tracking**: Automatic calculation of session lengths
- **Equipment Association**: Link equipment usage to specific sessions

### 4. Safety & Incident Management
- **Incident Logging**: Document safety issues and violations
- **Severity Classification**: Low, Medium, High, Critical levels
- **Resolution Tracking**: Monitor incident resolution status
- **Automatic Alerts**: Equipment damage triggers incident reports
- **Historical Records**: Complete incident history for analysis

## System Architecture

```
CreativeCornerSecurity (Main System)
├── User Management
│   ├── User Registration
│   ├── Access Verification
│   ├── Certification Management
│   └── Restriction Tracking
├── Equipment Management
│   ├── Inventory Control
│   ├── Check-out/Check-in
│   ├── Damage Reporting
│   └── Maintenance Tracking
├── Session Management
│   ├── Session Creation
│   ├── Activity Tracking
│   ├── Collaboration Support
│   └── Duration Monitoring
└── Security & Analytics
    ├── Incident Logging
    ├── Access Logging
    ├── Usage Reports
    └── Security Audits
```

## User Roles & Access Levels

### Visitor
- Limited access to basic equipment
- Supervised sessions only
- No certification privileges

### Student
- Standard access to general equipment
- Can earn certifications for specialized equipment
- Independent sessions allowed

### Instructor
- Full access to all equipment
- Can certify students
- Can report and resolve incidents

### Admin
- Complete system access
- User management privileges
- Equipment and system configuration

## Equipment Categories

### Art Supplies
- Paint sets, brushes, canvases
- Drawing tablets, styluses
- No certification required

### Digital Fabrication
- **3D Printers** (Certification Required)
- **Laser Cutters** (Certification Required)
- **CNC Machines** (Certification Required)

### Textiles
- **Sewing Machines** (Certification Required)
- Fabric, thread, patterns
- Hand tools (no certification)

### Photography
- Digital cameras
- Lighting equipment
- Tripods and accessories

### Music
- Instruments
- Recording equipment
- Audio interfaces

## Usage Workflow

### Starting a Session

1. **User Arrives**
   ```python
   # Verify user identity
   success, message = cc.verify_user(user_id, access_token)
   ```

2. **Start Session**
   ```python
   # Create new session
   session_id, message = cc.start_session(user_id, "Sculpture project")
   ```

3. **Check Out Equipment**
   ```python
   # Check out needed equipment
   success, msg = cc.check_out_equipment(equipment_id, user_id, session_id)
   ```

4. **Work on Project**
   ```python
   # Add notes during session
   cc.add_session_note(session_id, "Completed base structure")
   ```

5. **Check In Equipment**
   ```python
   # Return equipment
   cc.check_in_equipment(equipment_id, condition="good")
   ```

6. **End Session**
   ```python
   # Close session
   cc.end_session(session_id)
   ```

### Reporting Issues

```python
# Report equipment damage
cc.report_equipment_damage(
    equipment_id="eq_3dprinter",
    reported_by="student001",
    description="Nozzle clogged",
    severity="medium"
)

# Log safety incident
cc.log_incident(
    description="Minor burn from hot glue gun",
    severity=IncidentSeverity.LOW,
    reported_by="student002"
)
```

## Security Features

### Access Token Generation
- Unique SHA-256 hash for each user
- Combines user ID, name, and random secret
- 64-character hexadecimal string
- Cannot be reverse-engineered

### Certification System
- Equipment-specific certifications
- Tracks certifying instructor
- Certification date recorded
- Prevents unauthorized equipment use

### Restriction Management
- Temporary restrictions with expiration
- Permanent restrictions for serious violations
- Automatic enforcement during verification
- Detailed reason tracking

### Audit Trail
- All access attempts logged
- Equipment check-out/check-in recorded
- Session activities tracked
- Incident reports maintained

## Analytics & Reporting

### Security Report
```python
report = cc.get_security_report()
```

Provides:
- Total users (active, restricted)
- Equipment status (available, in use, damaged)
- Session statistics (active, total)
- Incident counts (total, unresolved)

### User Activity Report
```python
activity = cc.get_user_activity(user_id)
```

Provides:
- Total sessions
- Total duration
- Certifications earned
- Restriction history
- Last access time

## CLI Management Tool

The Creative Corner includes a comprehensive CLI tool for system management:

```bash
python scripts/manage_creative_corner.py
```

### Features:
1. **User Management**: Register, verify, certify users
2. **Equipment Management**: Add, check-out, maintain equipment
3. **Session Management**: Start, end, track sessions
4. **Incident Management**: Log, resolve incidents
5. **Reports**: Generate security and usage reports

## API Reference

### User Management

```python
# Register new user
user = cc.register_user(
    user_id="student001",
    name="Alice Johnson",
    role="student",
    access_level=AccessLevel.STUDENT,
    contact="alice@school.edu"
)

# Verify user
success, message = cc.verify_user(user_id, access_token)

# Certify user for equipment
cc.certify_user(user_id, equipment_type, certified_by)

# Add restriction
user.add_restriction(restriction, reason, duration_days)
```

### Equipment Management

```python
# Add equipment
equipment = cc.add_equipment(
    equipment_id="eq_laser01",
    name="Laser Cutter",
    category="laser_cutting",
    requires_certification=True
)

# Check out equipment
success, msg = cc.check_out_equipment(equipment_id, user_id, session_id)

# Check in equipment
success, msg = cc.check_in_equipment(equipment_id, condition="good")

# Report damage
cc.report_equipment_damage(equipment_id, reported_by, description, severity)
```

### Session Management

```python
# Start session
session_id, msg = cc.start_session(user_id, purpose)

# Add note
cc.add_session_note(session_id, note)

# End session
success, msg = cc.end_session(session_id)
```

### Incident Management

```python
# Log incident
cc.log_incident(description, severity, reported_by, details)

# Resolve incident
cc.resolve_incident(incident_id, resolution)
```

## Data Storage

All data is stored in JSON format under `data/creative_corner/`:

- **users.json**: User profiles and credentials
- **equipment.json**: Equipment inventory and status
- **sessions.json**: Active and historical sessions
- **incidents.json**: Incident reports
- **access_log.json**: Access attempt audit trail

## Testing

Comprehensive test suite included:

```bash
# Run all Creative Corner tests
pytest tests/test_creative_corner.py -v

# Run specific test class
pytest tests/test_creative_corner.py::TestUserManagement -v

# Run with coverage
pytest tests/test_creative_corner.py --cov=src.modules.creative_corner
```

## Best Practices

### For Administrators

1. **Regular Audits**: Review access logs and incident reports weekly
2. **Equipment Maintenance**: Schedule regular maintenance checks
3. **Certification Updates**: Keep user certifications current
4. **Incident Response**: Resolve incidents promptly
5. **Data Backups**: Regularly backup all JSON data files

### For Instructors

1. **Verify Certifications**: Always check user certifications before equipment use
2. **Document Issues**: Report all equipment problems immediately
3. **Monitor Sessions**: Keep track of active sessions
4. **Safety First**: Log any safety concerns as incidents

### For Students

1. **Proper Check-in**: Always check in equipment when finished
2. **Report Damage**: Immediately report any equipment issues
3. **Follow Restrictions**: Respect certification requirements
4. **Document Work**: Add session notes for project continuity

## Security Considerations

### Data Protection
- Access tokens stored securely
- No plaintext passwords
- Audit logs are append-only
- Regular security reports

### Physical Security
- Equipment tagged with unique IDs
- Check-out system prevents theft
- Damage reports create accountability
- Incident logging deters misuse

### Privacy
- User contact information protected
- Session details confidential
- Access logs for security only
- GDPR-compliant data handling

## Future Enhancements

### Planned Features
- [ ] RFID card integration for faster check-in
- [ ] Real-time equipment location tracking
- [ ] Automated maintenance scheduling
- [ ] Mobile app for session management
- [ ] Integration with school ID system
- [ ] Email notifications for incidents
- [ ] Advanced analytics dashboard
- [ ] Equipment reservation system

### Integration Opportunities
- School calendar system
- Student information system
- Inventory management
- Notification services
- Access control hardware

## Troubleshooting

### Common Issues

**User Cannot Access Equipment**
- Check certification status
- Verify no active restrictions
- Confirm equipment is available
- Check access token validity

**Equipment Shows Wrong Status**
- Verify check-in was completed
- Check for unreported damage
- Review maintenance schedule
- Audit recent transactions

**Session Won't Start**
- Verify user credentials
- Check for active restrictions
- Ensure user exists in system
- Review access logs

## Support & Contact

For questions or issues:
- Check this documentation
- Review test files for examples
- Run CLI tool for interactive help
- Contact system administrator

---

**Last Updated**: October 2025
**Version**: 1.0.0
**Status**: Production Ready
