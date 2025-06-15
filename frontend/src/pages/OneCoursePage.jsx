import { useEffect, useState } from "react"
import { useParams, Link } from "react-router-dom"
import Header from "@/components/Header"
import { Button } from "@/components/ui/button"
import axios from "axios"

export default function CoursePage() {
  const { id } = useParams()
  const [info, setInfo] = useState(null)
  const [materialCount, setMaterialCount] = useState(0)

  useEffect(() => {
    const token = localStorage.getItem("access_token")

    const fetchInfo = async () => {
      try {
        const res = await axios.get("/get_course_info", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id }
        })
        setInfo(res.data)
      } catch (err) {
        console.error("Failed to load course info:", err)
      }
    }

    const fetchMaterialCount = async () => {
      try {
        const res = await axios.get("/get_course_feed", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id }
        })
        setMaterialCount(res.data.length)
      } catch (err) {
        console.error("Failed to load materials:", err)
      }
    }

    fetchInfo()
    fetchMaterialCount()
  }, [id])

  if (!info) return <Header><p>Loading...</p></Header>

  return (
    <Header>
<div className="w-full h-screen overflow-x-hidden overflow-y-auto pt-6 px-8 flex flex-col gap-10">
        <div>
          <h1 className="text-4xl font-bold text-[#333940]">{info.title}</h1>
          <p className="text-sm text-gray-500">Course ID: {id}</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 w-full">
  <InfoCard
    title="Materials"
    description={`${materialCount} total`}
    link={`/courses/${id}/add-material`}
  />
  <InfoCard
    title="Students"
    description={`${info.number_of_students} enrolled`}
    link={`/courses/${id}/add-student`}
  />
  <InfoCard
    title="Parents"
    description="—"
    link={`/courses/${id}/add-parent`}
  />
</div>

      </div>
    </Header>
  )
}

function InfoCard({ title, description, link }) {
  return (
    <div className="flex-1 min-w-[200px] max-w-[300px] bg-white p-4 rounded-lg border shadow-sm flex flex-col justify-between">
      <div>
        <h2 className="text-md font-semibold text-[#333940]">{title}</h2>
        <p className="text-gray-500 text-sm mt-1">{description}</p>
      </div>
      <Link to={link} className="mt-4 self-start">
        <Button className="h-8 px-3 text-sm bg-[#4CB050] hover:bg-[#3BBF12] text-white">
          + Add
        </Button>
      </Link>
    </div>
  )
}
