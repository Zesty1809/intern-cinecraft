# Fake User Generator - Documentation

## 🎭 Generate Sample Department Profiles

A Django management command to create realistic fake user profiles for testing the admin dashboard and submission workflows.

---

## 🚀 Quick Start

### Basic Usage (Generate 20 profiles):
```bash
cd /home/zesty/CodeFiles/Django/cinecraft
python manage.py create_sample_profiles
```

### Generate Custom Number:
```bash
# Generate 50 profiles
python manage.py create_sample_profiles --count 50

# Generate 100 profiles
python manage.py create_sample_profiles --count 100
```

### Clear Existing Data First:
```bash
# Clear all profiles and generate 30 new ones
python manage.py create_sample_profiles --count 30 --clear
```

---

## 📋 Command Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--count` | Integer | 20 | Number of fake profiles to generate |
| `--clear` | Flag | False | Delete all existing profiles before generating |

### Examples:
```bash
# Default: 20 profiles
python manage.py create_sample_profiles

# Generate 5 profiles for quick testing
python manage.py create_sample_profiles --count 5

# Generate 100 profiles for load testing
python manage.py create_sample_profiles --count 100

# Start fresh with 25 new profiles
python manage.py create_sample_profiles --count 25 --clear
```

---

## 🎨 Generated Data

### Personal Information
- **Full Name**: Realistic Indian names (e.g., "Rajesh Kumar", "Priya Sharma")
- **Email**: Auto-generated from name (e.g., "rajesh.kumar@example.com")
- **Phone**: Random Indian mobile numbers (+91 format)
- **Date of Birth**: Age between 25-55 years
- **Address**: Realistic street addresses
- **City**: Major Indian cities (Mumbai, Delhi, Bangalore, etc.)
- **State**: Matching Indian states
- **Pin Code**: Random 6-digit codes

### Professional Information
- **Department**: 15 different cinema departments
  - Direction Department
  - Cinematography
  - Music Department
  - Sound Department
  - Editing Department
  - Art Department
  - Costume Design
  - Make Up Department
  - Visual Effects
  - Production Department
  - Lighting Department
  - Camera Department
  - Choreography
  - Casting Department
  - Script Department

- **Years of Experience**: 1-20 years
- **Key Skills**: Department-specific skill sets
- **Previous Projects**: Realistic project descriptions
- **Availability**: Various availability statuses
- **Expected Salary**: Realistic salary ranges (₹30K - ₹300K)
- **Work Locations**: Multiple cities

### Education & Recognition
- **Educational Qualification**: Film school degrees, diplomas, self-taught
- **Certifications**: Industry-relevant certifications
- **Awards**: Film festival awards and recognition

### Portfolio & Links
- **Portfolio Link**: Personal portfolio websites (30% have links)
- **LinkedIn Profile**: Professional profiles (80% have links)
- **IMDb Profile**: IMDb pages (50% have profiles)

### Approval Status
Profiles are distributed across different statuses:
- **40% Pending** - New submissions waiting for review
- **30% Approved** - Accepted profiles
- **15% Rejected** - Declined applications
- **15% Inactive** - Deactivated profiles

---

## 📊 Sample Output

```bash
$ python manage.py create_sample_profiles --count 10

Created: Rajesh Kumar - Direction Department - PENDING (ID: 24CC00001)
Created: Priya Sharma - Cinematography - APPROVED (ID: 24CC00002)
Created: Amit Singh - Music Department - PENDING (ID: 24CC00003)
Created: Sneha Patel - Editing Department - APPROVED (ID: 24CC00004)
Created: Vikram Reddy - Art Department - REJECTED (ID: 24CC00005)
Created: Anjali Gupta - Make Up Department - PENDING (ID: 24CC00006)
Created: Arjun Nair - Sound Department - APPROVED (ID: 24CC00007)
Created: Deepika Rao - Visual Effects - PENDING (ID: 24CC00008)
Created: Karan Chopra - Production Department - INACTIVE (ID: 24CC00009)
Created: Pooja Verma - Costume Design - PENDING (ID: 24CC00010)

✅ Successfully created 10 sample profiles!
   - Pending: 5
   - Approved: 3
   - Rejected: 1
   - Inactive: 1
```

---

## 🧪 Testing Scenarios

### 1. **Test Submission Tab**
```bash
# Generate profiles with mostly pending status
python manage.py create_sample_profiles --count 20
# View them in Admin Dashboard → Submission tab
```

### 2. **Test Users Tab**
```bash
# Generate mix of approved/active users
python manage.py create_sample_profiles --count 15
# View approved users in Admin Dashboard → Users tab
```

