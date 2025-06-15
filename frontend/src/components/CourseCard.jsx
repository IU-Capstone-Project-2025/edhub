import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useNavigate } from "react-router-dom"

export default function CourseCard({ title, date, students, id }) {
  const navigate = useNavigate()

  return (
    <Card
      onClick={() => navigate(`/courses/${id}`)}
      className="cursor-pointer w-full max-w-sm shadow-md hover:shadow-xl transition duration-300 border border-[#E5E7EB]"
    >
      <CardHeader className="p-0">
        <img
          src="/placeholder_course.png"
          alt="Course image"
          className="h-40 w-full object-cover rounded-t-md"
          onError={(e) => {
            e.target.onerror = null
            e.target.src =
              "data:image/svg+xml;charset=UTF-8,<svg width='100%' height='100%' viewBox='0 0 300 120' xmlns='http://www.w3.org/2000/svg'><rect width='300' height='120' fill='%23f3f4f6'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='%239ca3af' font-size='20'>No image</text></svg>"
          }}
        />
      </CardHeader>
      <CardContent className="p-4">
        <CardTitle className="text-lg text-[#333940] font-semibold mb-1">{title}</CardTitle>
        <p className="text-sm text-gray-500">Created on: {date}</p>
        <Badge className="mt-3 bg-[#4CB050] text-white px-3 py-1 rounded-full text-sm w-fit">
          Students: {students}
        </Badge>
      </CardContent>
    </Card>
  )
}
