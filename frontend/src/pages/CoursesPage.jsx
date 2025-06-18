import Header from "@/components/Header"
import CourseCard from "../components/CourseCard"
import { useEffect, useState } from "react"
import axios from "axios"
import { Button } from "@/components/ui/button"

export default function CoursesPage() {
  const [courses, setCourses] = useState([])

  useEffect(() => {
  const fetchCourses = async () => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      console.error("No access token found")
      return
    }

    try {
      const res = await axios.get("/available_courses", {
        headers: { Authorization: `Bearer ${token}` },
      })

      const full = await Promise.all(
        res.data.map(async (c) => {
          const r = await axios.get("/get_course_info", {
            headers: { Authorization: `Bearer ${token}` },
            params: { course_id: c.course_id },
          })
          return r.data
        })
      )

      setCourses(full)
    } catch (err) {
      console.error("Ошибка получения курсов:", err)
      if (err.response?.status === 401) {
        alert("Сессия истекла. Пожалуйста, войдите снова.")
        window.location.href = "/"
      }
    }
  }

  fetchCourses()
}, [])


  return (
    <Header>
  <div className="w-full px-[5%] py-[2%]">
    <div className="flex justify-between items-center mb-[2%] flex-wrap gap-4 w-full">
      <h1 className="text-2xl font-bold text-[#333940]">Your Courses</h1>
      <a href="/create-course">
        <Button className="bg-[#4CB050] hover:bg-[#3BBF12] text-white text-md rounded-xl px-[5%] py-[2%] border-2 border-transparent hover:border-[#2E7D32] transition">
          + Add Course
        </Button>
      </a>
    </div>

    <div className="grid gap-[3%] grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 w-full">
      {courses.map((course) => (
        <CourseCard
          key={course.course_id}
          id={course.course_id}      
          title={course.title}
          date={course.creation_date}
          students={course.number_of_students}
        />

      ))}
    </div>
  </div>
</Header>

  )
}
