import View from './View';
import { useState } from 'react';
import { useGameSearch } from '../hooks/useGameSearch';

const Index = () => {
	const [searchQuery, setSearchQuery] = useState<string | null>(null);
	const { data, isLoading } = useGameSearch(searchQuery);

	const submitGameSearch = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		const formData = new FormData(e.currentTarget);
		const searchQuery = formData.get('search') as string;
		setSearchQuery(searchQuery);
	};
    
	return (
		<View
			submitGameSearch={submitGameSearch}
			data={data}
			isLoading={isLoading}
		/>
	);
};

export default Index;
