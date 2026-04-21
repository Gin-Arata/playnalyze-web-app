import { Link } from 'react-router';

const View = () => {
	return (
		<>
			<div className="d-flex flex-column min-vh-100">
				<div className="navbar bg-body-tertiary">
					<div className="container-fluid d-flex justify-content-between align-items-center">
						<Link
							to="/"
							className="navbar-brand d-flex gap-2 align-items-center"
						>
							<img src="/public/favicon.svg" alt="" width={20} />
							Playnalyze
						</Link>

						<button className="btn btn-outline-primary">
							<i className="fa fa-question me-1"></i>
							FAQ
						</button>
					</div>
				</div>

				
			</div>
		</>
	);
};

export default View;