### 3. **Test Approve/Reject Actions**
```bash
# Generate pending profiles to test actions
python manage.py create_sample_profiles --count 10
# Test approve/reject buttons in dashboard
```

### 4. **Test Edit Functionality**
```bash
# Generate profiles to edit
python manage.py create_sample_profiles --count 5
# Click Edit button and modify fields
```

### 5. **Test Email Notifications**
```bash
# Generate profiles and test approval emails
python manage.py create_sample_profiles --count 3
# Approve/reject and check console for emails
```

### 6. **Load Testing**
```bash
# Generate large dataset to test performance
python manage.py create_sample_profiles --count 100
# Check dashboard loading speed
```

### 7. **Clean Slate Testing**
```bash
# Start fresh each time
python manage.py create_sample_profiles --count 10 --clear
# Ensures consistent test environment
```

---

## 🎯 Use Cases

### Development Testing
- Test UI with realistic data
- Verify form validation
- Check data display consistency
- Test search and filter functions

### Feature Testing
- Test approve/reject workflow
- Test edit functionality
- Test delete operations
- Test email notifications

### Performance Testing
- Generate 100+ profiles for load testing
- Test pagination
- Test database queries
- Check dashboard performance

### Demo & Presentation
- Quick generation of sample data
- Realistic looking profiles
- Professional presentation
- Client demos

---

## 📁 File Location

```
cinecraft/
└── cineapp/
    └── management/
        └── commands/
            └── create_sample_profiles.py
```

---

## 🔧 Technical Details

### Data Pools
- **32 First Names**: Common Indian names
- **24 Last Names**: Popular Indian surnames
- **15 Departments**: Cinema industry roles
- **12 Cities**: Major Indian metropolitan areas
- **10 Skill Sets**: Department-specific skills
- **10 Project Types**: Realistic project descriptions

### Randomization
- Uses Python's `random` module for varied data
- Weighted distribution for approval statuses
- Optional fields have probability-based generation
- Ensures realistic data combinations

### Database Operations
- Uses `DepartmentProfile.objects.create()`
- Auto-generates Application IDs (24CC00001, etc.)
- Handles duplicate prevention
- Provides error messages for failed creations

---

## ⚠️ Important Notes

### Email Addresses
- All emails use `@example.com` domain
- Not real email addresses
- Safe for testing without sending actual emails

### Phone Numbers
- Random 10-digit numbers with +91 prefix
- Not real phone numbers
- For display and testing only

### Links
- Portfolio and social media links are fictional
- URLs won't actually work
- For demonstration purposes only

### Data Cleanup
- Use `--clear` flag to remove all profiles
- Or manually delete from Django admin
- Or use: `DepartmentProfile.objects.all().delete()` in shell

---

## 🛠️ Customization

### Add More Names
Edit the `first_names` and `last_names` lists in the command:
```python
first_names = [
    'YourName1', 'YourName2', # Add more
]
```

### Add More Departments
Edit the `departments` list:
```python
departments = [
    'Your Department', # Add more
]
```

### Change Status Distribution
Modify the `status_weights`:
```python
# More approved profiles
status_weights = [0.2, 0.6, 0.1, 0.1]  # [pending, approved, rejected, inactive]
```

---

## 🧹 Cleanup Commands

### Delete All Profiles
```bash
# Using management command
python manage.py create_sample_profiles --count 0 --clear

# Or using Django shell
python manage.py shell
>>> from cineapp.models import DepartmentProfile
>>> DepartmentProfile.objects.all().delete()
```

### Delete by Status
```bash
python manage.py shell
>>> from cineapp.models import DepartmentProfile
>>> DepartmentProfile.objects.filter(approval_status='pending').delete()
```

---

## 🎉 Quick Reference

```bash
# Most Common Commands

# Generate default 20 profiles
python manage.py create_sample_profiles

# Start fresh with 25 profiles
python manage.py create_sample_profiles --count 25 --clear

# Quick test with 5 profiles
python manage.py create_sample_profiles --count 5

# Load testing with 100 profiles
python manage.py create_sample_profiles --count 100

# View generated data in admin
python manage.py runserver
# Go to: http://localhost:8000/admin/
```

---

## 📊 Statistics Example

After generating 50 profiles:
- **~20 Pending** (40%) - For testing submission approval
- **~15 Approved** (30%) - Visible in Users tab
- **~8 Rejected** (15%) - For testing rejection flow
- **~7 Inactive** (15%) - For testing status management

Perfect distribution for comprehensive testing!

---

**Created**: January 2025  
**Status**: ✅ Ready to Use  
**Command**: `create_sample_profiles`  
**Default Count**: 20 profiles
