const FAQModal = () => {
	return (
		<>
			<div
				className="modal modal-lg fade"
				id="faqModal"
				tabIndex={-1}
				aria-labelledby="faqModalLabel"
				aria-hidden="true"
			>
				<div className="modal-dialog">
					<div className="modal-content">
						<div className="modal-header">
							<h1 className="modal-title fs-5" id="faqModalLabel">
								FAQ
							</h1>
							<button
								type="button"
								className="btn-close"
								data-bs-dismiss="modal"
								aria-label="Close"
							></button>
						</div>
						<div className="modal-body">
							<div
								className="accordion"
								id="accordionPanelsStayOpenExample"
							>
								<div className="accordion-item">
									<h2 className="accordion-header">
										<button
											className="accordion-button"
											type="button"
											data-bs-toggle="collapse"
											data-bs-target="#panelsStayOpen-collapseOne"
											aria-expanded="true"
											aria-controls="panelsStayOpen-collapseOne"
										>
											How to Use?
										</button>
									</h2>
									<div
										id="panelsStayOpen-collapseOne"
										className="accordion-collapse collapse show"
									>
										<div className="accordion-body">
											Put your <strong>Game URL</strong> or <strong>Game Name</strong> in the search bar, then press enter to get the analysis result. You can also click on the game card to see more details about the game likes descriptions of game, summary reviews positive and negative from users. <br />
                                            example of game url: <br/>
                                            Steam: <em>https://store.steampowered.com/app/1091500/Resident_Evil_3/</em> or <em>Resident Evil 3</em>
                                            <br />
                                            Play Stores: <em>https://play.google.com/store/apps/details?id=com.netease.stzb.gb</em> or <em>Identity V</em>
                                            <br />
                                            itch.io: <em>https://suzukaze.itch.io/kaiju-kitchen</em> or <em>Kaiju Kitchen</em>
										</div>
									</div>
								</div>
								<div className="accordion-item">
									<h2 className="accordion-header">
										<button
											className="accordion-button collapsed"
											type="button"
											data-bs-toggle="collapse"
											data-bs-target="#panelsStayOpen-collapseTwo"
											aria-expanded="false"
											aria-controls="panelsStayOpen-collapseTwo"
										>
											How does it work?
										</button>
									</h2>
									<div
										id="panelsStayOpen-collapseTwo"
										className="accordion-collapse collapse"
									>
										<div className="accordion-body">
											First, we will fetch the game data from the API based on the search query. Then, we will display the game data in the card format. When the user clicks on the game card, we will fetch the game detail data from the API and display it in the modal. The game detail data includes the game information, summary reviews, and recommendation percentage.
										</div>
									</div>
								</div>
								<div className="accordion-item">
									<h2 className="accordion-header">
										<button
											className="accordion-button collapsed"
											type="button"
											data-bs-toggle="collapse"
											data-bs-target="#panelsStayOpen-collapseThree"
											aria-expanded="false"
											aria-controls="panelsStayOpen-collapseThree"
										>
											Where do you get the data?
										</button>
									</h2>
									<div
										id="panelsStayOpen-collapseThree"
										className="accordion-collapse collapse"
									>
										<div className="accordion-body">
											We get the data from the API that we have built. The API will fetch the data from the web and process it with algorithms to get the recommendation percentage and summary reviews. The data is fetched from various sources such as Steam, Play Store, and itch.io.
										</div>
									</div>
								</div>
                                <div className="accordion-item">
									<h2 className="accordion-header">
										<button
											className="accordion-button collapsed"
											type="button"
											data-bs-toggle="collapse"
											data-bs-target="#panelsStayOpen-collapseFour"
											aria-expanded="false"
											aria-controls="panelsStayOpen-collapseFour"
										>
											What if the game is not found?
										</button>
									</h2>
									<div
										id="panelsStayOpen-collapseFour"
										className="accordion-collapse collapse"
									>
										<div className="accordion-body">
											If the game is not found, we will display a message indicating that the game could not be found. You can try searching for a different game or check the spelling of the game name or URL of the game.
										</div>
									</div>
								</div>
                                <div className="accordion-item">
									<h2 className="accordion-header">
										<button
											className="accordion-button collapsed"
											type="button"
											data-bs-toggle="collapse"
											data-bs-target="#panelsStayOpen-collapseFive"
											aria-expanded="false"
											aria-controls="panelsStayOpen-collapseFive"
										>
											What game stores do you support?
										</button>
									</h2>
									<div
										id="panelsStayOpen-collapseFive"
										className="accordion-collapse collapse"
									>
										<div className="accordion-body">
											We support games from various stores including <strong>Steam</strong>, <strong>Play Store</strong>, and <strong>itch.io</strong>.
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</>
	);
};

export default FAQModal;
