import { baseURL } from "./constants";

export interface QueryParams {
    actor: string[],
    type: string[],
    ToneMax: number,
    ToneMin: number,
    GoldsteinScaleHigh: number,
    GoldsteinScaleLow: number,
    startTime: string,
    endTime: string,
    radius: number,
    latitude: number,
    longitude: number,
}

export interface APIGroupResponse {
    Group_ID: number,
    Count: number,
    City: string,
    Region: string,
    Country: string,
    Country_Code: string,
    Location: {
        type: string,
        coordinates: [number, number]
    },
    Events: {
        GLOBALEVENTID: string
    }[]
}

export const createSearchParams = (params: Partial<QueryParams>) => {
    const searchParams = new URLSearchParams()
    if (params.GoldsteinScaleHigh) searchParams.set('GoldsteinScaleHigh', params.GoldsteinScaleHigh.toString())
    if (params.GoldsteinScaleLow) searchParams.set('GoldsteinScaleLow', params.GoldsteinScaleLow.toString())
    if (params.ToneMax) searchParams.set('ToneMax', params.ToneMax.toString())
    if (params.ToneMin) searchParams.set('ToneMin', params.ToneMin.toString())
    if (params.startTime) searchParams.set('startTime', params.startTime)
    if (params.endTime) searchParams.set('endTime', params.endTime)
    if (params.radius) searchParams.set('radius', params.radius.toString())
    if (params.latitude) searchParams.set('latitude', params.latitude.toString())
    if (params.longitude) searchParams.set('longitude', params.longitude.toString())
    if (params.actor && params.actor.length != 0) {
        for (const actor of params.actor) searchParams.append('actor', actor)
    }
    if (params.type && params.type.length != 0) {
        for (const type of params.type) searchParams.append('type', type)
    }
    return searchParams
}

export const getCountries = async (params: Partial<QueryParams>): Promise<APIGroupResponse[]> => {
    const searchParams = createSearchParams(params)
    const response = await fetch(`${baseURL}/news/groups/country/ids?${searchParams}`)
    return (await response.json()).results
}

export const getRegions = async (params: Partial<QueryParams>): Promise<APIGroupResponse[]> => {
    const searchParams = createSearchParams(params)
    const response = await fetch(`${baseURL}/news/groups/region/ids?${searchParams}`)
    return (await response.json()).results
}

export const getCities = async (params: Partial<QueryParams>): Promise<APIGroupResponse[]> => {
    const searchParams = createSearchParams(params)
    const response = await fetch(`${baseURL}/news/groups/city/ids?${searchParams}`)
    return (await response.json()).results
}

export interface APIEvent {
    GLOBALEVENTID: string,
    Location_Name: string,
    Country_Code: string,
    Location: {
        type: string,
        coordinates: [number, number]
    },
    Actors: {
        Name: string,
        Type: string,
        Location: {
            type: string,
            coordinates: [number, number]
        }
    }[],
    Source: string,
    IsRootEvent: string,
    GoldsteinScale: number,
    AvgTone: number,
    NumMentions: string,
    Date: string,
    Type: string,
    Counts: string,
    Media: {
        type: string,
        content: string
    },
    Title: string
}

export const getEvents = async (ids: string[]): Promise<APIEvent[]> => {
    const response = await fetch(`${baseURL}/news/events/multiple?id=${ids.join('&id=')}`)
    return (await response.json()).results
}