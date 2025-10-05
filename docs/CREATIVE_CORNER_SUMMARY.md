# Creative Corner - Quick Reference

## What is it?

The Creative Corner is a secure, managed educational space for creative activities with comprehensive identification, equipment tracking, and safety features.

## Key Features at a Glance

### 🔐 Security
- **4-Level Access Control**: Visitor → Student → Instructor → Admin
- **Secure Authentication**: SHA-256 token-based verification
- **Audit Logging**: Complete access history tracking

### 🔧 Equipment Management
- **7 Equipment Categories**: Art supplies, 3D printing, laser cutting, textiles, photography, music, digital art
- **5 Status Types**: Available, In Use, Maintenance, Damaged, Missing
- **Certification System**: Restrict dangerous equipment to trained users
- **Damage Reporting**: Track issues with severity levels

### 📅 Session Tracking
- **Purpose Documentation**: Know what users are working on
- **Duration Monitoring**: Automatic time tracking
- **Collaborative Sessions**: Support group projects
- **Session Notes**: Document progress and observations

### ⚠️ Safety Features
- **Incident Logging**: 4 severity levels (Low, Medium, High, Critical)
- **Resolution Tracking**: Monitor incident status
- **Automatic Alerts**: Equipment damage triggers incidents
- **Historical Analysis**: Learn from past issues

## Quick Start

### Initialize System
```bash
python scripts/manage_creative_corner.py
# Choose option 6: Initialize Sample Data
```

### Register a User
```python
from src.modules.creative_corner import CreativeCornerSecurity, AccessLevel

cc = CreativeCornerSecurity()
user = cc.register_user(
    "student001",
    "Alice Johnson",
    "student",
    AccessLevel.STUDENT,
    "alice@school.edu"
)
print(f"Access Token: {user.access_token}")
```

### Start a Session
```python
# Verify user
success, msg = cc.verify_user("student001", user.access_token)

# Start session
session_id, msg = cc.start_session("student001", "Sculpture project")

# Check out equipment
cc.check_out_equipment("eq_paint01", "student001", session_id)

# Work on project...

# Check in equipment
cc.check_in_equipment("eq_paint01", "good")

# End session
cc.end_session(session_id)
```

### Certify User for Equipment
```python
# Only certified users can use dangerous equipment
cc.certify_user("student001", "3d_printing", "instructor001")
cc.certify_user("student001", "laser_cutting", "instructor001")
```

### Report Issues
```python
# Report equipment damage
cc.report_equipment_damage(
    "eq_laser",
    "student001",
    "Laser not cutting properly",
    "medium"
)

# Log safety incident
from src.modules.creative_corner import IncidentSeverity
cc.log_incident(
    "Minor burn from hot glue gun",
    IncidentSeverity.LOW,
    "student002"
)
```

## Equipment Categories

| Category | Certification Required | Examples |
|----------|----------------------|----------|
| Art Supplies | ❌ No | Paint sets, brushes, canvases |
| 3D Printing | ✅ Yes | 3D printers, filament |
| Laser Cutting | ✅ Yes | Laser cutters |
| Textiles | ✅ Yes | Sewing machines |
| Photography | ❌ No | Cameras, lighting |
| Music | ❌ No | Instruments, recording gear |
| Digital Art | ❌ No | Drawing tablets, styluses |

## Access Levels

| Level | Permissions |
|-------|------------|
| **Visitor** | Basic equipment, supervised only |
| **Student** | General equipment, can earn certifications |
| **Instructor** | All equipment, can certify students |
| **Admin** | Full system access, user management |

## CLI Commands

```bash
python scripts/manage_creative_corner.py
```

**Main Menu Options:**
1. User Management - Register, verify, certify users
2. Equipment Management - Add, check-out, maintain equipment
3. Session Management - Start, end, track sessions
4. Incident Management - Log, resolve incidents
5. Reports & Analytics - View security reports
6. Initialize Sample Data - Set up demo data

## Data Files

All data stored in `data/creative_corner/`:
- `users.json` - User profiles and tokens
- `equipment.json` - Equipment inventory
- `sessions.json` - Session history
- `incidents.json` - Incident reports
- `access_log.json` - Access audit trail

## Testing

```bash
# Run all Creative Corner tests
pytest tests/test_creative_corner.py -v

# Run specific test category
pytest tests/test_creative_corner.py::TestUserManagement -v

# Run with coverage
pytest tests/test_creative_corner.py --cov=src.modules.creative_corner --cov-report=html
```

## Common Workflows

### New Student Onboarding
1. Register student with STUDENT access level
2. Provide access token (save securely)
3. Schedule certification training for required equipment
4. Certify after training completion
5. Student can now use certified equipment

### Equipment Checkout
1. User starts session with purpose
2. User checks out needed equipment
3. System verifies certification if required
4. Equipment status changes to IN_USE
5. User works on project
6. User checks in equipment
7. User ends session

### Incident Response
1. Incident reported (damage, safety issue, etc.)
2. System logs incident with severity
3. Admin/instructor reviews incident
4. Issue resolved (repair, training, etc.)
5. Incident marked as resolved
6. Lessons learned documented

### Equipment Maintenance
1. Equipment status set to MAINTENANCE
2. Maintenance performed
3. Maintenance logged with notes
4. Equipment status returned to AVAILABLE
5. Maintenance history updated

## Security Best Practices

### For Administrators
- ✅ Review access logs weekly
- ✅ Audit equipment status daily
- ✅ Resolve incidents promptly
- ✅ Keep certifications current
- ✅ Backup data regularly

### For Instructors
- ✅ Verify certifications before equipment use
- ✅ Report all equipment issues immediately
- ✅ Monitor active sessions
- ✅ Document safety concerns

### For Students
- ✅ Always check in equipment when done
- ✅ Report damage immediately
- ✅ Respect certification requirements
- ✅ Add session notes for continuity

## Troubleshooting

**"User not certified"**
→ Contact instructor for certification training

**"Equipment not available"**
→ Check equipment status, may be in use or maintenance

**"Access denied - active restrictions"**
→ Contact administrator to review restrictions

**"Session not found"**
→ Verify session ID, may have already ended

## Support

- 📖 Full Documentation: `docs/CREATIVE_CORNER.md`
- 🧪 Test Examples: `tests/test_creative_corner.py`
- 💻 CLI Tool: `scripts/manage_creative_corner.py`
- 📝 API Reference: See full documentation

---

**Version**: 3.1.0  
**Last Updated**: October 2025
