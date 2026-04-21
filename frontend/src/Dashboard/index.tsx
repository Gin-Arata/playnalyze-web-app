import axios from 'axios';
import View from './View';
import { useState } from 'react';
import type { GameDataResponse } from '../types/game';

const Index = () => {
    const [ data, setData ] = useState<GameDataResponse>(null);

	const submitGameSearch = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		const formData = new FormData(e.currentTarget);

        try {
            const query = formData.get('search') as string;
            const res = await axios.get(`${import.meta.env.VITE_API_URL}/games/search?link=${query}`);

            console.log('Game data response:', res);
            
            setData(res.data);
        } catch (error) {
            console.error('Error fetching game data:', error);
        }
	};

	return <View submitGameSearch={submitGameSearch} data={data} />;
};

export default Index;
