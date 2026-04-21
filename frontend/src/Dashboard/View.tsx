import React from 'react';
import type { GameDataResponse } from '../types/game';
import './index.css';

const View = ({
	submitGameSearch,
	data,
	isLoading,
	searchText,
}: {
	submitGameSearch: (e: React.FormEvent<HTMLFormElement>) => void;
	data: GameDataResponse;
	isLoading: boolean;
	searchText?: string;
}) => {
	return (
		<div className="d-flex flex-column min-vh-100">
			<div className="navbar" style={{ backgroundColor: '#60A5FA' }}>
				<div className="container-fluid d-flex justify-content-between align-items-center">
					<a
						className="navbar-brand d-flex gap-2 align-items-center text-white"
						style={{ cursor: 'pointer' }}
						onClick={() => (window.location.href = '/')}
					>
						<img src="/public/favicon.svg" alt="" width={20} />
						Playnalyze
					</a>

					<button className="btn btn-outline-light">
						<i className="fa fa-question me-1"></i>
						FAQ
					</button>
				</div>
			</div>

			{/* Game Search Section */}
			{!data && !isLoading && (
				<div className="container flex-grow-1 d-flex flex-column align-items-center justify-content-center">
					<div className="d-flex flex-column align-items-center gap-2">
						<h1>Welcome to Playnalyze!</h1>
						<p>Get started by entering a URL or Game Name below.</p>
					</div>

					<div className="position-relative w-100">
						<form onSubmit={(e) => submitGameSearch(e)}>
							<input
								type="search"
								name="search"
								className="form-control pe-5"
								placeholder="Input your URL here"
							/>
							<i className="fa fa-search position-absolute end-0 top-50 translate-middle-y me-3 fs-6 text-muted" />
						</form>
					</div>
				</div>
			)}

			{/* Game Data Display Section */}
			{(data || isLoading) && (
				<>
					<div className="container flex-grow-1 d-flex flex-column align-items-center mt-3">
						<div className="position-relative w-100">
							<form onSubmit={(e) => submitGameSearch(e)}>
								<input
									type="search"
									name="search"
									className="form-control pe-5"
									placeholder="Input your URL here"
									defaultValue={searchText}
								/>
							</form>
							<i className="fa fa-search position-absolute end-0 top-50 translate-middle-y me-3 fs-6 text-muted" />
						</div>

						{isLoading && (
							<>
								<div
									className="spinner-border text-primary mt-3"
									role="status"
								>
									<span className="visually-hidden">
										Loading...
									</span>
								</div>
								<p className="mt-2">Loading game data...</p>
							</>
						)}

						{!isLoading && data && (
							<>
								{Array.isArray(data) ? (
									<>
										<div className="w-100 mt-3">
											{data.map((game) => (
												<div
													key={game.game_id}
													className="card d-flex flex-row mb-3"
													style={{ height: '200px' }}
												>
													<img
														src="/public/icons.svg"
														className="card-img-left"
														alt={game.name}
														style={{
															width: '200px',
															height: '100%',
															objectFit: 'cover',
														}}
													/>
													<div className="card-body d-flex flex-column">
														<h5 className="card-title">
															{game.name}
														</h5>
														<p className="card-text text-muted">
															{game.description}
														</p>
														<p className="card-text">
															<strong>
																Recommendation:
															</strong>{' '}
															{
																game.recommendation_percent
															}
															%
														</p>
														<a
															href="#"
															className="btn btn-primary mt-auto"
															style={{
																width: 'fit-content',
															}}
														>
															View Details
														</a>
													</div>
												</div>
											))}
										</div>
									</>
								) : (
									<>
										<p className="mt-3">{data?.message}</p>
									</>
								)}
							</>
						)}
					</div>
				</>
			)}
		</div>
	);
};

export default View;
