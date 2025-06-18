import { useEffect, useState } from "react"
import { Link, useLocation } from "react-router-dom"
import { cn } from "@/lib/utils"
import axios from "axios"

export default function Header({ children }) {
  const location = useLocation()
  const [courses, setCourses] = useState([])

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const token = localStorage.getItem("access_token")
        const res = await axios.get("/available_courses", {
          headers: { Authorization: `Bearer ${token}` },
        })

        const detailed = await Promise.all(
          res.data.map(async (course) => {
            const info = await axios.get("/get_course_info", {
              headers: { Authorization: `Bearer ${token}` },
              params: { course_id: course.course_id },
            })
            return {
              id: course.course_id,
              title: info.data.title,
            }
          })
        )

        setCourses(detailed)
      } catch (err) {
        console.error("Failed to load courses", err)
      }
    }

    fetchCourses()
  }, [])

  const crumbs = location.pathname
    .split("/")
    .filter(Boolean)
    .map((seg, idx, arr) => (
      <span key={idx} className={cn("text-sm", idx === arr.length - 1 ? "text-[#4CB050] font-medium" : "text-gray-500")}>
        {seg[0].toUpperCase() + seg.slice(1)}
        {idx < arr.length - 1 && <span className="mx-1 text-gray-400">/</span>}
      </span>
    ))

  return (
    <div className="min-h-screen flex bg-[#f9fafb]">
      <aside className="w-64 bg-white border-r border-gray-200 shadow-sm h-screen p-6">
        <h2 className="text-xl font-bold text-[#333940] mb-6">EdHub LMS</h2>
        <nav className="space-y-2 text-sm">
          <Link to="/courses" className={cn("block hover:text-[#4CB050]", location.pathname === "/courses" && "text-[#4CB050] font-semibold")}>
            Courses
          </Link>

          <div className="ml-4 space-y-1">
            {courses.map((course) => (
              <Link
                key={course.id}
                to={`/courses/${course.id}`}
                className={cn(
                  "block text-gray-600 hover:text-[#4CB050]",
                  location.pathname === `/courses/${course.id}` && "text-[#4CB050] font-medium"
                )}
              >
                {course.title}
              </Link>
            ))}
          </div>

          <Link to="/create-course" className="block hover:text-[#4CB050] text-gray-700 mt-4">
            + Create Course
          </Link>
        </nav>
      </aside>

<main className="flex-1 p-6 md:p-10 space-y-6 overflow-x-hidden">
        <div className="text-sm flex items-center space-x-1">{crumbs}</div>
        {children}
      </main>
    </div>
  )
}
