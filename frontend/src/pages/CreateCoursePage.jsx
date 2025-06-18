import { useState } from "react"
import Header from "@/components/Header"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardTitle } from "@/components/ui/card"
import axios from "axios"
import { useNavigate } from "react-router-dom"

export default function CreateCoursePage() {
  const [title, setTitle] = useState("")
  const [department, setDepartment] = useState("")
  const [subject, setSubject] = useState("")
  const [auditorium, setAuditorium] = useState("")
  const navigate = useNavigate()

  const handleCreateCourse = async () => {
    try {
      const token = localStorage.getItem("access_token")
      const res = await axios({
        method: "post",
        url: `/create_course?title=${encodeURIComponent(title)}`,
        /* TODO:нужно добавить department, subject и auditorium в запрос*/
        headers: {
          Authorization: `Bearer ${token}`
        }
      })

      alert("Course created successfully!")
      navigate("/courses")
    } catch (err) {
      console.error(err)
      const msg = err.response?.data?.detail || err.message || "Unknown error"
      alert("Failed to create course: " + msg)
    }
  }

  return (
    <Header>
      <div className="min-h-screen flex items-center justify-center bg-[#f5f9ff]">
        <Card className="w-full max-w-md p-6 shadow-md">
          <CardTitle className="text-center mb-4 text-xl">Create Course</CardTitle>
          <CardContent className="space-y-4">
            <Input
              placeholder="Course title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            <Input
              placeholder="Department"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
            />
            <Input
              placeholder="Subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
            />
            <Input
              placeholder="Auditorium"
              value={auditorium}
              onChange={(e) => setAuditorium(e.target.value)}
            />
            <Button
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              onClick={handleCreateCourse}
            >
              Create Course
            </Button>
            <div className="text-right text-sm">
              <a href="/courses" className="text-blue-600 hover:underline">
                Back to courses
              </a>
            </div>
          </CardContent>
        </Card>
      </div>
    </Header>
  )
}
