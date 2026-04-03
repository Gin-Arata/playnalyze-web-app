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

				<div className="container flex-grow-1 d-flex flex-column align-items-center mt-3">
					<div className="position-relative w-100">
						<input
							type="search"
							className="form-control pe-5"
							placeholder="Input your URL here"
						/>
						<i className="fa fa-search position-absolute end-0 top-50 translate-middle-y me-3 fs-6 text-muted" />
					</div>

					<div className="d-flex flex-wrap justify-content-center gap-3 mt-3">
						<div className="card" style={{ width: '18rem' }}>
							<img src="/public/icons.svg" className="card-img-top" alt="..."/>
							<div className="card-body">
								<h5 className="card-title">Card title</h5>
								<p className="card-text">Some quick example text to build on the card title and make up the bulk of the card’s content.</p>
								<a href="#" className="btn btn-primary">Go somewhere</a>
							</div>
						</div>
						<div className="card" style={{ width: '18rem' }}>
							<img src="/public/icons.svg" className="card-img-top" alt="..."/>
							<div className="card-body">
								<h5 className="card-title">Card title</h5>
								<p className="card-text">Some quick example text to build on the card title and make up the bulk of the card’s content.</p>
								<a href="#" className="btn btn-primary">Go somewhere</a>
							</div>
						</div>
						<div className="card" style={{ width: '18rem' }}>
							<img src="/public/icons.svg" className="card-img-top" alt="..."/>
							<div className="card-body">
								<h5 className="card-title">Card title</h5>
								<p className="card-text">Some quick example text to build on the card title and make up the bulk of the card’s content.</p>
								<a href="#" className="btn btn-primary">Go somewhere</a>
							</div>
						</div>
						<div className="card" style={{ width: '18rem' }}>
							<img src="/public/icons.svg" className="card-img-top" alt="..."/>
							<div className="card-body">
								<h5 className="card-title">Card title</h5>
								<p className="card-text">Some quick example text to build on the card title and make up the bulk of the card’s content.</p>
								<a href="#" className="btn btn-primary">Go somewhere</a>
							</div>
						</div>
						<div className="card" style={{ width: '18rem' }}>
							<img src="/public/icons.svg" className="card-img-top" alt="..."/>
							<div className="card-body">
								<h5 className="card-title">Card title</h5>
								<p className="card-text">Some quick example text to build on the card title and make up the bulk of the card’s content.</p>
								<a href="#" className="btn btn-primary">Go somewhere</a>
							</div>
						</div>
						<div className="card" style={{ width: '18rem' }}>
							<img src="/public/icons.svg" className="card-img-top" alt="..."/>
							<div className="card-body">
								<h5 className="card-title">Card title</h5>
								<p className="card-text">Some quick example text to build on the card title and make up the bulk of the card’s content.</p>
								<a href="#" className="btn btn-primary">Go somewhere</a>
							</div>
						</div>
					</div>
				</div>
			</div>
		</>
	);
};

export default View;
