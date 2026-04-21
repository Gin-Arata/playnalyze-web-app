import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import type { GameDataResponse } from '../types/game'

export const useGameSearch = (query: string | null) => {
    return useQuery({
        queryKey: ['games', query],
        queryFn: async () => {
            if (!query) return null
            const res = await axios.get(
                `${import.meta.env.VITE_API_URL}/games/search?link=${query}`
            )
            return res.data as GameDataResponse
        },
        enabled: !!query, // Hanya jalan ketika query ada
    })
}