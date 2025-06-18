import { useNavigate } from "react-router-dom"
import { useEffect, useState } from "react"
import { useParams, Link } from "react-router-dom"
import Header from "@/components/Header"
import { Button } from "@/components/ui/button"
import axios from "axios"

export default function AddMaterialPage() {
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

  function buttonOnClick(){
    alert("Action placeholder")
  }
  if (!info) return <Header><p>Loading...</p></Header>

  return (
    <Header>
        <div className="w-full h-screen overflow-x-hidden overflow-y-auto pt-6 px-8 flex flex-col gap-10">
        <div>
          <h1 className="text-4xl font-bold text-[#333940]">{info.title}</h1>
          <p className="text-sm text-gray-500">Course ID: {id}</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 w-full">
            Materials : {materialCount} total
        </div>
        <Button onClick={buttonOnClick} className="bg-[#4CB050] hover:bg-[#3BBF12] text-white text-md rounded-xl px-[5%] py-[2%] border-2 border-transparent hover:border-[#2E7D32] transition"> 
            Add material
        </Button> 

        </div>
    </Header>
  )
}
