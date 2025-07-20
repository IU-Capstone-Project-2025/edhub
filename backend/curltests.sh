#!/bin/bash
set -e

API_URL="http://localhost/api"

USER_EMAIL="alice@example.com"
USER_PASS="alicePass123!"
USER_NAME="Alice"
STUDENT_EMAIL="student@example.com"
STUDENT_PASS="studentPass123!"
STUDENT_NAME="Student"
PARENT_EMAIL="parent@example.com"
PARENT_PASS="parentPass123!"
PARENT_NAME="Parent"
TEACHER2_EMAIL="teacher2@example.com"
TEACHER2_PASS="teacher2Pass123!"
TEACHER2_NAME="Teacher2"

extract_token() {
    python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])"
}
extract_course_id() {
    python3 -c "import sys, json; print(json.load(sys.stdin)['course_id'])"
}
extract_material_id() {
    python3 -c "import sys, json; print(json.load(sys.stdin)['material_id'])"
}
extract_assignment_id() {
    python3 -c "import sys, json; print(json.load(sys.stdin)['assignment_id'])"
}

echo "== Registering users =="
curl -s --fail -X POST $API_URL/create_user -H "Content-Type: application/json" \
    -d "{\"email\":\"$USER_EMAIL\",\"password\":\"$USER_PASS\",\"name\":\"$USER_NAME\"}" > /dev/null
curl -s --fail -X POST $API_URL/create_user -H "Content-Type: application/json" \
    -d "{\"email\":\"$STUDENT_EMAIL\",\"password\":\"$STUDENT_PASS\",\"name\":\"$STUDENT_NAME\"}" > /dev/null
curl -s --fail -X POST $API_URL/create_user -H "Content-Type: application/json" \
    -d "{\"email\":\"$PARENT_EMAIL\",\"password\":\"$PARENT_PASS\",\"name\":\"$PARENT_NAME\"}" > /dev/null
curl -s --fail -X POST $API_URL/create_user -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEACHER2_EMAIL\",\"password\":\"$TEACHER2_PASS\",\"name\":\"$TEACHER2_NAME\"}" > /dev/null

echo "== Logging in as Alice =="
TOKEN=$(curl -s --fail -X POST $API_URL/login -H "Content-Type: application/json" \
    -d "{\"email\":\"$USER_EMAIL\",\"password\":\"$USER_PASS\"}" | extract_token)
echo "Token: $TOKEN"

echo "== Creating a course =="
COURSE_ID=$(curl -s --fail -X POST "$API_URL/create_course?title=Physics" \
    -H "Authorization: Bearer $TOKEN" | extract_course_id)
echo "Course ID: $COURSE_ID"

echo "== Getting available courses =="
curl -s --fail -X GET "$API_URL/available_courses" -H "Authorization: Bearer $TOKEN"
echo

echo "== Getting course info =="
curl -s --fail -X GET "$API_URL/get_course_info?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN"
echo

echo "== Inviting student to course =="
curl -s --fail -X POST "$API_URL/invite_student?course_id=$COURSE_ID&student_email=$STUDENT_EMAIL" \
    -H "Authorization: Bearer $TOKEN"

echo
echo "== Getting enrolled students =="
curl -s --fail -X GET "$API_URL/get_enrolled_students?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN"
echo

echo "== Inviting parent to student =="
curl -s --fail -X POST "$API_URL/invite_parent?course_id=$COURSE_ID&student_email=$STUDENT_EMAIL&parent_email=$PARENT_EMAIL" \
    -H "Authorization: Bearer $TOKEN"
echo

echo "== Getting student's parents =="
curl -s --fail -X GET "$API_URL/get_students_parents?course_id=$COURSE_ID&student_email=$STUDENT_EMAIL" \
    -H "Authorization: Bearer $TOKEN"
echo

echo "== Inviting second teacher =="
curl -s --fail -X POST "$API_URL/invite_teacher?course_id=$COURSE_ID&new_teacher_email=$TEACHER2_EMAIL" \
    -H "Authorization: Bearer $TOKEN"
echo

echo "== Getting course teachers =="
curl -s --fail -X GET "$API_URL/get_course_teachers?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN"
echo

echo "== Creating material =="
MATERIAL_ID=$(curl -s --fail -X POST "$API_URL/create_material?course_id=$COURSE_ID&title=Intro&description=Welcome" \
    -H "Authorization: Bearer $TOKEN" | extract_material_id)
echo "Material ID: $MATERIAL_ID"
echo

echo "== Getting course feed =="
curl -s --fail -X GET "$API_URL/get_course_feed?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN"
echo

echo "== Getting material =="
curl -s --fail -X GET "$API_URL/get_material?course_id=$COURSE_ID&material_id=$MATERIAL_ID" -H "Authorization: Bearer $TOKEN"
echo

echo "== Creating assignment =="
ASSIGNMENT_ID=$(curl -s --fail -X POST "$API_URL/create_assignment?course_id=$COURSE_ID&title=Homework1&description=Chapter1" \
    -H "Authorization: Bearer $TOKEN" | extract_assignment_id)
echo "Assignment ID: $ASSIGNMENT_ID"

echo "== Getting assignment info =="
curl -s --fail -X GET "$API_URL/get_assignment?course_id=$COURSE_ID&assignment_id=$ASSIGNMENT_ID" \
    -H "Authorization: Bearer $TOKEN"
echo

echo "== Submitting assignment =="
STUDENT_TOKEN=$(curl -s --fail -X POST $API_URL/login -H "Content-Type: application/json" \
    -d "{\"email\":\"$STUDENT_EMAIL\",\"password\":\"$STUDENT_PASS\"}" | extract_token)
curl -s --fail -X POST "$API_URL/submit_assignment?course_id=$COURSE_ID&assignment_id=$ASSIGNMENT_ID&comment=MySolution" \
    -H "Authorization: Bearer $STUDENT_TOKEN"
echo

echo "== Grading assignment =="
curl -s --fail -X POST "$API_URL/grade_submission?course_id=$COURSE_ID&assignment_id=$ASSIGNMENT_ID&student_email=$STUDENT_EMAIL&grade=95" \
    -H "Authorization: Bearer $TOKEN"
echo

echo "== Grade report =="
curl -s --fail -X GET "$API_URL/download_full_course_grade_table?course_id=$COURSE_ID" \
    -H "Authorization: Bearer $TOKEN"
echo

echo "== Grade report (json) =="
curl -s --fail -X GET "$API_URL/get_full_course_grade_table_json?course_id=$COURSE_ID" \
    -H "Authorization: Bearer $TOKEN"
echo

echo "== Admin login =="
TOKEN=$(curl -s --fail -X POST $API_URL/login -H "Content-Type: application/json" \
    -d "{\"email\":\"admin\",\"password\":\"admin\"}" | extract_token)
echo

echo "== Admin creating material =="
MATERIAL_ID=$(curl -s --fail -X POST "$API_URL/create_material?course_id=$COURSE_ID&title=AdminTitle&description=AdminDescription" \
    -H "Authorization: Bearer $TOKEN" | extract_material_id)
echo "Material ID: $MATERIAL_ID"
echo

echo "== Admin remove course =="
curl -s -X POST "$API_URL/remove_course?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN"

echo "== All tests completed =="
