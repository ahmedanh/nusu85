"""
Fix DB data issues:
1. Delete empty-named department in Engineering college
2. Add Computer Science to Engineering if not already there
3. Don't create duplicate CS departments
"""
import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'acdc_config.settings'
django.setup()

from attendance.models import College, Department

# --- Find Engineering college ---
eng = None
for col in College.objects.all():
    if 'هندس' in col.college_name or 'Engineering' in col.college_name or 'Engin' in col.college_name:
        eng = col
        print(f"Found Engineering college: id={col.college_id} name='{col.college_name}'")
        break

if not eng:
    print("Engineering college not found! Available colleges:")
    for col in College.objects.all():
        print(f"  id={col.college_id} name='{col.college_name}'")
else:
    # Show all departments in Engineering
    depts = Department.objects.filter(college=eng)
    print(f"\nDepartments in Engineering ({depts.count()}):")
    for d in depts:
        print(f"  id={d.id} name='{d.name}'")

    # Delete empty-named departments in Engineering
    empty = depts.filter(name='')
    if empty.exists():
        count = empty.count()
        empty.delete()
        print(f"\nDeleted {count} empty-named department(s) from Engineering.")
    else:
        print("\nNo empty departments found in Engineering.")

    # Find if CS already exists globally and in Engineering
    cs_global = Department.objects.filter(name__icontains='Computer Science').first() or \
                Department.objects.filter(name__icontains='علوم الحاسب').first() or \
                Department.objects.filter(name__icontains='Comput').first()

    cs_in_eng = Department.objects.filter(college=eng).filter(
        name__icontains='Computer'
    ).first() or Department.objects.filter(college=eng).filter(
        name__icontains='علوم الحاسب'
    ).first()

    if cs_in_eng:
        print(f"\nCS already in Engineering: id={cs_in_eng.id} name='{cs_in_eng.name}'")
    elif cs_global:
        # CS exists but not linked to Engineering — check if it's linked to another college
        print(f"\nCS exists globally: id={cs_global.id} college_id={cs_global.college_id} name='{cs_global.name}'")
        if cs_global.college_id is None:
            # Not linked — link to Engineering
            cs_global.college = eng
            cs_global.save(update_fields=['college'])
            print(f"Linked existing CS dept to Engineering college.")
        else:
            # Already linked to another college — create new one for Engineering
            new_cs = Department.objects.create(name='Computer Science', college=eng)
            print(f"Created new CS dept in Engineering: id={new_cs.id}")
    else:
        # Create CS in Engineering
        new_cs = Department.objects.create(name='Computer Science', college=eng)
        print(f"\nCreated Computer Science in Engineering: id={new_cs.id}")

print("\nDone.")
