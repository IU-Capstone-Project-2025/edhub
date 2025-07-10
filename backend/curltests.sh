#!/bin/bash
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
curl -s --fail-with-body -X POST $API_URL/create_user -H "Content-Type: application/json" \
    -d "{\"email\":\"$USER_EMAIL\",\"password\":\"$USER_PASS\",\"name\":\"$USER_NAME\"}"
if [ $? -gt 0 ]; then exit 1; fi
echo
curl -s --fail-with-body -X POST $API_URL/create_user -H "Content-Type: application/json" \
    -d "{\"email\":\"$STUDENT_EMAIL\",\"password\":\"$STUDENT_PASS\",\"name\":\"$STUDENT_NAME\"}"
if [ $? -gt 0 ]; then exit 1; fi
echo
curl -s --fail-with-body -X POST $API_URL/create_user -H "Content-Type: application/json" \
    -d "{\"email\":\"$PARENT_EMAIL\",\"password\":\"$PARENT_PASS\",\"name\":\"$PARENT_NAME\"}"
if [ $? -gt 0 ]; then exit 1; fi
echo
curl -s --fail-with-body -X POST $API_URL/create_user -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEACHER2_EMAIL\",\"password\":\"$TEACHER2_PASS\",\"name\":\"$TEACHER2_NAME\"}"
if [ $? -gt 0 ]; then exit 1; fi
echo

echo "== Logging in as Alice =="
TEMP="$(curl -s --fail-with-body -X POST $API_URL/login -H "Content-Type: application/json" \
    -d "{\"email\":\"$USER_EMAIL\",\"password\":\"$USER_PASS\"}")"
RES=$?
echo "$TEMP"
if [ $RES -gt 0 ]; then exit 1; fi
TOKEN=$(echo "$TEMP" | extract_token)
echo "Token: $TOKEN"

echo "== Creating a course =="
TEMP=$(curl -s --fail-with-body -X POST "$API_URL/create_course?title=Physics" \
    -H "Authorization: Bearer $TOKEN")
RES=$?
echo "$TEMP"
if [ $RES -gt 0 ]; then exit 1; fi
COURSE_ID=$(echo "$TEMP" | extract_course_id)
echo "Course ID: $COURSE_ID"

echo "== Getting available courses =="
curl -s --fail-with-body -X GET "$API_URL/available_courses" -H "Authorization: Bearer $TOKEN"
if [ $? -gt 0 ]; then exit 1; fi
echo

echo "== Getting course info =="
curl -s --fail-with-body -X GET "$API_URL/get_course_info?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN" 
if [ $? -gt 0 ]; then exit 1; fi
echo

echo "== Inviting student to course =="
curl -s --fail-with-body -X POST "$API_URL/invite_student?course_id=$COURSE_ID&student_email=$STUDENT_EMAIL" \
    -H "Authorization: Bearer $TOKEN" 
if [ $? -gt 0 ]; then exit 1; fi
echo
echo "== Getting enrolled students =="
curl -s --fail-with-body -X GET "$API_URL/get_enrolled_students?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN" 
if [ $? -gt 0 ]; then exit 1; fi
echo

echo "== Inviting parent to student =="
curl -s --fail-with-body -X POST "$API_URL/invite_parent?course_id=$COURSE_ID&student_email=$STUDENT_EMAIL&parent_email=$PARENT_EMAIL" \
    -H "Authorization: Bearer $TOKEN" 
if [ $? -gt 0 ]; then exit 1; fi
echo

echo "== Getting student's parents =="
curl -s --fail-with-body -X GET "$API_URL/get_students_parents?course_id=$COURSE_ID&student_email=$STUDENT_EMAIL" \
    -H "Authorization: Bearer $TOKEN" 
if [ $? -gt 0 ]; then exit 1; fi
echo

echo "== Inviting second teacher =="
curl -s --fail-with-body -X POST "$API_URL/invite_teacher?course_id=$COURSE_ID&new_teacher_email=$TEACHER2_EMAIL" \
    -H "Authorization: Bearer $TOKEN" 
if [ $? -gt 0 ]; then exit 1; fi
echo

echo "== Getting course teachers =="
curl -s --fail-with-body -X GET "$API_URL/get_course_teachers?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN" 
if [ $? -gt 0 ]; then exit 1; fi
echo

