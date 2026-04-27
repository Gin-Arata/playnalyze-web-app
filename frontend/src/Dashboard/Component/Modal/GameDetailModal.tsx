import type { GameData } from '../../../types/game';
import ButtonToMarketplace from '../Button/ButtonToMarketplace';

const GameDetailModal = ({ data }: { data: GameData | null }) => {
    console.log(data)
	return (
		<>
			<div
				className="modal modal-lg fade"
				id="gameDetailModal"
				tabIndex={-1}
				aria-labelledby="exampleModalLabel"
				aria-hidden="true"
			>
				<div className="modal-dialog">
					<div className="modal-content">
						<div className="modal-header">
							<h1
								className="modal-title fs-5"
								id="exampleModalLabel"
							>
								Game Detail
							</h1>
							<button
								type="button"
								className="btn-close"
								data-bs-dismiss="modal"
								aria-label="Close"
							></button>
						</div>
						<div className="modal-body">
                            <div className="row">
                                {/* Game Information Content */}
                                <div className="col-3">
                                    <img className="img-fluid rounded text-center" src={data?.img_url} alt={data?.name} />
                                </div>
                                <div className="col-9">
                                    <div className="row">
                                        <div className="col-8 fw-bold">{data?.name}</div>
                                        <div className="col-4"><ButtonToMarketplace gameUrl={data?.game_url} type={data?.from_platform} /></div>
                                        <div className="col-12 mt-2">{data?.description?.slice(0, 400)}...<a href={data?.game_url} className='text-decoration-none' target="_blank" rel="noopener noreferrer">Readmore</a></div>
                                    </div>
                                </div>

                                {/* Summary and Recommendation Content */}
                                <div className="col-12 mt-2">
                                    <p className="fw-bold p-0 m-0">Recommendation: {data?.recommendation_percent}%</p>
                                </div>
                                <div className="col-12 mt-2">
                                    <p className="fw-bold p-0 m-0">Review Summary</p>
                                </div>
                                {/* Positive Review Summary Content */}
                                <div className="col-12 mt-2">
                                    <p className="fw-bold p-0 m-0">Positive:</p>
                                </div>
                                <div className="col-12 mt-1">
                                    <div className="card">
                                        <div className="card-body">
                                            <p className="p-0 m-0">{data?.summary_positive}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Negative Review Summary Content */}
                                <div className="col-12 mt-2">
                                    <p className="fw-bold p-0 m-0">Negative:</p>
                                </div>
                                <div className="col-12 mt-1">
                                    <div className="card">
                                        <div className="card-body">
                                            <p className="p-0 m-0">{data?.summary_negative}</p>
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

export default GameDetailModal;
