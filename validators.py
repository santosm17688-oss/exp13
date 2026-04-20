import re

def validate_student(data, is_update=False):
    errors = []

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    age = data.get("age")
    course = data.get("course", "").strip()

    if not is_update or "name" in data:
        if not name or len(name) < 2:
            errors.append("Name must be at least 2 characters.")

    if not is_update or "email" in data:
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("A valid email is required.")

    if not is_update or "age" in data:
        if age is None or not str(age).isdigit() or not (1 <= int(age) <= 120):
            errors.append("Age must be a number between 1 and 120.")

    if not is_update or "course" in data:
        if not course or len(course) < 2:
            errors.append("Course must be at least 2 characters.")

    return errors