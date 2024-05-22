import { useEffect, useState } from "react"
import { baseURL } from "../lib/constants"

export interface Type {
    Count: number
    Type: string
    Type_Name: string
    BaseType: string
    BaseType_Name: string
}

export const useTypes = () => {
    const [actors, setActors] = useState<Type[]>([]);
    useEffect(() => {
        fetch(`${baseURL}/news/extra/types?startTime=2024-04-08&endTime=2024-05-08`)
            .then(response => response.json())
            .then(data => setActors(data.results))
    }, [])

    return actors;
}