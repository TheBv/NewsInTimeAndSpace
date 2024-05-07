import { useEffect, useState } from "react"
import { baseURL } from "../lib/constants"

interface Actor {
    Count: number
    Actor: string
    Type: string
    Location: {
        type: string
        coordinates: number[]
    }
}

export const useActors = () => {
    const [actors, setActors] = useState<Actor[]>([]);
    useEffect(() => {
        fetch(`${baseURL}/news/extra/actors`)
            .then(response => response.json())
            .then(data => setActors(data.results))
    }, [])

    return actors;
}