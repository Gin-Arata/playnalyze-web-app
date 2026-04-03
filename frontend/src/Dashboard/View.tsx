import './index.css';

const View = () => {
	return (
		<div className="d-flex flex-column min-vh-100">
			<div className="navbar bg-body-tertiary">
				<div className="container-fluid d-flex justify-content-between align-items-center">
					<a
						href="#"
						className="navbar-brand d-flex gap-2 align-items-center"
					>
						<img src="/public/favicon.svg" alt="" width={20} />
						Playnalyze
					</a>

					<button className="btn btn-outline-primary">
						<i className="fa fa-question me-1"></i>
						FAQ
					</button>
				</div>
			</div>

			<div className="container flex-grow-1 d-flex flex-column align-items-center justify-content-center">
				<div className="d-flex flex-column align-items-center gap-2">
					<h1>Playnalyze</h1>
					<p>blablablebleblublublubalablbabalab</p>
				</div>

                <div className="position-relative w-100">
                    <input
                        type="search"
                        className="form-control pe-5"
                        placeholder="Input your URL here"
                    />
                    <i className="fa fa-search position-absolute end-0 top-50 translate-middle-y me-3 fs-6 text-muted" />
                </div>
			</div>
		</div>
	);
};

export default View;
