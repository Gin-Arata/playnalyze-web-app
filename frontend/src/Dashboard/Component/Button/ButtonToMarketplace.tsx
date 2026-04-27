const ButtonToMarketplace = ({
	gameUrl,
	type,
}: {
	gameUrl: string | undefined;
	type: number | undefined;
}) => {
	if (type === 1) {
		return (
			<a href={gameUrl} target="_blank" rel="noopener noreferrer">
				<img
					className="rounded"
					src="icons/steam-icon.jpg"
					alt="Steam"
                    width={20}
				/>
			</a>
		);
	} else if (type === 2) {
		return (
			<a href={gameUrl} target="_blank" rel="noopener noreferrer">
				<img
					className="rounded"
					src="icons/steam-icon.jpg"
					alt="Steam"
                    width={20}
				/>
			</a>
		);
	} else if (type === 3) {
		return (
			<>
				<a href={gameUrl} target="_blank" rel="noopener noreferrer">
					<img
						className="rounded float-end"
						src="icons/steam-icon.jpg"
						alt="Steam"
                        width={40}
					/>
				</a>
			</>
		);
	}
};

export default ButtonToMarketplace;
