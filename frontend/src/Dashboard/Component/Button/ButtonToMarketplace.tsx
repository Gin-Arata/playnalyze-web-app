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
					className="rounded float-end"
					src="icons/itchio-icon.jpg"
					alt="itch.io"
                    width={40}
				/>
			</a>
		);
	} else if (type === 2) {
		return (
			<a href={gameUrl} target="_blank" rel="noopener noreferrer">
				<img
					className="rounded float-end"
					src="icons/playstore-icon.jpg"
					alt="Play Store"
                    width={40}
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
