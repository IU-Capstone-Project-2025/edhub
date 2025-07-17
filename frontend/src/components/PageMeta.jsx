import { useEffect } from "react";

export default function PageMeta({ title, icon }) {
  useEffect(() => {
    if (!title) {
        document.title = "EdHub"
    }else{
        document.title = title
    }
    if (icon) {
      let link = document.querySelector("link[rel~='icon']")
      if (!link) {
        link = document.createElement("link")
        link.rel = "icon"
        document.head.appendChild(link)
      }
      link.href = icon
    }
  }, [title, icon])
}