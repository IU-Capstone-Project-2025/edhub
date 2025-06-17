#!/bin/bash

API_URL="http://localhost:8000"

# Test user credentials
USER_EMAIL="alice@example.com"
USER_PASS="alicepass"
USER_NAME="Alice"
STUDENT_EMAIL="student@example.com"
STUDENT_PASS="studentpass"
STUDENT_NAME="Student"
PARENT_EMAIL="parent@example.com"
PARENT_PASS="parentpass"
PARENT_NAME="Parent"
TEACHER2_EMAIL="teacher2@example.com"
TEACHER2_PASS="teacher2pass"
TEACHER2_NAME="Teacher2"

# Helper to extract values from JSON
extract_token() {
    python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])"
}
extract_course_id() {
    python3 -c "import sys, json; print(json.load(sys.stdin)['course_id'])"
}
extract_material_id() {
    python3 -c "import sys, json; print(json.load(sys.stdin)['material_id'])"
}

echo "== Registering users =="
curl -s -X POST $API_URL/create_user -H "Content-Type: application/json" \
    -d "{\"email\":\"$USER_EMAIL\",\"password\":\"$USER_PASS\",\"name\":\"$USER_NAME\"}" > /dev/null
curl -s -X POST $API_URL/create_user -H "Content-Type: application/json" \
    -d "{\"email\":\"$STUDENT_EMAIL\",\"password\":\"$STUDENT_PASS\",\"name\":\"$STUDENT_NAME\"}" > /dev/null
curl -s -X POST $API_URL/create_user -H "Content-Type: application/json" \
    -d "{\"email\":\"$PARENT_EMAIL\",\"password\":\"$PARENT_PASS\",\"name\":\"$PARENT_NAME\"}" > /dev/null
curl -s -X POST $API_URL/create_user -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEACHER2_EMAIL\",\"password\":\"$TEACHER2_PASS\",\"name\":\"$TEACHER2_NAME\"}" > /dev/null

echo "== Logging in as Alice =="
TOKEN=$(curl -s -X POST $API_URL/login -H "Content-Type: application/json" \
    -d "{\"email\":\"$USER_EMAIL\",\"password\":\"$USER_PASS\"}" | extract_token)
echo "Token: $TOKEN"

echo "== Creating a course =="
COURSE_ID=$(curl -s -X POST "$API_URL/create_course?title=Physics" \
    -H "Authorization: Bearer $TOKEN" | extract_course_id)
echo "Course ID: $COURSE_ID"

echo "== Getting available courses =="
curl -s -X GET "$API_URL/available_courses" -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== Getting course info =="
curl -s -X GET "$API_URL/get_course_info?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== Inviting student to course =="
curl -s -X POST "$API_URL/invite_student?course_id=$COURSE_ID&student_email=$STUDENT_EMAIL" \
    -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== Getting enrolled students =="
curl -s -X GET "$API_URL/get_enrolled_students?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== Inviting parent to student =="
curl -s -X POST "$API_URL/invite_parent?course_id=$COURSE_ID&student_email=$STUDENT_EMAIL&parent_email=$PARENT_EMAIL" \
    -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== Getting student's parents =="
curl -s -X GET "$API_URL/get_students_parents?course_id=$COURSE_ID&student_email=$STUDENT_EMAIL" \
    -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== Inviting second teacher =="
curl -s -X POST "$API_URL/invite_teacher?course_id=$COURSE_ID&new_teacher_email=$TEACHER2_EMAIL" \
    -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== Getting course teachers =="
curl -s -X GET "$API_URL/get_course_teachers?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== Creating material =="
MATERIAL_ID=$(curl -s -X POST "$API_URL/create_material?course_id=$COURSE_ID&title=Intro&description=Welcome" \
    -H "Authorization: Bearer $TOKEN" | extract_material_id)
echo "Material ID: $MATERIAL_ID"

echo "== Getting course feed =="
curl -s -X GET "$API_URL/get_course_feed?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== Getting material =="
curl -s -X GET "$API_URL/get_material?course_id=$COURSE_ID&material_id=$MATERIAL_ID" -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== Removing material =="
curl -s -X POST "$API_URL/remove_material?course_id=$COURSE_ID&material_id=$MATERIAL_ID" -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== Removing parent from student =="
curl -s -X POST "$API_URL/remove_parent?course_id=$COURSE_ID&student_email=$STUDENT_EMAIL&parent_email=$PARENT_EMAIL" \
    -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== Removing student from course =="
curl -s -X POST "$API_URL/remove_student?course_id=$COURSE_ID&student_email=$STUDENT_EMAIL" \
    -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== Removing second teacher =="
curl -s -X POST "$API_URL/remove_teacher?course_id=$COURSE_ID&removing_teacher_email=$TEACHER2_EMAIL" \
    -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== Removing course =="
curl -s -X POST "$API_URL/remove_course?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN" | tee /dev/stderr

echo "== All tests completed =="