echo "== Creating material =="
TEMP=$(curl -s --fail-with-body -X POST "$API_URL/create_material?course_id=$COURSE_ID&title=Intro&description=Welcome" \
    -H "Authorization: Bearer $TOKEN" | extract_material_id)
RES=$?
echo "$TEMP"
if [ $RES -gt 0 ]; then exit 1; fi
MATERIAL_ID=$(echo "$TEMP" | extract_material_id)
echo "Material ID: $MATERIAL_ID"

echo "== Getting course feed =="
curl -s --fail-with-body -X GET "$API_URL/get_course_feed?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN" 
if [ $? -gt 0 ]; then exit 1; fi
echo

echo "== Getting material =="
curl -s --fail-with-body -X GET "$API_URL/get_material?course_id=$COURSE_ID&material_id=$MATERIAL_ID" -H "Authorization: Bearer $TOKEN" 
if [ $? -gt 0 ]; then exit 1; fi
echo

echo "== Creating assignment =="
TEMP=$(curl -s --fail-with-body -X POST "$API_URL/create_assignment?course_id=$COURSE_ID&title=Homework1&description=Chapter1" \
    -H "Authorization: Bearer $TOKEN")
RES=$?
echo "$TEMP"
if [ $RES -gt 0 ]; then exit 1; fi
ASSIGNMENT_ID=$(echo "$TEMP" | extract_assignment_id)
echo "Assignment ID: $ASSIGNMENT_ID"

echo "== Getting assignment info =="
curl -s --fail-with-body -X GET "$API_URL/get_assignment?course_id=$COURSE_ID&assignment_id=$ASSIGNMENT_ID" \
    -H "Authorization: Bearer $TOKEN" 
if [ $? -gt 0 ]; then exit 1; fi
echo

echo "== Submitting assignment =="
TEMP=$(curl -s --fail-with-body -X POST $API_URL/login -H "Content-Type: application/json" \
    -d "{\"email\":\"$STUDENT_EMAIL\",\"password\":\"$STUDENT_PASS\"}")
RES=$?
echo "$TEMP"
if [ $RES -gt 0 ]; then exit 1; fi
STUDENT_TOKEN=$(echo "$TEMP" | extract_token)
echo "Student token: $STUDENT_TOKEN"
curl -s --fail-with-body -X POST "$API_URL/submit_assignment?course_id=$COURSE_ID&assignment_id=$ASSIGNMENT_ID&comment=MySolution" \
    -H "Authorization: Bearer $STUDENT_TOKEN" 
if [ $? -gt 0 ]; then exit 1; fi
echo

echo "== Grading assignment =="
curl -s --fail-with-body -X POST "$API_URL/grade_submission?course_id=$COURSE_ID&assignment_id=$ASSIGNMENT_ID&student_email=$STUDENT_EMAIL&grade=95" \
    -H "Authorization: Bearer $TOKEN" 
if [ $? -gt 0 ]; then exit 1; fi
echo

echo "== Grade report =="
curl -s --fail-with-body -X GET "$API_URL/download_full_course_grade_table?course_id=$COURSE_ID" \
    -H "Authorization: Bearer $TOKEN" 
if [ $? -gt 0 ]; then exit 1; fi
echo

echo "== Admin login =="
ADMIN_PASSWORD=$(cat ./random-secrets/admin_credentials.txt | tail -n 1 | sed 's/password: //')
TEMP=$(curl -s --fail-with-body -X POST $API_URL/login -H "Content-Type: application/json" \
    -d "{\"email\":\"admin\",\"password\":\"$ADMIN_PASSWORD\"}")
RES=$?
echo "$TEMP"
if [ $RES -gt 0 ]; then exit 1; fi
TOKEN=$(echo "$TEMP" | extract_token)
echo

echo "== Admin creating material =="
TEMP=$(curl -s --fail-with-body -X POST "$API_URL/create_material?course_id=$COURSE_ID&title=AdminTitle&description=AdminDescription" \
    -H "Authorization: Bearer $TOKEN")
RES=$?
echo "$TEMP"
if [ $RES -gt 0 ]; then exit 1; fi
MATERIAL_ID=$(echo "$TEMP" | extract_material_id)
echo "Material ID: $MATERIAL_ID"
echo

echo "== Admin remove course =="
curl -s --fail-with-body -X POST "$API_URL/remove_course?course_id=$COURSE_ID" -H "Authorization: Bearer $TOKEN"
if [ $? -gt 0 ]; then exit 1; fi

echo "== All tests completed =="
