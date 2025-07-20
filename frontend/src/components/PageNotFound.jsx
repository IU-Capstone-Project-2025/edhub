import React, {useEffect, useState, useRef} from "react"
import "../styles/PageNotFound.css"
import {useParams, useNavigate} from "react-router-dom"
import axios from "axios"
import AddGrade from "../components/AddGrade"
import PageMeta from "../components/PageMeta"

export default function PageNotFound() {
    return (
        <div className="body">
            <PageMeta title="Page Not Found" />
            <h1>404 - Page Not Found</h1>
            <p>Sorry, the page you are looking for does not exist.</p>
            <p>You can go back to the <a href="/courses">Courses Page</a> or return to the <a href="/">Home Page</a>.</p>
        </div>
    )
}
